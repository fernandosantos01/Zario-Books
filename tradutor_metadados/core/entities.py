# -*- coding: utf-8 -*-
"""
Entidades de domínio: objetos que representam conceitos do negócio.

Usa dataclasses para imutabilidade, type hints e fácil serialização.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Book:
    """Representa um livro a ser traduzido."""

    id: int
    title: str
    synopsis: str
    language: str = "eng"

    def has_synopsis(self) -> bool:
        """Verifica se o livro tem sinopse com conteúdo."""
        return bool(self.synopsis and self.synopsis.strip())


@dataclass
class TranslationResult:
    """Resultado bem-sucedido de uma tradução de livro."""

    book_id: int
    translated_synopsis: str
    original_title: str
    translated_title: Optional[str]
    language: str = "por"


@dataclass
class TranslationErrorResult:
    """Resultado de erro durante tradução."""

    book_id: int
    book_title: str
    error_message: str
