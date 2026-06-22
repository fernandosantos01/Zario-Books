# -*- coding: utf-8 -*-
"""
Exceções customizadas para a camada de domínio.

Define hierarquia clara de exceções para cada tipo de falha,
facilitando tratamento granular e testes.
"""


class TranslationError(Exception):
    """Exceção base para erros de tradução."""
    pass


class NetworkError(TranslationError):
    """Falha de conexão com o servidor de tradução."""
    pass


class ApiResponseError(TranslationError):
    """Resposta inesperada ou inválida da API."""
    pass


class ValidationError(TranslationError):
    """Falha na validação de entrada."""
    pass


class EmptyTextError(ValidationError):
    """Texto ficou vazio após processamento."""
    pass


class EmptySynopsisError(ValidationError):
    """Sinopse do livro está vazia ou não tem conteúdo suficiente."""
    pass
