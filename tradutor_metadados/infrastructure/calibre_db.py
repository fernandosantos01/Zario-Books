# -*- coding: utf-8 -*-
"""
Repository para acesso ao banco de dados do Calibre.

Encapsula métodos de leitura/escrita, facilitando testes e futuros cambios.
"""

from typing import List, Optional

from ..core.entities import Book


class CalibreDatabase:
    """Repository para acesso ao banco de dados do Calibre.

    Encapsula métodos de leitura/escrita de metadados,
    facilitando testes e abstração da implementação.
    """

    def __init__(self, db):
        """Inicializa repository.

        Args:
            db: Instância do banco de dados do Calibre
        """
        self.db = db

    def get_book(self, book_id: int) -> Book:
        """Carrega um livro do banco de dados.

        Args:
            book_id: ID do livro

        Returns:
            Entidade Book com dados do livro
        """
        title = self.db.title(book_id, index_is_id=True) or ""
        synopsis = self.db.comments(book_id, index_is_id=True) or ""

        return Book(
            id=book_id,
            title=title,
            synopsis=synopsis,
        )

    def update_synopsis(self, book_id: int, new_synopsis: str) -> None:
        """Atualiza sinopse de um livro.

        Args:
            book_id: ID do livro
            new_synopsis: Nova sinopse
        """
        self.db.set_comment(book_id, new_synopsis)

    def update_title(self, book_id: int, new_title: str) -> None:
        """Atualiza título de um livro.

        Args:
            book_id: ID do livro
            new_title: Novo título
        """
        self.db.set_title(book_id, new_title)

    def update_language(self, book_id: int, language_code: str) -> None:
        """Atualiza idioma de um livro.

        Args:
            book_id: ID do livro
            language_code: Código de idioma (ex: 'por', 'eng', 'spa')
        """
        self.db.set_languages(book_id, [language_code])

    def refresh_view(self, book_ids: List[int], view_model) -> None:
        """Atualiza visualização na UI após mudanças.

        Args:
            book_ids: Lista de IDs dos livros que foram atualizados
            view_model: Modelo da view a atualizar
        """
        view_model.refresh_ids(book_ids)
