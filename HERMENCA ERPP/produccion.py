import sys
import requests
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFormLayout, QLineEdit, QVBoxLayout,
    QCheckBox, QPushButton, QHBoxLayout, QMessageBox, QScrollArea, QLabel,
    QComboBox, QCalendarWidget, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt

class ProduccionFormWindow(QMainWindow):
    # Mapeo entre la etiqueta del checkbox en la UI y la clave que doPost espera
    CHECKBOX_KEYS = {
        "XLUV": "xlUV",
        "XL75 (ANICOLOR)": "xl75",
        "Barnizado": "barnizado",
        "Hotstamping": "hotstamping",
        "Plastificado": "plastificado",
        "Localizado": "localizado",
        "Sello Seco": "selloSeco",
        "EASY MATRIX": "easyMatrix",
        "CILINDRICA": "cilindrica",
        "TIPOGRAFICA": "tipografica",
        "Peg. 1 Punto": "peg1Punto",
        "Peg. 3 Puntos": "peg3Puntos",
        "Perforado": "perforado",
        "Doblado": "doblado",
        "Compaginado": "compaginado",
        "Engrapado": "engrapado",
        "Emblocado": "emblocado",
        "Engarrado": "engarrado",
        "Pegado con Tesa": "pegadoConTesa"
    }

    def __init__(self, main_window=None, api_url=""):
        """
        main_window: Referencia a la ventana principal.
        api_url: La URL de tu API que recibes desde main.py.
        """
        super().__init__()
        self.main_window = main_window
        self.api_url = api_url  # <-- Se usará en vez de la constante

        self.setWindowTitle("Formulario de Producción")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #f0f0f0; border-radius: 20px;")

        # Layout principal
        self.main_layout = QVBoxLayout()

        # Área de desplazamiento
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

        # Campos de Producción
        self.numero_ot = self.create_text_entry(editable=True)
        self.cliente = self.create_text_entry(read_only=True)
        self.descripcion = self.create_text_entry(read_only=True)

        # Fechas con lineEdit + calendario flotante
        self.fecha_apertura_ot = self.create_date_lineedit()
        self.fecha_entrega = self.create_date_lineedit()

        self.cartulina_papel = self.create_text_entry(editable=True)
        self.cantidad_hojas = self.create_text_entry(editable=True)
        self.tiraje_impresion = self.create_text_entry(editable=True)
        self.tinta = self.create_text_entry(editable=True)
        self.placas = self.create_text_entry(editable=True)
        self.tipo_impresion = self.create_text_entry(editable=True)
        self.numero_pasadas = self.create_text_entry(editable=True)

        # Agregar campos al formulario
        self.form_layout.addRow("Número de Proforma:", self.numero_proforma)
        self.form_layout.addRow("Número de O.T.:", self.numero_ot)
        self.form_layout.addRow("Cliente:", self.cliente)
        self.form_layout.addRow("Descripción:", self.descripcion)
        self.form_layout.addRow("Fecha Apertura de O.T.:", self.fecha_apertura_ot)
        self.form_layout.addRow("Fecha de Entrega:", self.fecha_entrega)
        self.form_layout.addRow("Cartulina y Papel:", self.cartulina_papel)
        self.form_layout.addRow("Cantidad de Hojas:", self.cantidad_hojas)
        self.form_layout.addRow("Tiraje en impresión:", self.tiraje_impresion)
        self.form_layout.addRow("Tinta:", self.tinta)
        self.form_layout.addRow("Placas:", self.placas)
        self.form_layout.addRow("Tipo de Impresión:", self.tipo_impresion)
        self.form_layout.addRow("N° de pasadas:", self.numero_pasadas)

        form_container.addLayout(self.form_layout)

        # Columna derecha (CheckBoxes)
        checkbox_container = QVBoxLayout()
        checkbox_title = QLabel("Procesos de Impresión:")
        checkbox_title.setStyleSheet("font-weight: bold; font-size: 14px; padding-bottom: 5px;")
        checkbox_container.addWidget(checkbox_title)

        self.checkboxes = {}
        checkbox_titles = list(self.CHECKBOX_KEYS.keys())
        for label in checkbox_titles:
            checkbox = self.create_checkbox(label)
            self.checkboxes[label] = checkbox
            checkbox_container.addWidget(checkbox)

        # Añadir ambas columnas al scroll_layout
        scroll_layout.addLayout(form_container)
        scroll_layout.addLayout(checkbox_container)

        # Botones (Guardar y Volver)
        button_layout = QHBoxLayout()
        guardar_button = QPushButton("Guardar")
        guardar_button.setStyleSheet(self.style_button_blue())
        guardar_button.clicked.connect(self.enviar_datos)

        back_button = QPushButton("Volver")
        back_button.setStyleSheet(self.style_button_blue())
        back_button.clicked.connect(self.go_back)

        button_layout.addWidget(guardar_button)
        button_layout.addWidget(back_button)

        # Integración final
        scroll_area.setWidget(scroll_content)
        self.main_layout.addWidget(scroll_area)
        self.main_layout.addLayout(button_layout)

        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

        # Cargar proformas al iniciar
        self.cargar_proformas()

    # ------------------- CREACIÓN CAMPOS ------------------- #
    def create_text_entry(self, read_only=False, editable=False) -> QLineEdit:
        entry = QLineEdit(self)
        entry.setReadOnly(read_only)
        if read_only:
            entry.setStyleSheet(self.style_light_blue())
        elif editable:
            entry.setStyleSheet(self.style_editable_white())
        return entry

    def create_date_lineedit(self) -> QLineEdit:
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

    def create_checkbox(self, label: str) -> QCheckBox:
        checkbox = QCheckBox(label)
        checkbox.setStyleSheet("QCheckBox::indicator { width: 18px; height: 18px; }")
        return checkbox

    # ------------------- CALENDARIO FLOTANTE ------------------- #
    def show_calendar(self, lineedit: QLineEdit):
        self.close_calendar()
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

    # ------------------- ESTILOS ------------------- #
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

    # ------------------- LÓGICA DE CARGA ------------------- #
    def cargar_proformas(self):
        """
        Llamamos a action=getAllProformas usando self.api_url en vez de la constante.
        """
        if not self.api_url:
            QMessageBox.warning(self, "Error", "No hay URL configurada para Producción.")
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
        Llamamos a action=getFullProformaData&numeroProforma=...
        usando self.api_url para obtener los datos y mostrarlos.
        """
        if not self.api_url:
            QMessageBox.warning(self, "Error", "No hay URL configurada para Producción.")
            return

        proforma = self.numero_proforma.currentText()
        url = f"{self.api_url}?action=getFullProformaData&numeroProforma={proforma}"
        try:
            response = requests.get(url)
            data = response.json()
            print("\n📢 Datos de la API recibidos:", data)

            comercial = data.get("Comercial", [])
            produccion = data.get("Produccion", [])

            if not comercial or not produccion:
                QMessageBox.warning(self, "Advertencia", "No hay datos de producción para esta proforma.")
                return

            # Comercial
            self.cliente.setText(str(comercial[2]) if len(comercial) > 2 else "")
            self.descripcion.setText(str(comercial[4]) if len(comercial) > 4 else "")

            # Producción
            self.numero_ot.setText(str(produccion[0]) if len(produccion) > 0 else "")

            fecha_apertura = str(produccion[1]).split("T")[0] if len(produccion) > 1 else ""
            fecha_entrega = str(produccion[2]).split("T")[0] if len(produccion) > 2 else ""
            fa_split = fecha_apertura.split("-") if fecha_apertura else ["", "", ""]
            fe_split = fecha_entrega.split("-") if fecha_entrega else ["", "", ""]

            self.fecha_apertura_ot.setText(f"{fa_split[2]}/{fa_split[1]}/{fa_split[0]}")
            self.fecha_entrega.setText(f"{fe_split[2]}/{fe_split[1]}/{fe_split[0]}")

            self.cartulina_papel.setText(str(produccion[3]) if len(produccion) > 3 else "")
            self.cantidad_hojas.setText(str(produccion[4]) if len(produccion) > 4 else "")
            self.tiraje_impresion.setText(str(produccion[5]) if len(produccion) > 5 else "")

            # Tinta, placas, tipoImp, pasadas (índices 25..28)
            tinta = str(produccion[25]) if len(produccion) > 25 else ""
            placas = str(produccion[26]) if len(produccion) > 26 else ""
            tipo_imp = str(produccion[27]) if len(produccion) > 27 else ""
            pasadas = str(produccion[28]) if len(produccion) > 28 else ""
            self.tinta.setText(tinta)
            self.placas.setText(placas)
            self.tipo_impresion.setText(tipo_imp)
            self.numero_pasadas.setText(pasadas)

            # Procesos de impresión (índices 6..24)
            procesos_de_impresion = produccion[6:25] if len(produccion) > 24 else []
            for i, checkbox in enumerate(self.checkboxes.values()):
                if i < len(procesos_de_impresion):
                    checkbox.setChecked(procesos_de_impresion[i] == "X")
                else:
                    checkbox.setChecked(False)

            # Manejar "Pegado con Tesa" en índice 24
            if len(produccion) > 24 and produccion[24] == "X":
                label_tesa = "Pegado con Tesa"
                if label_tesa in self.checkboxes:
                    self.checkboxes[label_tesa].setChecked(True)

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Error al conectar con la API: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error inesperado", str(e))

    # ------------------- LÓGICA DE ENVÍO ------------------- #
    def enviar_datos(self):
        """
        Envía la info de Producción con section=Produccion y checkboxes marcados.
        """
        if not self.api_url:
            QMessageBox.warning(self, "Error", "No hay URL configurada para Producción.")
            return

        datos = {
            "section": "Produccion",
            "numeroProforma": self.numero_proforma.currentText(),
            "numeroOT": self.numero_ot.text(),
            "fechaAperturaOT": self.fecha_apertura_ot.text(),
            "fechaEntrega": self.fecha_entrega.text(),
            "cartulinaPapel": self.cartulina_papel.text(),
            "cantidadHojas": self.cantidad_hojas.text(),
            "tirajeImpresion": self.tiraje_impresion.text(),
            "tinta": self.tinta.text(),
            "placas": self.placas.text(),
            "tipoImpresion": self.tipo_impresion.text(),
            "numeroPasadas": self.numero_pasadas.text()
        }

        # Marcar "X" en los checkboxes activados
        for label, checkbox in self.checkboxes.items():
            if label == "XLUV":
                datos["xlUV"] = "X" if checkbox.isChecked() else ""
            elif label == "XL75 (ANICOLOR)":
                datos["xl75"] = "X" if checkbox.isChecked() else ""
            elif label == "Barnizado":
                datos["barnizado"] = "X" if checkbox.isChecked() else ""
            elif label == "Hotstamping":
                datos["hotstamping"] = "X" if checkbox.isChecked() else ""
            elif label == "Plastificado":
                datos["plastificado"] = "X" if checkbox.isChecked() else ""
            elif label == "Localizado":
                datos["localizado"] = "X" if checkbox.isChecked() else ""
            elif label == "Sello Seco":
                datos["selloSeco"] = "X" if checkbox.isChecked() else ""
            elif label == "EASY MATRIX":
                datos["easyMatrix"] = "X" if checkbox.isChecked() else ""
            elif label == "CILINDRICA":
                datos["cilindrica"] = "X" if checkbox.isChecked() else ""
            elif label == "TIPOGRAFICA":
                datos["tipografica"] = "X" if checkbox.isChecked() else ""
            elif label == "Peg. 1 Punto":
                datos["peg1Punto"] = "X" if checkbox.isChecked() else ""
            elif label == "Peg. 3 Puntos":
                datos["peg3Puntos"] = "X" if checkbox.isChecked() else ""
            elif label == "Perforado":
                datos["perforado"] = "X" if checkbox.isChecked() else ""
            elif label == "Doblado":
                datos["doblado"] = "X" if checkbox.isChecked() else ""
            elif label == "Compaginado":
                datos["compaginado"] = "X" if checkbox.isChecked() else ""
            elif label == "Engrapado":
                datos["engrapado"] = "X" if checkbox.isChecked() else ""
            elif label == "Emblocado":
                datos["emblocado"] = "X" if checkbox.isChecked() else ""
            elif label == "Engarrado":
                datos["engarrado"] = "X" if checkbox.isChecked() else ""
            elif label == "Pegado con Tesa":
                datos["pegadoConTesa"] = "X" if checkbox.isChecked() else ""

        try:
            response = requests.post(self.api_url, json=datos)
            resp_text = response.text
            if "Error" in resp_text:
                QMessageBox.critical(self, "Error", f"Hubo un problema al guardar: {resp_text}")
            else:
                QMessageBox.information(self, "Éxito", "Los datos fueron guardados correctamente.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar con la API: {e}")

    def go_back(self):
        """
        Cierra esta ventana y regresa a la ventana principal (si existe).
        """
        self.close()
        if self.main_window:
            self.main_window.showFullScreen()


# ------------------------------------------------------------
#     Ejemplo de ejecución independiente (para pruebas)
# ------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Por ejemplo, pasar la URL si deseas:
    # window = ProduccionFormWindow(api_url="https://script.google.com/macros/s/TU_URL/exec")
    window = ProduccionFormWindow()
    window.showFullScreen()
    sys.exit(app.exec_())
