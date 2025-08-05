import sys
import os
import asyncio
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QGridLayout, QWidget,
    QPushButton, QHBoxLayout, QMessageBox, QDialog, QFormLayout, QLineEdit,
    QDialogButtonBox
)
from PyQt5.QtCore import Qt, QTimer, QThread, QSettings
from PyQt5.QtGui import QPixmap

from comercial import ComercialFormWindow  # Importa la clase del formulario de Comercial
from diagramacion import DiagramacionFormWindow  # Importa la clase del formulario de Diagramación
from server import run_async_modbus_server  # Servidor Modbus
from produccion import ProduccionFormWindow  # Importa la clase del formulario de Producción
from taskprogram import TaskWindow          # Importa la clase del formulario de Programación de Tareas
from produccionplan import ProductionPlanerWindow  # Importa la clase del formulario de Plan de Producción

# --------------------------------------------------------------------
#  Diálogo simple para configurar la URL de la API
# --------------------------------------------------------------------
class ConfigDialog(QDialog):
    def __init__(self, current_api_url="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración de API")

        layout = QFormLayout()
        self.api_url_edit = QLineEdit(current_api_url, self)
        layout.addRow("URL del ERP:", self.api_url_edit)

        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            parent=self
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_api_url(self):
        """Devuelve la URL que el usuario ingresó (si presionó OK)."""
        return self.api_url_edit.text().strip()

# --------------------------------------------------------------------
#  Hilo para ejecutar el servidor Modbus en segundo plano
# --------------------------------------------------------------------
class ModbusServerThread(QThread):
    def run(self):
        asyncio.run(run_async_modbus_server())

# --------------------------------------------------------------------
#  Ventana Principal
# --------------------------------------------------------------------
class SoftwareWindow(QMainWindow):
    # URL base (ya no se usará para check_comercial / check_diagramacion)
    # Se mantiene en caso de querer un valor por defecto.
    BASE_URL = "https://script.google.com/macros/s/AKfycbxgX_-XgPuiRpAF0AQLn1EtIi7MxTpi5Gvlj-VVssg4VhPbRrT6hitDG7KUvGaLjXFweQ/exec"

    def __init__(self):
        super().__init__()

        # ----------------------------------------------------------------
        # 1) LEER / ESCRIBIR URL en QSettings para persistirla
        # ----------------------------------------------------------------
        self.settings = QSettings("HermencaCorp", "ERPApp")
        self.api_url = self.settings.value("api_url", defaultValue=self.BASE_URL)
        # Si no existía nada en QSettings, usamos self.BASE_URL como fallback

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(800, 600)
        self.setStyleSheet("background-color: white; border-radius: 15px;")

        self.layout = QVBoxLayout()

        # Mostrar imagen inicial
        image_path = self.get_resource_path('HERMENCA_LOGO.png')
        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            QMessageBox.critical(self, "Error", f"No se pudo cargar la imagen: {image_path}")
            sys.exit()

        self.image_label = QLabel(self)
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.central_widget = QWidget(self)
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        # Temporizador para mostrar el dashboard tras 1 segundo
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_dashboard)
        self.timer.start(1000)

        # Iniciar servidor Modbus en un hilo
        self.start_modbus_server()

    def get_resource_path(self, relative_path):
        """Obtiene la ruta del recurso, compatible con PyInstaller."""
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def start_modbus_server(self):
        self.modbus_thread = ModbusServerThread()
        self.modbus_thread.start()

    # ----------------------------------------------------------------
    #  Pantalla Dashboard tras la imagen inicial
    # ----------------------------------------------------------------
    def show_dashboard(self):
        self.timer.stop()
        self.showFullScreen()

        # Limpiar layout anterior
        self.layout.deleteLater()
        self.central_widget.deleteLater()

        # Nuevo widget central
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)

        # Barra superior (botón cerrar)
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setContentsMargins(0, 0, 0, 0)
        top_bar_layout.addStretch()

        close_button = QPushButton("X", self)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 18px;
                font-weight: bold;
                color: black;
            }
            QPushButton:hover {
                color: red;
            }
        """)
        close_button.setFixedSize(50, 50)
        close_button.clicked.connect(self.close)
        top_bar_layout.addWidget(close_button)

        main_layout.addLayout(top_bar_layout)

        # Logo
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(20, 10, 20, 10)
        image_path = self.get_resource_path('HERMENCA_LOGO.png')
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            QMessageBox.critical(self, "Error", f"No se pudo cargar la imagen: {image_path}")
            sys.exit()
        image_label = QLabel(self)
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(image_label)
        main_layout.addLayout(logo_layout)

        # Botones principales
        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(20, 20, 20, 20)

        # Cambiamos "Logística" -> "Configuración de API" con callback open_config_dialog
        buttons_data = [
            {"text": "Comercial",               "color": "#63c8aa", "callback": self.show_commercial_form},
            {"text": "Programación de tareas",  "color": "#207fbe", "callback": self.show_task_program_form},
            {"text": "Plan de producción",       "color": "#63c8aa", "callback": self.show_production_plan_form},
            {"text": "Diagramación",            "color": "#207fbe", "callback": self.show_diagramacion_form},
            {"text": "Producción",              "color": "#63c8aa", "callback": self.show_production_form},
            {"text": "Configuración de API",    "color": "#207fbe", "callback": self.open_config_dialog}
        ]

        index = 0
        for i in range(2):
            for j in range(3):
                if index < len(buttons_data):
                    data = buttons_data[index]
                    button = self.create_button(data["text"], data["color"], data["callback"])
                    grid_layout.addWidget(button, i, j)
                    index += 1

        main_layout.addLayout(grid_layout)

    def create_button(self, text, color, callback=None):
        button = QPushButton(text, self)
        button.setMinimumSize(200, 200)
        button.setStyleSheet(f"""
            background-color: {color};
            color: white;
            font-family: 'Arial Narrow', sans-serif;
            font-size: 24px;
            font-weight: bold;
            border-radius: 10px;
            padding: 10px;
        """)
        if callback:
            button.clicked.connect(callback)
        return button

    # ----------------------------------------------------------------
    #   Botones: abrir subventanas (sin verificación de Comercial/Diagramación)
    # ----------------------------------------------------------------
    def show_commercial_form(self):
        self.commercial_form = ComercialFormWindow(main_window=self,api_url=self.api_url)
        self.commercial_form.showFullScreen()
        self.hide()

    def show_diagramacion_form(self):
        # Eliminadas llamadas de verificación
        self.diagramacion_form = DiagramacionFormWindow(main_window=self,api_url=self.api_url)
        self.diagramacion_form.showFullScreen()
        self.hide()

    def show_production_form(self):
        self.production_form = ProduccionFormWindow(main_window=self, api_url=self.api_url)
        self.production_form.showFullScreen()
        self.hide()

    def show_task_program_form(self):
        self.task_program_form = TaskWindow(parent=self, api_url=self.api_url)
        self.task_program_form.showFullScreen()
        self.hide()

    def show_production_plan_form(self):
        self.production_plan_form = ProductionPlanerWindow(parent=self, api_url=self.api_url)
        self.production_plan_form.showFullScreen()
        self.hide()

    def show_main_window(self):
        self.showFullScreen()
        if hasattr(self, 'task_program_form') and self.task_program_form is not None:
            self.task_program_form.close()
        if hasattr(self, 'production_plan_form') and self.production_plan_form is not None:
            self.production_plan_form.close()

    # ----------------------------------------------------------------
    #   Configuración de API (persistencia en QSettings)
    # ----------------------------------------------------------------
    def open_config_dialog(self):
        dlg = ConfigDialog(current_api_url=self.api_url, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            new_url = dlg.get_api_url()
            if new_url:
                self.api_url = new_url
                self.settings.setValue("api_url", self.api_url)
                QMessageBox.information(self, "URL guardada", f"La nueva URL es:\n{self.api_url}")
            else:
                QMessageBox.warning(self, "Aviso", "No se ingresó una URL.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SoftwareWindow()
    window.show()
    sys.exit(app.exec_())
