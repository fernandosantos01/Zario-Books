# -*- coding: utf-8 -*-
"""
Integração com API pública do Google Translate.

Encapsula lógica de:
- Limpeza de HTML
- Construção de URL
- Parsing de resposta
"""

import re
import urllib.parse
from typing import Optional

from ..core.exceptions import ApiResponseError, EmptyTextError
from .http_client import HttpClient


class TextProcessor:
    """Processador de texto com limpeza de HTML e reconstrução."""

    @staticmethod
    def clean_html(html_text: str) -> str:
        """Remove tags HTML do texto.

        Args:
            html_text: Texto com tags HTML

        Returns:
            Texto limpo sem tags

        Raises:
            EmptyTextError: Se texto ficar vazio após limpeza
        """
        # Remove todas as tags HTML
        cleaned = re.sub(r"<[^>]+>", "", html_text).strip()

        if not cleaned:
            raise EmptyTextError(
                "Texto ficou vazio após limpeza de HTML. "
                "Verifique se a sinopse tem conteúdo válido."
            )

        return cleaned

    @staticmethod
    def wrap_in_paragraph(text: str) -> str:
        """Envolve texto em tag <p>.

        Args:
            text: Texto a envolver

        Returns:
            Texto com tags <p> ao redor
        """
        return f"<p>{text}</p>"


class GoogleTranslateAPI:
    """Integração com API pública do Google Translate.

    Traduz texto de inglês para português usando endpoint não-oficial.

    Nota:
        Este é um endpoint não-oficial. Não há SLA, pode mudar sem aviso.
    """

    # Endpoint da API pública do Google
    API_URL = "https://translate.googleapis.com/translate_a/single"

    def __init__(self, http_client: Optional[HttpClient] = None):
        """Inicializa integração com Google Translate.

        Args:
            http_client: Cliente HTTP para requisições (cria padrão se não fornecido)
        """
        self.http_client = http_client or HttpClient()
        self.text_processor = TextProcessor()

    def translate(self, text: str, is_html: bool = False) -> str:
        """Traduz texto de inglês para português.

        Args:
            text: Texto a traduzir
            is_html: Se True, remove tags HTML antes de traduzir e
                    reconstrói com <p> depois

        Returns:
            Texto traduzido para português

        Raises:
            EmptyTextError: Se texto vazio
            NetworkError: Se falhar conexão
            ApiResponseError: Se resposta inválida
        """
        # Limpar texto conforme tipo
        if is_html:
            clean_text = self.text_processor.clean_html(text)
        else:
            clean_text = text.strip()
            if not clean_text:
                raise EmptyTextError("Texto vazio para tradução")

        # Construir URL da API
        url = (
            f"{self.API_URL}?"
            f"client=gtx&sl=en&tl=pt&dt=t&q={urllib.parse.quote(clean_text)}"
        )

        # Fazer requisição
        response_data = self.http_client.get(url)

        # Parsear resposta (estrutura: dados[0] = lista de sentenças)
        try:
            translated_sentences = [
                sentence[0] for sentence in response_data[0] if sentence and sentence[0]
            ]
            if not translated_sentences:
                raise ApiResponseError(
                    "Nenhuma sentença traduzida na resposta da API"
                )
            translated_text = "".join(translated_sentences)
        except (IndexError, KeyError, TypeError) as e:
            raise ApiResponseError(
                f"Estrutura de resposta inesperada da API: {e}"
            ) from e

        # Reconstitua HTML se necessário
        if is_html:
            return self.text_processor.wrap_in_paragraph(translated_text)

        return translated_text
