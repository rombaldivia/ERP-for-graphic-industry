import sys
import requests
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QFormLayout, QScrollArea, QMessageBox,
    QComboBox, QCalendarWidget, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt

class ComercialFormWindow(QMainWindow):
    def __init__(self, main_window=None, api_url=""):
        super().__init__()
        self.main_window = main_window
        self.api_url = api_url  # <-- Aquí manejas la URL (en vez de una constante fija)

        self.setWindowTitle("Formulario Comercial (Crear / Editar)")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #f0f0f0; border-radius: 15px;")

        # Variables para "Crear"
        self.forms = []               # Contendrá dict con info de cada formulario (layout, widgets, etc.)
        self.form_count = 0
        self.last_proforma_number = None  # Para trackear el último # de proforma en la hoja

        # Variables para "Editar"
        self.edit_combo_proforma = None

        # Layout principal
        self.main_layout = QVBoxLayout()

        # Barra superior con botón "Cerrar"
        top_bar_layout = QHBoxLayout()
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
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.close)
        top_bar_layout.addWidget(close_button)
        self.main_layout.addLayout(top_bar_layout)

        # QTabWidget (dos pestañas: "Crear" y "Editar")
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("QTabWidget::pane { border: none; }")
        self.tab_create = QWidget()
        self.tab_edit = QWidget()

        self.setup_create_tab()
        self.setup_edit_tab()

        self.tab_widget.addTab(self.tab_create, "Crear")
        self.tab_widget.addTab(self.tab_edit,   "Editar")
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        self.main_layout.addWidget(self.tab_widget)
        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

        # Comienza en la pestaña "Crear" y añade 1 formulario por defecto
        self.tab_widget.setCurrentIndex(0)
        self.add_form_entry()

    # ---------------------------------------------------------------------
    #                         PESTAÑA "CREAR"
    # ---------------------------------------------------------------------
    def setup_create_tab(self):
        layout = QVBoxLayout(self.tab_create)
        scroll_area = QScrollArea(self.tab_create)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")

        self.scroll_widget_create = QWidget()
        self.scroll_layout_create = QVBoxLayout(self.scroll_widget_create)

        # Botonera superior
        create_button_layout = QHBoxLayout()
        create_button_layout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )

        self.add_button = QPushButton("Añadir Otro Pedido", self.tab_create)
        self.add_button.setStyleSheet("""
            background-color: #87CEFA; color: white;
            font-size: 16px; padding: 5px;
        """)
        self.add_button.setFixedWidth(200)
        self.add_button.clicked.connect(self.add_form_entry)
        create_button_layout.addWidget(self.add_button)

        self.submit_button_create = QPushButton("Enviar", self.tab_create)
        self.submit_button_create.setStyleSheet("""
            background-color: #4682B4; color: white;
            font-size: 16px; padding: 5px;
        """)
        self.submit_button_create.setFixedWidth(200)
        self.submit_button_create.clicked.connect(self.submit_create_mode)
        create_button_layout.addWidget(self.submit_button_create)

        back_button_create = QPushButton("Volver", self.tab_create)
        back_button_create.setStyleSheet("""
            background-color: #FF5733; color: white;
            font-weight: bold; font-size:16px; padding:5px;
        """)
        back_button_create.setFixedWidth(200)
        back_button_create.clicked.connect(self.go_back)
        create_button_layout.addWidget(back_button_create)

        create_button_layout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )

        self.scroll_layout_create.addLayout(create_button_layout)

        # Aquí meteremos los formularios
        self.form_layout_create = QVBoxLayout()
        self.scroll_layout_create.addLayout(self.form_layout_create)

        scroll_area.setWidget(self.scroll_widget_create)
        layout.addWidget(scroll_area)

    def add_form_entry(self):
        self.form_count += 1
        form_dict = self.create_form_entry(self.form_count)
        self.forms.append(form_dict)

    def create_form_entry(self, index):
        """
        Crea un QFormLayout con los campos de Comercial.
        Añade un botón "X" para eliminar excepto en el primero.
        """
        # Generamos un nuevo número de proforma
        prof_number = self.get_new_proforma_number()

        # Title layout con "Nº Proforma X" y botón "X"
        title_layout = QHBoxLayout()
        title_label = QLabel(f"Nº Proforma Aprobada {index}:", self.tab_create)
        remove_btn = QPushButton("X", self.tab_create)
        remove_btn.setFixedSize(24, 24)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4d4d;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e60000;
            }
        """)
        # Al hacer clic, eliminamos este form (excepto si es index=1)
        remove_btn.clicked.connect(lambda _, idx=index: self.remove_form_entry(idx))

        if index == 1:
            remove_btn.setEnabled(False)

        title_layout.addWidget(title_label)
        title_layout.addWidget(remove_btn)

        # Campo con el número de proforma
        proforma_label = QLineEdit(prof_number, self.tab_create)
        proforma_label.setReadOnly(True)
        proforma_label.setStyleSheet("""
            background-color: white;
            border:1px solid #000;
            border-radius:5px;
            padding:5px;
            font-size:16px;
            color:#000;
        """)

        ejecutivo_comercial = QLineEdit(self.tab_create)
        cliente = QLineEdit(self.tab_create)
        clasificacion_cliente = QLineEdit(self.tab_create)
        descripcion = QLineEdit(self.tab_create)
        cantidad_pedido = QLineEdit(self.tab_create)

        fecha_entrega = QLineEdit(self.tab_create)
        fecha_entrega.setReadOnly(True)
        fecha_entrega.setStyleSheet("""
            background-color:white;
            border:1px solid #000;
            border-radius:5px;
            padding:5px;
            font-size:16px;
            color:#000;
        """)
        # Calendario flotante
        fecha_entrega.mousePressEvent = lambda event, idx=index: self.show_calendar_create(event, idx)

        for w in [ejecutivo_comercial, cliente, clasificacion_cliente, descripcion, cantidad_pedido]:
            w.setStyleSheet("""
                background-color:white;
                border:1px solid #000;
                border-radius:5px;
                padding:5px;
                font-size:16px;
                color:#000;
            """)

        layout = QFormLayout()

        # Metemos en la primera fila => col(0) un QWidget con title_layout
        row_container = QWidget()
        row_container.setLayout(title_layout)
        layout.addRow(row_container, proforma_label)

        layout.addRow(f"Ejecutivo Comercial {index}:", ejecutivo_comercial)
        layout.addRow(f"Cliente {index}:", cliente)
        layout.addRow(f"Clasificación {index}:", clasificacion_cliente)
        layout.addRow(f"Descripción {index}:", descripcion)
        layout.addRow(f"Cantidad de Pedido {index}:", cantidad_pedido)
        layout.addRow(f"Fecha de Entrega {index}:", fecha_entrega)

        self.form_layout_create.addLayout(layout)

        return {
            "index": index,
            "layout": layout,
            "num_proforma": proforma_label,
            "ejecutivo_comercial": ejecutivo_comercial,
            "cliente": cliente,
            "clasificacion_cliente": clasificacion_cliente,
            "descripcion": descripcion,
            "cantidad_pedido": cantidad_pedido,
            "fecha_entrega": fecha_entrega
        }

    def remove_form_entry(self, index):
        """
        Elimina el formulario con este índice y reasigna los siguientes.
        """
        if index == 1:
            return  # No borramos el primero

        to_remove = None
        for f in self.forms:
            if f["index"] == index:
                to_remove = f
                break
        if not to_remove:
            return

        layout = to_remove["layout"]
        self.removeLayout(layout, self.form_layout_create)
        self.forms.remove(to_remove)

        # Recalcular self.form_count
        self.form_count = len(self.forms)
        # Reasignar índices y proformas
        self.reassign_forms()

    def removeLayout(self, layout, parent_layout):
        """
        Elimina el QFormLayout del parent_layout, limpiando sus widgets.
        """
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

        # Quitar layout de parent_layout
        i = 0
        while i < parent_layout.count():
            item = parent_layout.itemAt(i)
            if item.layout() == layout:
                parent_layout.removeItem(item)
                break
            i += 1

    def reassign_forms(self):
        """
        Reasigna índices y números de proforma a cada formulario.
        """
        self.last_proforma_number = None
        for i, f in enumerate(self.forms, start=1):
            f["index"] = i
            # Generamos un nuevo proforma
            new_prof = self.get_new_proforma_number()
            f["num_proforma"].setText(new_prof)

            layout = f["layout"]
            # Actualizar labels (Ejecutivo Comercial i, etc.)
            self.updateFormLayoutLabelText(layout, 1, f"Ejecutivo Comercial {i}:")
            self.updateFormLayoutLabelText(layout, 2, f"Cliente {i}:")
            self.updateFormLayoutLabelText(layout, 3, f"Clasificación {i}:")
            self.updateFormLayoutLabelText(layout, 4, f"Descripción {i}:")
            self.updateFormLayoutLabelText(layout, 5, f"Cantidad de Pedido {i}:")
            self.updateFormLayoutLabelText(layout, 6, f"Fecha de Entrega {i}:")

            # Cambia la label "Nº Proforma Aprobada i:"
            row0_item = layout.itemAt(0, QFormLayout.LabelRole)
            if row0_item:
                row0_widget = row0_item.widget()
                if row0_widget:
                    hlayout = row0_widget.layout()
                    if hlayout and hlayout.count() > 0:
                        lbl = hlayout.itemAt(0).widget()
                        if lbl:
                            lbl.setText(f"Nº Proforma Aprobada {i}:")
                        remove_btn = hlayout.itemAt(1).widget()
                        if i == 1:
                            remove_btn.setEnabled(False)
                        else:
                            remove_btn.setEnabled(True)

    def updateFormLayoutLabelText(self, layout, rowIndex, newText):
        label_item = layout.itemAt(rowIndex, QFormLayout.LabelRole)
        if label_item:
            label_widget = label_item.widget()
            if label_widget:
                label_widget.setText(newText)

    def get_new_proforma_number(self):
        """
        Genera un nuevo número de proforma con sufijo de año (dd..-yy).
        """
        if not self.api_url:
            # No hay URL => creamos un dummy
            return "0000-00"

        suffix = datetime.now().year % 100  # p.ej. 25 => 2025
        if self.last_proforma_number is None:
            url = f"{self.api_url}?action=getLastProforma"
            try:
                resp = requests.get(url)
                resp.raise_for_status()
                data = resp.json()
                last_prof = str(data.get("lastProforma", f"0000-{suffix}"))
                base_number = last_prof.split("-")[0]
                self.last_proforma_number = int(base_number)
            except:
                self.last_proforma_number = 0

        self.last_proforma_number += 1
        return f"{self.last_proforma_number:04d}-{suffix}"

    # Calendario "Crear"
    def show_calendar_create(self, event, index):
        form = None
        for f in self.forms:
            if f["index"] == index:
                form = f
                break
        if not form:
            return

        self.calendar_create = QCalendarWidget(self.tab_create)
        self.calendar_create.setGridVisible(True)
        self.calendar_create.setFixedSize(400,300)

        close_btn = QPushButton("Cerrar", self.tab_create)
        close_btn.setStyleSheet("background-color:#FF5733; color:white; font-size:16px; padding:5px;")
        close_btn.clicked.connect(self.close_calendar_create)

        def pick_date(date):
            form["fecha_entrega"].setText(date.toString("dd/MM/yyyy"))
            self.close_calendar_create()

        self.calendar_create.clicked.connect(pick_date)

        layout = QVBoxLayout()
        layout.addWidget(self.calendar_create)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)

        self.calendar_container_create = QWidget(self.tab_create)
        self.calendar_container_create.setLayout(layout)

        cx = self.width()//2 - 200
        cy = self.height()//2 - 150
        self.calendar_container_create.setGeometry(cx, cy, 420, 350)

        self.calendar_container_create.show()
        self.calendar_container_create.raise_()

    def close_calendar_create(self):
        if hasattr(self, "calendar_container_create") and self.calendar_container_create:
            self.calendar_container_create.hide()
            self.calendar_container_create = None
            self.calendar_create = None

    def submit_create_mode(self):
        """
        Envía todos los pedidos en la pestaña "Crear".
        """
        if not self.api_url:
            QMessageBox.warning(self, "Error", "No hay URL configurada para Comercial.")
            return

        url = self.api_url
        for i, form in enumerate(self.forms, start=1):
            data = {
                "section": "Comercial",
                "numeroProforma": form["num_proforma"].text(),
                "ejecutivoComercial": form["ejecutivo_comercial"].text(),
                "cliente": form["cliente"].text(),
                "clasificacion": form["clasificacion_cliente"].text(),
                "descripcion": form["descripcion"].text(),
                "cantidadPedido": form["cantidad_pedido"].text(),
                "fechaEntrega": form["fecha_entrega"].text()
            }
            if not all(data.values()):
                QMessageBox.warning(
                    self, "Advertencia",
                    f"Formulario {i} está incompleto."
                )
                return
            try:
                resp = requests.post(url, json=data)
                if resp.status_code != 200:
                    QMessageBox.critical(
                        self, "Error",
                        f"Error al enviar: {resp.text}"
                    )
                    return
            except Exception as e:
                QMessageBox.critical(
                    self, "Error",
                    f"Error al conectar con la API: {e}"
                )
                return

        QMessageBox.information(self, "Éxito", "Todos los pedidos creados exitosamente.")
        self.clear_create_forms()

    def clear_create_forms(self):
        for f in self.forms:
            f["ejecutivo_comercial"].clear()
            f["cliente"].clear()
            f["clasificacion_cliente"].clear()
            f["descripcion"].clear()
            f["cantidad_pedido"].clear()
            f["fecha_entrega"].clear()
        QMessageBox.information(
            self, "Limpieza",
            "Formularios de 'Crear' reseteados."
        )

    # ---------------------------------------------------------------------
    #                         PESTAÑA "EDITAR"
    # ---------------------------------------------------------------------
    def setup_edit_tab(self):
        layout = QVBoxLayout(self.tab_edit)
        combo_layout = QHBoxLayout()
        lbl = QLabel("Proforma a Editar:")
        lbl.setStyleSheet("font-size:14px; font-weight:bold;")

        self.edit_combo_proforma = QComboBox(self.tab_edit)
        self.edit_combo_proforma.setStyleSheet("""
            background-color:white; border:1px solid #000;
            border-radius:5px; padding:5px; font-size:16px; color:#000;
        """)
        self.edit_combo_proforma.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.edit_combo_proforma.currentIndexChanged.connect(self.load_proforma_data_for_edit)
        combo_layout.addWidget(lbl)
        combo_layout.addWidget(self.edit_combo_proforma)
        layout.addLayout(combo_layout)

        self.edit_ejecutivo = QLineEdit(self.tab_edit)
        self.edit_cliente = QLineEdit(self.tab_edit)
        self.edit_clasificacion = QLineEdit(self.tab_edit)
        self.edit_descripcion = QLineEdit(self.tab_edit)
        self.edit_cantidad = QLineEdit(self.tab_edit)

        self.edit_fecha_entrega = QLineEdit(self.tab_edit)
        self.edit_fecha_entrega.setReadOnly(True)
        self.edit_fecha_entrega.setStyleSheet("""
            background-color:white; border:1px solid #000;
            border-radius:5px; padding:5px; font-size:16px; color:#000;
        """)
        self.edit_fecha_entrega.mousePressEvent = self.show_calendar_edit

        for w in [
            self.edit_ejecutivo, self.edit_cliente,
            self.edit_clasificacion, self.edit_descripcion, self.edit_cantidad
        ]:
            w.setStyleSheet("""
                background-color:white; border:1px solid #000;
                border-radius:5px; padding:5px; font-size:16px; color:#000;
            """)

        form_edit = QFormLayout()
        form_edit.addRow("Ejecutivo Comercial:", self.edit_ejecutivo)
        form_edit.addRow("Cliente:", self.edit_cliente)
        form_edit.addRow("Clasificación:", self.edit_clasificacion)
        form_edit.addRow("Descripción:", self.edit_descripcion)
        form_edit.addRow("Cantidad Pedido:", self.edit_cantidad)
        form_edit.addRow("Fecha de Entrega:", self.edit_fecha_entrega)
        layout.addLayout(form_edit)

        edit_button_layout = QHBoxLayout()
        edit_button_layout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )

        save_edit_btn = QPushButton("Guardar Cambios", self.tab_edit)
        save_edit_btn.setStyleSheet("""
            background-color:#4682B4;
            color:white;
            font-size:16px;
            padding:5px;
        """)
        save_edit_btn.clicked.connect(self.submit_edit_mode)
        edit_button_layout.addWidget(save_edit_btn)

        back_button_edit = QPushButton("Volver", self.tab_edit)
        back_button_edit.setStyleSheet("""
            background-color:#FF5733;
            color:white;
            font-weight:bold;
            font-size:16px;
            padding:5px;
        """)
        back_button_edit.clicked.connect(self.go_back)
        edit_button_layout.addWidget(back_button_edit)

        edit_button_layout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        layout.addLayout(edit_button_layout)

    def on_tab_changed(self, index):
        if index == 1:  # "Editar"
            self.load_proformas_for_edit()

    def load_proformas_for_edit(self):
        if not self.api_url:
            QMessageBox.warning(self, "Error", "No hay URL configurada para Comercial.")
            return
        url = f"{self.api_url}?action=getAllProformas"
        try:
            resp = requests.get(url)
            data = resp.json()
            proformas = data.get("proformas", [])
            self.edit_combo_proforma.clear()
            self.edit_combo_proforma.addItem("-- Seleccione Proforma --")
            for p in proformas:
                self.edit_combo_proforma.addItem(p)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Error al cargar proformas: {e}")

    def load_proforma_data_for_edit(self):
        if not self.api_url:
            QMessageBox.warning(self, "Error", "No hay URL configurada para Comercial.")
            return
        idx = self.edit_combo_proforma.currentIndex()
        if idx <= 0:
            return

        proforma = self.edit_combo_proforma.currentText()
        url = f"{self.api_url}?action=getFullProformaData&numeroProforma={proforma}"
        try:
            resp = requests.get(url)
            data = resp.json()
            comercial = data.get("Comercial", [])
            if not comercial:
                QMessageBox.warning(self, "Aviso", "No hay datos comerciales para esta proforma.")
                return
            # [0]=Proforma, [1]=Ejecutivo, [2]=Cliente, [3]=Clasificacion,
            # [4]=Descripcion, [5]=Cantidad, [6]=FechaEntrega
            self.edit_ejecutivo.setText(str(comercial[1]) if len(comercial)>1 else "")
            self.edit_cliente.setText(str(comercial[2]) if len(comercial)>2 else "")
            self.edit_clasificacion.setText(str(comercial[3]) if len(comercial)>3 else "")
            self.edit_descripcion.setText(str(comercial[4]) if len(comercial)>4 else "")
            self.edit_cantidad.setText(str(comercial[5]) if len(comercial)>5 else "")

            fecha_ = str(comercial[6]) if len(comercial)>6 else ""
            fecha_split = fecha_.split("T")[0] if fecha_ else ""
            parts = fecha_split.split("-") if fecha_split else ["","",""]
            if len(parts)==3:
                self.edit_fecha_entrega.setText(f"{parts[2]}/{parts[1]}/{parts[0]}")
            else:
                self.edit_fecha_entrega.setText(fecha_)

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Conexión fallida: {e}")

    def submit_edit_mode(self):
        if not self.api_url:
            QMessageBox.warning(self, "Error", "No hay URL configurada para Comercial.")
            return
        idx = self.edit_combo_proforma.currentIndex()
        if idx <= 0:
            QMessageBox.warning(self, "Aviso", "Seleccione una Proforma para editar.")
            return

        proforma = self.edit_combo_proforma.currentText()
        url = self.api_url
        data = {
            "section": "Comercial",
            "numeroProforma": proforma,
            "ejecutivoComercial": self.edit_ejecutivo.text(),
            "cliente": self.edit_cliente.text(),
            "clasificacion": self.edit_clasificacion.text(),
            "descripcion": self.edit_descripcion.text(),
            "cantidadPedido": self.edit_cantidad.text(),
            "fechaEntrega": self.edit_fecha_entrega.text()
        }
        if not all(data.values()):
            QMessageBox.warning(self, "Advertencia", "Complete todos los campos para editar.")
            return
        try:
            resp = requests.post(url, json=data)
            if resp.status_code != 200:
                QMessageBox.critical(self, "Error", f"Error al enviar en Edit: {resp.text}")
            else:
                QMessageBox.information(self, "Éxito", "Proforma editada correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error de conexión: {e}")

    # Calendario para "Editar"
    def show_calendar_edit(self, event):
        self.close_calendar_edit()
        self.calendar_edit = QCalendarWidget(self.tab_edit)
        self.calendar_edit.setGridVisible(True)
        self.calendar_edit.setFixedSize(400,300)

        close_btn = QPushButton("Cerrar", self.tab_edit)
        close_btn.setStyleSheet("background-color:#FF5733; color:white; font-size:16px; padding:5px;")
        close_btn.clicked.connect(self.close_calendar_edit)

        def pick_date(date):
            self.edit_fecha_entrega.setText(date.toString("dd/MM/yyyy"))
            self.close_calendar_edit()

        self.calendar_edit.clicked.connect(pick_date)

        layout = QVBoxLayout()
        layout.addWidget(self.calendar_edit)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)

        self.calendar_container_edit = QWidget(self.tab_edit)
        self.calendar_container_edit.setLayout(layout)

        cx = self.width()//2 - 200
        cy = self.height()//2 - 150
        self.calendar_container_edit.setGeometry(cx, cy, 420, 350)

        self.calendar_container_edit.show()
        self.calendar_container_edit.raise_()

    def close_calendar_edit(self):
        if hasattr(self, "calendar_container_edit") and self.calendar_container_edit:
            self.calendar_container_edit.hide()
            self.calendar_container_edit = None
            self.calendar_edit = None

    # ---------------------------------------------------------------------
    def go_back(self):
        self.close()
        if self.main_window:
            self.main_window.showFullScreen()

# ------------------------------------------------------------
#   EJEMPLO DE USO
# ------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Si deseas probar pasando la URL:  window = ComercialFormWindow(api_url="...")
    window = ComercialFormWindow()
    window.showFullScreen()
    sys.exit(app.exec_())
