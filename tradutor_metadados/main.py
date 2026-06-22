# -*- coding: utf-8 -*-

import re
import json
import urllib.request
import urllib.parse
import urllib.error

from PyQt5.Qt import QThread, pyqtSignal
from PyQt5.Qt import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout

from calibre.gui2.actions import InterfaceAction
from calibre.gui2 import error_dialog, info_dialog


class TraducaoWorker(QThread):
    """
    Roda a tradução em uma thread separada para não congelar a interface
    do Calibre enquanto espera a resposta da rede.

    Traduz a sinopse (sempre aplicada automaticamente) e o título (aplicado
    apenas depois de confirmação manual do usuário, feita na thread principal).
    """

    # Sinais para comunicar o resultado de volta pra thread principal
    # book_id, sinopse_traduzida, titulo_original, titulo_traduzido
    sucesso = pyqtSignal(int, str, str, str)
    falha   = pyqtSignal(int, str)       # book_id, mensagem_de_erro

    def __init__(self, book_id, sinopse_original, titulo_original):
        super().__init__()
        self.book_id = book_id
        self.sinopse_original = sinopse_original
        self.titulo_original = titulo_original

    def run(self):
        try:
            sinopse_traduzida = self.chamar_api_traducao(self.sinopse_original, eh_html=True)

            titulo_traduzido = self.titulo_original
            if self.titulo_original:
                titulo_traduzido = self.chamar_api_traducao(self.titulo_original, eh_html=False)

            self.sucesso.emit(self.book_id, sinopse_traduzida, self.titulo_original, titulo_traduzido)
        except urllib.error.URLError as e:
            self.falha.emit(self.book_id, f'Falha de conexão com o servidor de tradução:\n{e}')
        except (json.JSONDecodeError, IndexError, KeyError) as e:
            self.falha.emit(self.book_id, f'Resposta inesperada do serviço de tradução:\n{e}')
        except Exception as e:
            self.falha.emit(self.book_id, f'Erro inesperado:\n{e}')

    def chamar_api_traducao(self, texto, eh_html):
        if eh_html:
            # Remove as tags HTML provisoriamente para o Google traduzir melhor.
            # OBS: isso colapsa parágrafos múltiplos em um texto só (ver nota
            # no main.py / README sobre essa limitação).
            texto_limpo = re.sub(r'<[^>]+>', '', texto).strip()
        else:
            texto_limpo = texto.strip()

        if not texto_limpo:
            raise ValueError('Texto ficou vazio após limpeza.')

        url = (
            "https://translate.googleapis.com/translate_a/single"
            "?client=gtx&sl=en&tl=pt&dt=t&q=" + urllib.parse.quote(texto_limpo)
        )

        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )

        # Timeout explícito: sem isso, uma rede travada deixa a thread
        # (e potencialmente o fechamento do Calibre) pendurada.
        resposta = urllib.request.urlopen(req, timeout=15).read()

        dados = json.loads(resposta)

        # O Google retorna o texto quebrado em várias frases; juntamos tudo.
        texto_traduzido = "".join(frase[0] for frase in dados[0] if frase[0])

        if eh_html:
            return f"<p>{texto_traduzido}</p>"
        return texto_traduzido


class DialogoConfirmarTitulo(QDialog):
    """
    Diálogo simples que mostra o título original e a tradução sugerida,
    permitindo ao usuário: aceitar a tradução, editá-la antes de aceitar,
    ou manter o título original (pular).
    """

    def __init__(self, parent, titulo_original, titulo_traduzido):
        super().__init__(parent)
        self.setWindowTitle('Confirmar tradução do título')
        self.resultado = None  # vai virar o texto final, ou None se "manter original"

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(f'<b>Título original:</b> {titulo_original}'))
        layout.addWidget(QLabel('<b>Título traduzido (edite se quiser):</b>'))

        self.campo_texto = QLineEdit(titulo_traduzido)
        layout.addWidget(self.campo_texto)

        botoes = QHBoxLayout()

        btn_manter = QPushButton('Manter original')
        btn_manter.clicked.connect(self._manter_original)
        botoes.addWidget(btn_manter)

        btn_aceitar = QPushButton('Usar tradução')
        btn_aceitar.setDefault(True)
        btn_aceitar.clicked.connect(self._aceitar)
        botoes.addWidget(btn_aceitar)

        layout.addLayout(botoes)
        self.setMinimumWidth(420)

    def _manter_original(self):
        self.resultado = None
        self.accept()

    def _aceitar(self):
        self.resultado = self.campo_texto.text().strip()
        self.accept()


class TradutorBotao(InterfaceAction):

    name = 'Tradutor de Metadados'
    # O segundo elemento fica None propositalmente: o Calibre NÃO resolve
    # o ícone sozinho a partir do nome do arquivo aqui. O ícone precisa ser
    # carregado manualmente em genesis() via get_icons() (ver abaixo).
    action_spec = (
        'Traduzir Metadados',
        None,
        'Traduzir sinopse, título e idioma do(s) livro(s) selecionado(s) para PT-BR',
        'Ctrl+T'
    )

    def genesis(self):
        # Carrega o icon.png de dentro do zip do plugin e aplica no qaction.
        # get_icons() é uma função builtin injetada pelo Calibre no namespace
        # do plugin (não precisa de import); ela lê o recurso do próprio
        # arquivo .zip instalado.
        icon = get_icons('icon.png', 'Tradutor de Metadados')
        self.qaction.setIcon(icon)

        self.qaction.triggered.connect(self.traduzir_livros)
        # Mantém referência às threads ativas para elas não serem
        # coletadas pelo garbage collector antes de terminarem.
        self._threads_ativas = []
        # Controla quantos livros ainda faltam terminar, para o diálogo
        # de sucesso/erro só aparecer no final do lote.
        self._pendentes = 0
        self._erros = []

    def traduzir_livros(self):
        linhas_selecionadas = self.gui.library_view.selectionModel().selectedRows()

        if not linhas_selecionadas:
            error_dialog(
                self.gui, 'Nenhum livro selecionado',
                'Por favor, selecione uma HQ ou livro na lista.', show=True
            )
            return

        db = self.gui.library_view.model().db
        model = self.gui.library_view.model()

        # Resolve os IDs reais dos livros via o modelo da view (e não
        # db.id(row) direto, que espera índice do db, não da view ordenada/filtrada).
        book_ids = [model.id(linha) for linha in linhas_selecionadas]

        livros_sem_sinopse = []
        self._pendentes = 0
        self._erros = []
        self._fila_confirmacao_titulo = []

        for book_id in book_ids:
            sinopse_original = db.comments(book_id, index_is_id=True)

            if not sinopse_original:
                titulo = db.title(book_id, index_is_id=True)
                livros_sem_sinopse.append(titulo)
                continue

            titulo_original = db.title(book_id, index_is_id=True)

            self._pendentes += 1
            worker = TraducaoWorker(book_id, sinopse_original, titulo_original)
            worker.sucesso.connect(self._ao_terminar_com_sucesso)
            worker.falha.connect(self._ao_terminar_com_falha)
            worker.finished.connect(lambda w=worker: self._threads_ativas.remove(w))
            self._threads_ativas.append(worker)
            worker.start()

        if livros_sem_sinopse:
            error_dialog(
                self.gui, 'Sinopse Vazia',
                'O(s) seguinte(s) livro(s) não possui(em) sinopse para traduzir:\n- '
                + '\n- '.join(livros_sem_sinopse),
                show=True
            )

        if self._pendentes == 0 and not livros_sem_sinopse:
            # Não deveria acontecer, mas por segurança.
            info_dialog(self.gui, 'Nada a fazer', 'Nenhuma sinopse para traduzir.', show=True)

    def _ao_terminar_com_sucesso(self, book_id, sinopse_traduzida, titulo_original, titulo_traduzido):
        db = self.gui.library_view.model().db

        # Sinopse: aplicada direto, sem confirmação (baixo risco).
        db.set_comment(book_id, sinopse_traduzida)

        # Idioma: forçamos para português, já que toda sinopse traduzida
        # aqui implica que o livro é tratado como PT-BR na sua biblioteca.
        db.set_languages(book_id, ['por'])

        # Atualiza a UI para refletir o novo texto/idioma no(s) livro(s) afetado(s).
        self.gui.library_view.model().refresh_ids([book_id])

        # Título: maior risco (nomes oficiais de obras nem sempre são tradução
        # literal), então só aplicamos depois de confirmação manual.
        # Enfileira para mostrar os diálogos um por vez, depois que todas as
        # traduções pendentes (sinopse) já tiverem sido aplicadas.
        if titulo_traduzido and titulo_traduzido != titulo_original:
            self._fila_confirmacao_titulo.append((book_id, titulo_original, titulo_traduzido))

        self._pendentes -= 1
        self._finalizar_se_concluido()

    def _ao_terminar_com_falha(self, book_id, mensagem_erro):
        db = self.gui.library_view.model().db
        titulo = db.title(book_id, index_is_id=True) or f'ID {book_id}'
        self._erros.append(f'{titulo}: {mensagem_erro}')

        self._pendentes -= 1
        self._finalizar_se_concluido()

    def _finalizar_se_concluido(self):
        if self._pendentes > 0:
            return  # ainda há traduções em andamento

        # Processa a fila de confirmação de títulos, um diálogo por vez,
        # ANTES de mostrar o resumo final de sucesso/erro.
        self._processar_proxima_confirmacao_titulo()

    def _processar_proxima_confirmacao_titulo(self):
        if not self._fila_confirmacao_titulo:
            self._mostrar_resumo_final()
            return

        book_id, titulo_original, titulo_traduzido = self._fila_confirmacao_titulo.pop(0)

        dialogo = DialogoConfirmarTitulo(self.gui, titulo_original, titulo_traduzido)
        dialogo.exec_()

        if dialogo.resultado:  # None significa "manter original"
            db = self.gui.library_view.model().db
            db.set_title(book_id, dialogo.resultado)
            self.gui.library_view.model().refresh_ids([book_id])

        # Continua para o próximo título pendente na fila (se houver).
        self._processar_proxima_confirmacao_titulo()

    def _mostrar_resumo_final(self):
        if self._erros:
            error_dialog(
                self.gui, 'Erro na Tradução',
                'Ocorreram erros ao traduzir:\n\n' + '\n\n'.join(self._erros),
                show=True
            )
        else:
            info_dialog(self.gui, 'Sucesso', 'Metadados traduzidos com sucesso!', show=True)