# -*- coding: utf-8 -*-
"""
Tradutor de Metadados - Plugin para Calibre

Traduz automaticamente metadados (sinopse, título, idioma) de livros/HQs
do inglês para português (PT-BR), usando a API pública de tradução do Google.

Entry point do plugin.
"""

from .plugin import TradutorBotao

__all__ = ["TradutorBotao"]


def load_translations():
    """Função obrigatória pelo Calibre para suporte a i18n."""
    return {}