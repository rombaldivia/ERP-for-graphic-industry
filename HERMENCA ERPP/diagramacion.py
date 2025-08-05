import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFormLayout, QLineEdit, QVBoxLayout,
    QPushButton, QHBoxLayout, QMessageBox, QScrollArea, QLabel, QComboBox,
    QCalendarWidget, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt

class DiagramacionFormWindow(QMainWindow):
    def __init__(self, main_window=None, api_url=""):
        """
        main_window: referencia a la ventana principal
        api_url: la URL real de la API que usas (pasada desde main.py)
        """
        super().__init__()
        self.main_window = main_window
        self.api_url = api_url  # <-- En vez de una constante

        self.setWindowTitle("Formulario de Diagramación")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #f0f0f0; border-radius: 20px;")

        # Layout principal
        self.main_layout = QVBoxLayout()

        # Scroll Area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")
        scroll_content = QWidget()
        scroll_layout = QHBoxLayout(scroll_content)

        # Columna izquierda (Formulario)
        form_container = QVBoxLayout()
        self.form_layout = QFormLayout()

        # Número de Proforma (ComboBox)
        self.numero_proforma = QComboBox(self)
        self.numero_proforma.setStyleSheet(self.style_light_blue())
        self.numero_proforma.currentIndexChanged.connect(self.cargar_datos_proforma)

        # Campos "Cliente" y "Descripción" (solo lectura)
        self.cliente = self.create_text_entry(read_only=True)
        self.descripcion = self.create_text_entry(read_only=True)

        # Campos de Diagramación
        self.fecha_recepcion_artes = self.create_date_lineedit()
        self.disenador = self.create_text_entry(editable=True)
        self.fecha_realizacion_preprensa = self.create_date_lineedit()
        self.fecha_envio_artes_aprobacion = self.create_date_lineedit()
        self.fecha_aprobacion_artes = self.create_date_lineedit()
        self.fecha_envio_ctp = self.create_date_lineedit()
        self.fecha_quemado_placas = self.create_date_lineedit()

        # Agregar campos al form_layout
        self.form_layout.addRow("Número de Proforma:", self.numero_proforma)

        # Cliente y Descripción (solo lectura)
        self.form_layout.addRow("Cliente:", self.cliente)
        self.form_layout.addRow("Descripción:", self.descripcion)

        self.form_layout.addRow("Fecha Recepción Artes:", self.fecha_recepcion_artes)
        self.form_layout.addRow("Diseñador:", self.disenador)
        self.form_layout.addRow("Fecha Realiz. Pre-Prensa:", self.fecha_realizacion_preprensa)
        self.form_layout.addRow("Fecha Envío Artes Aprob.:", self.fecha_envio_artes_aprobacion)
        self.form_layout.addRow("Fecha Aprobación Artes:", self.fecha_aprobacion_artes)
        self.form_layout.addRow("Fecha Envío a CTP:", self.fecha_envio_ctp)
        self.form_layout.addRow("Fecha Quemado de Placas:", self.fecha_quemado_placas)

        form_container.addLayout(self.form_layout)

        # Añadir form_container al scroll_layout
        scroll_layout.addLayout(form_container)
        scroll_area.setWidget(scroll_content)
        self.main_layout.addWidget(scroll_area)

        # Botones (Guardar y Volver)
        button_layout = QHBoxLayout()
        guardar_button = QPushButton("Guardar")
        guardar_button.clicked.connect(self.enviar_datos)
        guardar_button.setStyleSheet(self.style_button_blue())

        volver_button = QPushButton("Volver")
        volver_button.setStyleSheet(self.style_button_blue())
        volver_button.clicked.connect(self.go_back)

        button_layout.addWidget(guardar_button)
        button_layout.addWidget(volver_button)
        self.main_layout.addLayout(button_layout)

        # Central Widget
        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

        # Cargar proformas al iniciar
        self.cargar_proformas()

    # ------------------ CREACIÓN CAMPOS ------------------ #
    def create_text_entry(self, read_only=False, editable=False) -> QLineEdit:
        entry = QLineEdit(self)
        entry.setReadOnly(read_only)
        if read_only:
            entry.setStyleSheet(self.style_light_blue())
        elif editable:
            entry.setStyleSheet(self.style_editable_white())
        return entry

    def create_date_lineedit(self) -> QLineEdit:
        """
        Crea un QLineEdit que abrirá un calendario flotante al hacer clic.
        """
        lineedit = QLineEdit(self)
        lineedit.setReadOnly(True)
        lineedit.setStyleSheet("""
            background-color: white;
            padding: 10px;
            border: none;
            border-bottom: 2px solid #ccc;
            border-radius: 15px;
        """)
        lineedit.mousePressEvent = lambda event: self.show_calendar(lineedit)
        return lineedit

    # ------------------ CALENDARIO FLOTANTE ------------------ #
    def show_calendar(self, lineedit: QLineEdit):
        """
        Muestra un QWidget flotante con un QCalendarWidget centrado.
        Al hacer clic en una fecha, se coloca en lineedit con dd/MM/yyyy.
        """
        self.close_calendar()  # Cierra uno anterior si existe

        self.calendar_active_lineedit = lineedit

        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.set_date_from_calendar)
        self.calendar.setFixedSize(400, 300)

        close_button = QPushButton("Cerrar", self)
        close_button.setStyleSheet("background-color: #FF5733; color: white; font-size: 16px; padding: 5px;")
        close_button.clicked.connect(self.close_calendar)

        layout = QVBoxLayout()
        layout.addWidget(self.calendar)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)

        self.calendar_container = QWidget(self)
        self.calendar_container.setLayout(layout)

        # Centrar en la ventana principal
        center_x = self.width() // 2 - 200
        center_y = self.height() // 2 - 150
        self.calendar_container.setGeometry(center_x, center_y, 420, 350)

        self.calendar_container.show()
        self.calendar_container.raise_()

    def set_date_from_calendar(self, date):
        """Inserta la fecha en el lineedit activo y cierra el calendario."""
        if hasattr(self, "calendar_active_lineedit") and self.calendar_active_lineedit:
            self.calendar_active_lineedit.setText(date.toString("dd/MM/yyyy"))
        self.close_calendar()

    def close_calendar(self):
        if hasattr(self, "calendar_container") and self.calendar_container:
            self.calendar_container.hide()
            self.calendar_container.setParent(None)
            self.calendar_container = None
            self.calendar = None
            self.calendar_active_lineedit = None

    # ------------------ ESTILOS ------------------ #
    def style_light_blue(self) -> str:
        return (
            "background-color: lightblue;"
            "padding: 10px;"
            "border-radius: 10px;"
            "font-weight: bold;"
        )

    def style_editable_white(self) -> str:
        return (
            "background-color: white;"
            "padding: 10px;"
            "border-radius: 10px;"
            "border: 1px solid #ccc;"
        )

    def style_button_blue(self) -> str:
        return (
            "background-color: #4682B4;"
            "color: white;"
            "padding: 10px;"
            "font-size: 16px;"
            "border-radius: 20px;"
        )

    # ------------------ LÓGICA DE CARGA ------------------ #
    def cargar_proformas(self):
        """
        Llama a action=getAllProformas en la API y rellena el comboBox.
        """
        if not self.api_url:
            QMessageBox.warning(self, "Error", "No hay URL configurada para Diagramación.")
            return

        url = f"{self.api_url}?action=getAllProformas"
        try:
            response = requests.get(url)
            data = response.json()
            proformas = data.get("proformas", [])
            self.numero_proforma.clear()
            self.numero_proforma.addItems(proformas)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Error al conectar con la API: {e}")

    def cargar_datos_proforma(self):
        """
        Llama a action=getFullProformaData&numeroProforma=...
        y rellena los campos de Diagramación + Cliente & Descripción.
        """
        if not self.api_url:
            QMessageBox.warning(self, "Error", "No hay URL configurada para Diagramación.")
            return

        proforma = self.numero_proforma.currentText()
        url = f"{self.api_url}?action=getFullProformaData&numeroProforma={proforma}"
        try:
            response = requests.get(url)
            data = response.json()

            comercial = data.get("Comercial", [])
            diagramacion = data.get("Diagramacion", [])

            if not comercial or not diagramacion:
                QMessageBox.warning(
                    self, "Advertencia",
                    "No hay datos de Diagramación (o Comercial) para esta proforma."
                )
                return

            # Ajusta según tu hoja: [2]=cliente, [4]=descripcion, etc.
            self.cliente.setText(str(comercial[2]) if len(comercial) > 2 else "")
            self.descripcion.setText(str(comercial[4]) if len(comercial) > 4 else "")

            def format_date(api_date):
                parts = api_date.split("T")[0].split("-") if api_date else ["","",""]
                if len(parts) == 3:
                    return f"{parts[2]}/{parts[1]}/{parts[0]}"
                return ""

            self.fecha_recepcion_artes.setText(format_date(diagramacion[0]) if len(diagramacion)>0 else "")
            self.disenador.setText(str(diagramacion[1]) if len(diagramacion)>1 else "")
            self.fecha_realizacion_preprensa.setText(format_date(diagramacion[2]) if len(diagramacion)>2 else "")
            self.fecha_envio_artes_aprobacion.setText(format_date(diagramacion[3]) if len(diagramacion)>3 else "")
            self.fecha_aprobacion_artes.setText(format_date(diagramacion[4]) if len(diagramacion)>4 else "")
            self.fecha_envio_ctp.setText(format_date(diagramacion[5]) if len(diagramacion)>5 else "")
            self.fecha_quemado_placas.setText(format_date(diagramacion[6]) if len(diagramacion)>6 else "")

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Error al conectar con la API: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error inesperado", f"{e}")

    # ------------------ LÓGICA DE ENVÍO ------------------ #
    def enviar_datos(self):
        if not self.api_url:
            QMessageBox.warning(self, "Error", "No hay URL configurada para Diagramación.")
            return

        def revert_date(ddmm):
            partes = ddmm.split("/")
            if len(partes) == 3:
                return f"{partes[2]}-{partes[1]}-{partes[0]}"
            return ddmm

        data = {
            "section": "Diagramacion",
            "numeroProforma": self.numero_proforma.currentText(),
            "fechaRecepcionArtes": revert_date(self.fecha_recepcion_artes.text()),
            "diseñador": self.disenador.text(),
            "fechaRealizacionPrePrensa": revert_date(self.fecha_realizacion_preprensa.text()),
            "fechaEnvioArtesAprobacion": revert_date(self.fecha_envio_artes_aprobacion.text()),
            "fechaAprobacionArtes": revert_date(self.fecha_aprobacion_artes.text()),
            "fechaEnvioCTP": revert_date(self.fecha_envio_ctp.text()),
            "fechaQuemadoPlacas": revert_date(self.fecha_quemado_placas.text())
        }
        try:
            resp = requests.post(self.api_url, json=data)
            resp_text = resp.text
            if "Error" in resp_text:
                QMessageBox.critical(self, "Error", f"Ocurrió un problema al guardar: {resp_text}")
            else:
                QMessageBox.information(self, "Éxito", "Datos de Diagramación guardados correctamente.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar con la API: {e}")

    def go_back(self):
        self.close()
        if self.main_window:
            self.main_window.showFullScreen()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Ejemplo de prueba con una URL
    # window = DiagramacionFormWindow(api_url="https://script.google.com/macros/s/TU-URL/exec")
    window = DiagramacionFormWindow()
    window.showFullScreen()
    sys.exit(app.exec_())
