# -*- coding: utf-8 -*-
"""
Testes unitários para entidades de domínio.

Valida comportamento das classes de domínio sem dependências.
"""

import unittest

from tradutor_metadados.core.entities import Book, TranslationErrorResult, TranslationResult


class TestBook(unittest.TestCase):
    """Testes para entidade Book."""

    def test_book_with_synopsis(self):
        """Livro com sinopse deve passar em has_synopsis()."""
        book = Book(id=1, title="Test Book", synopsis="Some meaningful text")
        self.assertTrue(book.has_synopsis())

    def test_book_without_synopsis(self):
        """Livro sem sinopse deve falhar em has_synopsis()."""
        book = Book(id=1, title="Test Book", synopsis="")
        self.assertFalse(book.has_synopsis())

    def test_book_with_whitespace_only(self):
        """Livro com apenas espaços deve falhar em has_synopsis()."""
        book = Book(id=1, title="Test Book", synopsis="   \n  \t  ")
        self.assertFalse(book.has_synopsis())

    def test_book_default_language(self):
        """Livro deve ter idioma padrão 'eng'."""
        book = Book(id=1, title="Test", synopsis="Text")
        self.assertEqual(book.language, "eng")


class TestTranslationResult(unittest.TestCase):
    """Testes para entidade TranslationResult."""

    def test_translation_result_creation(self):
        """Criar TranslationResult com dados válidos."""
        result = TranslationResult(
            book_id=1,
            translated_synopsis="<p>Texto traduzido</p>",
            original_title="Original Title",
            translated_title="Título Traduzido",
        )
        self.assertEqual(result.book_id, 1)
        self.assertEqual(result.language, "por")

    def test_translation_result_without_translated_title(self):
        """TranslationResult com translated_title=None."""
        result = TranslationResult(
            book_id=1,
            translated_synopsis="<p>Texto traduzido</p>",
            original_title="Original Title",
            translated_title=None,
        )
        self.assertIsNone(result.translated_title)


class TestTranslationErrorResult(unittest.TestCase):
    """Testes para entidade TranslationErrorResult."""

    def test_error_result_creation(self):
        """Criar TranslationErrorResult com dados de erro."""
        error = TranslationErrorResult(
            book_id=1,
            book_title="Test Book",
            error_message="Network error occurred",
        )
        self.assertEqual(error.book_id, 1)
        self.assertEqual(error.book_title, "Test Book")


if __name__ == "__main__":
    unittest.main()
