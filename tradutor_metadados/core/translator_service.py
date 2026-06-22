# -*- coding: utf-8 -*-
"""
Serviço de tradução: lógica de negócio pura.

Orquestra a tradução de sinopse e título sem dependências de UI ou threads.
Completamente testável e reutilizável.
"""

from typing import Optional

from .entities import Book, TranslationResult
from .exceptions import EmptySynopsisError


class TranslatorService:
    """Serviço de tradução com lógica de negócio pura.

    Responsável por:
    - Validar livro (tem sinopse?)
    - Traduzir sinopse (sempre)
    - Traduzir título (se houver)
    - Retornar resultado estruturado

    Esta classe é 100% testável sem mocking de UI/BD/HTTP.
    """

    def __init__(self, translation_api):
        """Inicializa serviço de tradução.

        Args:
            translation_api: API de tradução (GoogleTranslateAPI ou similar)
                            Qualquer classe com método translate(text, is_html)
        """
        self.translation_api = translation_api

    def translate_book(self, book: Book) -> TranslationResult:
        """Traduz sinopse e título de um livro.

        Fluxo:
        1. Valida se livro tem sinopse
        2. Traduz sinopse (sempre, é o core da funcionalidade)
        3. Traduz título se houver
        4. Retorna resultado estruturado

        Args:
            book: Entidade Book com dados do livro

        Returns:
            TranslationResult com sinopse e título traduzidos

        Raises:
            EmptySynopsisError: Se livro não tem sinopse
            (outras exceções de API são propagadas)
        """
        # Validação: livro deve ter sinopse
        if not book.has_synopsis():
            raise EmptySynopsisError(
                f"Livro '{book.title}' não tem sinopse para traduzir"
            )

        # Traduzir sinopse (HTML)
        translated_synopsis = self.translation_api.translate(
            book.synopsis, is_html=True
        )

        # Traduzir título (se houver)
        translated_title: Optional[str] = None
        if book.title:
            translated_title = self.translation_api.translate(
                book.title, is_html=False
            )

        # Retornar resultado estruturado
        return TranslationResult(
            book_id=book.id,
            translated_synopsis=translated_synopsis,
            original_title=book.title,
            translated_title=translated_title,
            language="por",
        )
