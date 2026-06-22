# -*- coding: utf-8 -*-
"""
Diálogos visuais para confirmar tradução de título.

Encapsula componentes PyQt5 de UI.
"""

from PyQt5.Qt import QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout


class ConfirmTitleDialog(QDialog):
    """Diálogo para confirmar tradução de título.

    Mostra:
    - Título original
    - Tradução sugerida (editável)
    - Botões: Manter original, Usar tradução
    """

    def __init__(self, parent, original_title: str, translated_title: str):
        """Inicializa diálogo.

        Args:
            parent: Janela pai
            original_title: Título original em inglês
            translated_title: Título traduzido sugerido
        """
        super().__init__(parent)
        self.setWindowTitle("Confirmar tradução do título")
        self.result = None  # None = manter original, string = usar esta tradução

        layout = QVBoxLayout(self)

        # Labels com títulos
        layout.addWidget(QLabel(f"<b>Título original:</b> {original_title}"))
        layout.addWidget(QLabel("<b>Título traduzido (edite se quiser):</b>"))

        # Campo de texto editável
        self.text_field = QLineEdit(translated_title)
        layout.addWidget(self.text_field)

        # Botões
        buttons = QHBoxLayout()

        btn_keep = QPushButton("Manter original")
        btn_keep.clicked.connect(self._keep_original)
        buttons.addWidget(btn_keep)

        btn_accept = QPushButton("Usar tradução")
        btn_accept.setDefault(True)
        btn_accept.clicked.connect(self._accept_translation)
        buttons.addWidget(btn_accept)

        layout.addLayout(buttons)
        self.setMinimumWidth(420)

    def _keep_original(self):
        """Usuário selecionou manter original."""
        self.result = None
        self.accept()

    def _accept_translation(self):
        """Usuário selecionou usar tradução."""
        self.result = self.text_field.text().strip()
        self.accept()
