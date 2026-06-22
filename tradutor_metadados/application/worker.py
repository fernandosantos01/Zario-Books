# -*- coding: utf-8 -*-
"""
Worker para executar tradução em thread separada.

Recebe TranslatorService injetado e apenas executa em thread,
emitindo sinais para comunicação com UI.
"""

from PyQt5.Qt import QThread, pyqtSignal

from ..core.entities import Book
from ..core.exceptions import EmptySynopsisError, TranslationError


class TranslationWorker(QThread):
    """Worker para traduzir em thread separada.

    Responsabilidades:
    - Recebe TranslatorService injetado
    - Executa tradução em thread separada
    - Emite sinais para comunicação com UI
    - Propaga exceções como sinais

    Não contém lógica de negócio, apenas orquestra execução.
    """

    # Sinal de sucesso: emitido quando tradução termina bem
    # Emite TranslationResult serializado
    success = pyqtSignal(int, str, str, str)  # book_id, synopsis, orig_title, trans_title

    # Sinal de falha: emitido quando algo dá errado
    failure = pyqtSignal(int, str)  # book_id, error_message

    def __init__(self, translator_service, book: Book):
        """Inicializa worker.

        Args:
            translator_service: TranslatorService injetado
            book: Entidade Book a traduzir
        """
        super().__init__()
        self.translator_service = translator_service
        self.book = book

    def run(self):
        """Executa tradução em thread separada.

        Trata todas as exceções e emite sinais apropriados.
        """
        try:
            # Executar lógica de tradução (pura)
            result = self.translator_service.translate_book(self.book)

            # Emitir sucesso
            self.success.emit(
                result.book_id,
                result.translated_synopsis,
                result.original_title,
                result.translated_title or "",
            )

        except EmptySynopsisError:
            # Livro sem sinopse: não é erro, apenas skip
            # Será tratado no orquestrador como "livro pulado"
            pass

        except TranslationError as e:
            # Erro de tradução (network, API, validation)
            self.failure.emit(self.book.id, str(e))

        except Exception as e:
            # Erro inesperado
            self.failure.emit(self.book.id, f"Erro inesperado: {e}")
