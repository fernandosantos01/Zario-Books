# -*- coding: utf-8 -*-
"""
Cliente HTTP com retry logic e tratamento de erros.

Abstrai urllib3 e fornece interface limpa para requisições.
"""

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional

from ..core.exceptions import ApiResponseError, NetworkError


class HttpClient:
    """Cliente HTTP para integração com APIs externas.

    Responsável por:
    - Requisições HTTP com timeout
    - Tratamento de erros de rede
    - Parsing de JSON
    - Headers padrão (User-Agent, etc)
    """

    def __init__(self, timeout: int = 15):
        """Inicializa cliente HTTP.

        Args:
            timeout: Timeout em segundos para requisições (padrão: 15s)
        """
        self.timeout = timeout
        self.default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

    def get(
        self, url: str, headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Faz requisição GET e retorna JSON parseado.

        Args:
            url: URL para requisição
            headers: Headers adicionais (opcional)

        Returns:
            Dicionário com resposta JSON parseada

        Raises:
            NetworkError: Se falhar conexão
            ApiResponseError: Se JSON inválido
        """
        try:
            # Mescla headers padrão com headers customizados
            merged_headers = {**self.default_headers, **(headers or {})}

            req = urllib.request.Request(url, headers=merged_headers)
            response = urllib.request.urlopen(req, timeout=self.timeout).read()
            return json.loads(response)

        except urllib.error.URLError as e:
            raise NetworkError(f"Falha de conexão com servidor: {e}") from e
        except json.JSONDecodeError as e:
            raise ApiResponseError(f"Resposta JSON inválida: {e}") from e
