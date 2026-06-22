# -*- coding: utf-8 -*-
"""
Mensagens constantes para diálogos e notificações.

Centraliza strings de UI para facilitar manutenção e tradução.
"""


class DialogMessages:
    """Constantes de mensagens de UI."""

    # Diálogo de confirmação de título
    CONFIRM_TITLE_WINDOW = "Confirmar tradução do título"
    CONFIRM_TITLE_ORIGINAL = "<b>Título original:</b> {}"
    CONFIRM_TITLE_TRANSLATED = "<b>Título traduzido (edite se quiser):</b>"

    BTN_KEEP_ORIGINAL = "Manter original"
    BTN_USE_TRANSLATION = "Usar tradução"

    # Diálogos de erro
    ERROR_NO_BOOKS_SELECTED = (
        "Nenhum livro selecionado",
        "Por favor, selecione uma HQ ou livro na lista.",
    )

    ERROR_TRANSLATION_FAILED = (
        "Erro na Tradução",
        "Ocorreram erros ao traduzir:\n\n{}",
    )

    ERROR_EMPTY_SYNOPSIS = (
        "Sinopse Vazia",
        "O(s) seguinte(s) livro(s) não possui(em) sinopse para traduzir:\n{}",
    )

    # Diálogos de sucesso
    SUCCESS_TRANSLATION = ("Sucesso", "Metadados traduzidos com sucesso!")
    NOTHING_TO_DO = ("Nada a fazer", "Nenhuma sinopse para traduzir.")
