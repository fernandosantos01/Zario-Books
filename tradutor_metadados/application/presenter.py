# -*- coding: utf-8 -*-
"""
Presenter para formatação de resultados de tradução.

Separa lógica de formatação de dados da lógica de negócio.
"""

from typing import List

from ..core.entities import TranslationErrorResult


class TranslationPresenter:
    """Formata resultados de tradução para apresentação na UI.

    Responsável por:
    - Formatar erros como strings legíveis
    - Formatar listas de livros sem sinopse
    - Formatar resumo de sucesso
    """

    @staticmethod
    def format_error_messages(errors: List[TranslationErrorResult]) -> str:
        """Formata lista de erros como string multilinha.

        Args:
            errors: Lista de TranslationErrorResult

        Returns:
            String formatada para exibição em dialog
        """
        if not errors:
            return ""

        lines = [f"• {error.book_title}: {error.error_message}" for error in errors]
        return "\n".join(lines)

    @staticmethod
    def format_books_without_synopsis(titles: List[str]) -> str:
        """Formata lista de títulos de livros sem sinopse.

        Args:
            titles: Lista de títulos

        Returns:
            String formatada para exibição em dialog
        """
        if not titles:
            return ""
        return "\n- ".join([""] + titles)  # Inicia com quebra de linha

    @staticmethod
    def format_success_summary(count: int) -> str:
        """Formata resumo de sucesso.

        Args:
            count: Número de livros traduzidos com sucesso

        Returns:
            Mensagem formatada (com plural correto)
        """
        plural = "livro" if count == 1 else "livros"
        return f"{count} {plural} traduzido(s) com sucesso!"
