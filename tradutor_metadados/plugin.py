# -*- coding: utf-8 -*-
"""
Plugin principal para Calibre: Tradutor de Metadados.

Orquestra a tradução de múltiplos livros com threading e gerenciamento de fila.
"""

from typing import List, Optional, Tuple

from PyQt5.Qt import QThread
from calibre.gui2 import error_dialog, info_dialog
from calibre.gui2.actions import InterfaceAction

from .application.presenter import TranslationPresenter
from .application.worker import TranslationWorker
from .core.entities import Book, TranslationErrorResult
from .core.exceptions import EmptySynopsisError
from .core.translator_service import TranslatorService
from .infrastructure.calibre_db import CalibreDatabase
from .infrastructure.google_translate_api import GoogleTranslateAPI
from .infrastructure.http_client import HttpClient
from .presentation.dialogs import ConfirmTitleDialog


class TradutorBotao(InterfaceAction):
    """Plugin de tradução de metadados para Calibre.

    Responsável por:
    - Interface com Calibre (InterfaceAction)
    - Coordenação de threads de tradução
    - Gerenciamento de fila de confirmação de títulos
    - Apresentação de resultados finais

    Todas as dependências são injetadas no genesis().
    """

    name = "Tradutor de Metadados"
    action_spec = (
        "Traduzir Metadados",
        None,
        "Traduzir sinopse, título e idioma do(s) livro(s) selecionado(s) para PT-BR",
        "Ctrl+T",
    )

    def genesis(self):
        """Inicializa plugin com dependências injetadas.

        Chamado uma única vez quando o plugin é carregado.
        """
        # Setup de dependências (injeção)
        self.http_client = HttpClient(timeout=15)
        self.translation_api = GoogleTranslateAPI(self.http_client)
        self.translator_service = TranslatorService(self.translation_api)
        self.presenter = TranslationPresenter()

        # Carregar ícone e conectar sinal
        icon = get_icons("icon.png", "Tradutor de Metadados")
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.on_translate_books)

        # Estado para gerenciar tradução
        self._active_threads: List[QThread] = []
        self._pending_count = 0
        self._errors: List[TranslationErrorResult] = []
        self._title_confirmations: List[Tuple[int, str, str]] = []

    def on_translate_books(self):
        """Acionado quando usuário clica no botão 'Traduzir Metadados'."""
        # Obter linhas selecionadas
        selected_rows = self.gui.library_view.selectionModel().selectedRows()

        if not selected_rows:
            error_dialog(
                self.gui,
                "Nenhum livro selecionado",
                "Por favor, selecione uma HQ ou livro na lista.",
                show=True,
            )
            return

        # Obter IDs dos livros
        db = self.gui.library_view.model().db
        model = self.gui.library_view.model()
        book_ids = [model.id(row) for row in selected_rows]

        # Resetar estado
        self._active_threads = []
        self._pending_count = 0
        self._errors = []
        self._title_confirmations = []

        # Carregar livros e iniciar tradução
        calibre_db = CalibreDatabase(db)
        books_without_synopsis = []

        for book_id in book_ids:
            book = calibre_db.get_book(book_id)

            if not book.has_synopsis():
                books_without_synopsis.append(book.title)
                continue

            # Criar e iniciar worker
            self._pending_count += 1
            worker = TranslationWorker(self.translator_service, book)
            worker.success.connect(self._on_translation_success)
            worker.failure.connect(self._on_translation_failure)
            worker.finished.connect(lambda w=worker: self._active_threads.remove(w))
            self._active_threads.append(worker)
            worker.start()

        # Mostrar aviso se alguns livros não têm sinopse
        if books_without_synopsis:
            titles_str = self.presenter.format_books_without_synopsis(
                books_without_synopsis
            )
            error_dialog(
                self.gui,
                "Sinopse Vazia",
                f"O(s) seguinte(s) livro(s) não possui(em) sinopse para traduzir:{titles_str}",
                show=True,
            )

        # Se nenhum livro para traduzir, mostrar mensagem
        if self._pending_count == 0 and not books_without_synopsis:
            info_dialog(
                self.gui,
                "Nada a fazer",
                "Nenhuma sinopse para traduzir.",
                show=True,
            )

    def _on_translation_success(
        self, book_id: int, synopsis: str, orig_title: str, trans_title: str
    ):
        """Chamado quando tradução termina com sucesso."""
        db = self.gui.library_view.model().db
        model = self.gui.library_view.model()
        calibre_db = CalibreDatabase(db)

        # Atualizar sinopse (sempre)
        calibre_db.update_synopsis(book_id, synopsis)

        # Atualizar idioma para português
        calibre_db.update_language(book_id, "por")

        # Atualizar view
        calibre_db.refresh_view([book_id], model)

        # Enfileirar confirmação de título (se houver)
        if trans_title and trans_title != orig_title:
            self._title_confirmations.append((book_id, orig_title, trans_title))

        self._pending_count -= 1
        self._finalize_if_done()

    def _on_translation_failure(self, book_id: int, error_msg: str):
        """Chamado quando tradução falha."""
        db = self.gui.library_view.model().db
        title = db.title(book_id, index_is_id=True) or f"ID {book_id}"
        self._errors.append(TranslationErrorResult(book_id, title, error_msg))

        self._pending_count -= 1
        self._finalize_if_done()

    def _finalize_if_done(self):
        """Verifica se todas as traduções terminaram."""
        if self._pending_count > 0:
            return  # Ainda tem tradução em andamento

        # Todas as traduções terminaram, processar fila de confirmações
        self._process_next_title_confirmation()

    def _process_next_title_confirmation(self):
        """Processa confirmação de título da fila."""
        if not self._title_confirmations:
            # Fila vazia, mostrar resumo final
            self._show_final_summary()
            return

        # Pegar próximo da fila
        book_id, orig_title, trans_title = self._title_confirmations.pop(0)

        # Mostrar diálogo
        dialog = ConfirmTitleDialog(self.gui, orig_title, trans_title)
        dialog.exec_()

        # Se usuário aceitou, atualizar BD
        if dialog.result:
            db = self.gui.library_view.model().db
            model = self.gui.library_view.model()
            calibre_db = CalibreDatabase(db)
            calibre_db.update_title(book_id, dialog.result)
            calibre_db.refresh_view([book_id], model)

        # Continuar para próximo
        self._process_next_title_confirmation()

    def _show_final_summary(self):
        """Mostra resumo final de sucesso/erro."""
        if self._errors:
            errors_str = self.presenter.format_error_messages(self._errors)
            error_dialog(
                self.gui,
                "Erro na Tradução",
                f"Ocorreram erros ao traduzir:\n\n{errors_str}",
                show=True,
            )
        else:
            info_dialog(
                self.gui,
                "Sucesso",
                "Metadados traduzidos com sucesso!",
                show=True,
            )
