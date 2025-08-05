import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout,
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QLabel
)
from PyQt5.QtCore import Qt

# Aquí importarías tus otras ventanas, p. ej.:
# from comercial import ComercialFormWindow
# from diagramacion import DiagramacionFormWindow
# etc.

class ConfigDialog(QDialog):
    """
    Diálogo para configurar la URL del ERP.
    """
    def __init__(self, current_api_url="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración de API")

        # Layout y campos
        layout = QFormLayout()
        self.api_url_edit = QLineEdit(current_api_url, self)
        layout.addRow("URL del ERP:", self.api_url_edit)

        # Botones Aceptar/Cancelar
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def get_api_url(self):
        """
        Devuelve la URL que el usuario haya escrito (si aceptó).
        """
        return self.api_url_edit.text().strip()


class MainWindow(QMainWindow):
    """
    Ventana principal que contiene un botón para abrir
    la 'configuración de API' (aquí la llamas “Logística”, si deseas).
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ERP - Menú Principal")

        # Guarda aquí la URL de la API (por defecto vacío, o un valor inicial)
        self.api_url = ""

        # Botón de "Logística" (o “Config. API”)
        self.logistica_button = QPushButton("Logística / Configuración API", self)
        self.logistica_button.clicked.connect(self.open_config_dialog)

        # Botón para abrir otras ventanas
        # (por ejemplo, Comercial, Producción, etc.)
        # Al abrirlas, les pasaremos la api_url que tengamos en self.api_url
        self.open_comercial_button = QPushButton("Abrir Comercial", self)
        self.open_comercial_button.clicked.connect(self.open_comercial_window)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Bienvenido al ERP"))
        layout.addWidget(self.logistica_button)
        layout.addWidget(self.open_comercial_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_config_dialog(self):
        """
        Abre el diálogo para editar la URL de la API.
        Si el usuario acepta, guardamos la URL en self.api_url.
        """
        dlg = ConfigDialog(current_api_url=self.api_url, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            new_url = dlg.get_api_url()
            if new_url:
                self.api_url = new_url
                print("Nueva URL:", self.api_url)
            else:
                print("No se ingresó URL nueva")

    def open_comercial_window(self):
        """
        Ejemplo: abrir la ventana Comercial con la URL actual.
        """
        # from comercial import ComercialFormWindow  # (Si no lo importaste arriba)
        # comercial_win = ComercialFormWindow(api_url=self.api_url, parent=self)
        # comercial_win.show()

        print("Aquí abrirías la ventana 'Comercial' con la URL:", self.api_url)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
