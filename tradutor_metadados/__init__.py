# -*- coding: utf-8 -*-

from calibre.customize import InterfaceActionBase


class TradutorMetadadosPlugin(InterfaceActionBase):
    """
    Classe de registro do plugin. O Calibre lê esta classe para saber
    nome, versão, autor, etc. A lógica real do botão está em main.py,
    referenciada por 'actual_plugin' abaixo.
    """

    name                    = 'Tradutor de Metadados'
    description             = (
        'Traduz sinopse, título e idioma de livros/HQs de inglês para '
        'português usando a API do Google.'
    )
    supported_platforms     = ['windows', 'osx', 'linux']
    author                  = 'José Fernando || https://www.linkedin.com/in/fernandosantos00/'
    version                 = (2, 0, 0)
    minimum_calibre_version = (2, 0, 0)

    # Caminho do módulo real: calibre_plugins.<plugin-import-name>.<arquivo>:<classe>
    # O <plugin-import-name> tem que bater com o conteúdo do arquivo
    # plugin-import-name-tradutor_metadados.txt
    actual_plugin = 'calibre_plugins.tradutor_metadados.main:TradutorBotao'

    def is_customizable(self):
        return False