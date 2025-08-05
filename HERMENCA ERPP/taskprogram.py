import sys
import requests
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QListWidget,
    QListWidgetItem, QCalendarWidget, QAbstractItemView, QComboBox, QHBoxLayout,
    QMessageBox, QPushButton, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMimeData
from PyQt5.QtGui import QDrag

class LoadDataThread(QThread):
    data_loaded = pyqtSignal(dict)

    def __init__(self, api_url=""):
        super().__init__()
        self.api_url = api_url

    def run(self):
        """Hilo para cargar datos desde la API sin bloquear la UI."""
        if not self.api_url:
            print("No hay URL configurada para cargar OTs en TaskWindow.")
            return

        try:
            response = requests.get(f'{self.api_url}?action=loadOTs')
            if response.status_code == 200:
                data = response.json()
                self.data_loaded.emit(data)
            else:
                print(f"Error al cargar la lista de procesos: {response.status_code}")
        except Exception as e:
            print(f"Error al conectar con la API: {str(e)}")

class TaskWindow(QMainWindow):
    def __init__(self, parent=None, api_url=""):
        super().__init__(parent)
        self.api_url = api_url  # En lugar de BASE_URL

        self.setWindowTitle("Programación de Tareas de Producción")
        self.setGeometry(100, 100, 1200, 600)

        # Diccionario para almacenar procesos y las OTs asociadas
        self.process_ot_data = {}
        self.tasks_by_date = {}

        # Layout principal vertical
        main_layout = QVBoxLayout()

        # Botón "Volver"
        self.back_button = QPushButton("Volver", self)
        self.back_button.setStyleSheet("background-color: #FF5733; color: white; font-weight: bold;")
        self.back_button.setFixedSize(100, 40)
        self.back_button.clicked.connect(self.return_to_dashboard)
        main_layout.addWidget(self.back_button)

        # Layout horizontal para widgets de selección
        content_layout = QHBoxLayout()
        left_layout = QVBoxLayout()

        # QFrame con borde gris
        frame = QFrame()
        frame.setStyleSheet("QFrame { border: 1px solid gray; border-radius: 5px; }")
        frame_layout = QVBoxLayout(frame)

        self.process_label = QLabel("SELECCIONE UN PROCESO:")
        self.process_label.setStyleSheet("""
            font-family: 'Arial';
            font-size: 14px;
            color: white;
            background-color: #3E92CC;
            font-weight: bold;
            padding: 5px;
            border-radius: 4px;
        """)
        self.process_label.setAlignment(Qt.AlignCenter)

        self.process_combo = QComboBox()
        self.process_combo.setStyleSheet("""
            QComboBox {
                background-color: lightblue;
                font-family: 'Arial';
                font-size: 14px;
            }
            QComboBox QAbstractItemView {
                font-family: 'Arial';
                font-size: 14px;
            }
        """)
        self.process_combo.addItem("Cargando...")
        self.process_combo.setEnabled(False)
        self.process_combo.currentIndexChanged.connect(self.load_ots_for_process)

        self.ot_list = QListWidget()
        self.ot_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ot_list.setDragEnabled(True)
        self.ot_list.setDefaultDropAction(Qt.MoveAction)
        self.ot_list.startDrag = self.start_drag_ot_list

        ots_label = QLabel("OTS DISPONIBLES:")
        ots_label.setStyleSheet("""
            font-family: 'Arial';
            font-size: 14px;
            color: white;
            background-color: #63c8aa ;
            padding: 5px;
            border-radius: 4px;
            font-weight: bold;
        """)

        frame_layout.addWidget(self.process_label)
        frame_layout.addWidget(self.process_combo)
        frame_layout.addWidget(ots_label)
        frame_layout.addWidget(self.ot_list)

        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.load_tasks_for_date)
        frame_layout.addWidget(QLabel("Seleccionar fecha:"))
        frame_layout.addWidget(self.calendar)
        self.calendar.setStyleSheet("""
            QCalendarWidget QAbstractItemView {
                selection-background-color: #4CAF50;
                selection-color: white;
                background-color: white;
                color: black;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: gray;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #3E92CC;
            }
            QCalendarWidget QToolButton {
                background-color: #3E92CC;
                color: white;
                font-weight: bold;
            }
            QCalendarWidget QToolButton#qt_calendar_prevmonth,
            QCalendarWidget QToolButton#qt_calendar_nextmonth {
                background-color: #3E92CC;
            }
        """)

        self.task_assign_frame = TaskAssignListWidget(self)
        ots_asignadas = QLabel("OTS ASIGNADAS:                  [ ARRASTE AQUI PARA ASIGNAR... (↓) ]")
        ots_asignadas.setStyleSheet("""
            font-family: 'Arial';
            font-size: 14px;
            color: white;
            background-color: #63c8aa ;
            padding: 5px;
            border-radius: 4px;
            font-weight: bold;
        """)
        frame_layout.addWidget(ots_asignadas)
        frame_layout.addWidget(self.task_assign_frame)

        left_layout.addWidget(frame)
        content_layout.addLayout(left_layout)
        main_layout.addLayout(content_layout)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        # Cargar datos
        self.load_process_data()

    def load_process_data(self):
        """Iniciar hilo para cargar los datos de la API."""
        if not self.api_url:
            QMessageBox.warning(self, "Error", "No hay URL configurada para Programación de Tareas.")
            return

        self.thread = LoadDataThread(api_url=self.api_url)
        self.thread.data_loaded.connect(self.process_data)
        self.thread.start()

    def process_data(self, data):
        """Procesar los datos cargados en la interfaz."""
        if not data:
            QMessageBox.warning(self, "Error", "No se recibieron datos desde la API.")
            return

        current_process = self.process_combo.currentText()

        self.process_combo.setEnabled(True)
        self.process_ot_data = data
        self.process_combo.clear()
        self.process_combo.addItems(self.process_ot_data.keys())

        if current_process in self.process_ot_data:
            index = self.process_combo.findText(current_process)
            self.process_combo.setCurrentIndex(index)

        self.tasks_by_date.clear()
        for process, ots in self.process_ot_data.items():
            for ot_data in ots:
                if len(ot_data) > 1 and ot_data[1] != "No asignada":
                    ot = ot_data[0]
                    assigned_date = ot_data[1][:10]
                    if assigned_date not in self.tasks_by_date:
                        self.tasks_by_date[assigned_date] = []
                    self.tasks_by_date[assigned_date].append({"ot": ot, "process": process})

        self.load_ots_for_process()

    def load_ots_for_process(self):
        selected_process = self.process_combo.currentText()
        ots = self.process_ot_data.get(selected_process, [])
        self.ot_list.clear()

        for ot_data in ots:
            if isinstance(ot_data, list) and len(ot_data) > 1 and ot_data[1] != "No asignada":
                continue
            ot = ot_data[0] if isinstance(ot_data, list) and len(ot_data) > 0 else ot_data
            item_text = f"OT: {ot}"
            list_item = QtWidgets.QListWidgetItem(item_text)
            self.ot_list.addItem(list_item)

    def load_tasks_for_date(self, date):
        selected_date = date.toString("yyyy-MM-dd")
        self.task_assign_frame.clear()
        if selected_date in self.tasks_by_date:
            for task_info in self.tasks_by_date[selected_date]:
                self.add_task_widget(task_info['ot'], selected_date, task_info['process'])
        else:
            self.task_assign_frame.clear()

    def assign_ot_to_selected_date(self, ot_number):
        selected_process = self.process_combo.currentText()
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        self.send_task_to_api(ot_number, selected_process, selected_date)

    def add_task_widget(self, ot, date, process):
        item_text = f"{process}: OT {ot}"

        task_widget = QWidget()
        task_layout = QHBoxLayout()

        label = QLabel(item_text)
        delete_button = QPushButton("X")
        delete_button.setFixedSize(24, 24)
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #ff4d4d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e60000;
            }
            QPushButton:pressed {
                background-color: #cc0000;
            }
        """)
        delete_button.clicked.connect(lambda: self.remove_assigned_task(ot, process, date))

        task_layout.addWidget(label)
        task_layout.addWidget(delete_button)
        task_layout.setContentsMargins(0, 0, 0, 0)
        task_layout.setSpacing(10)
        task_widget.setLayout(task_layout)

        list_item = QListWidgetItem(self.task_assign_frame)
        list_item.setSizeHint(task_widget.sizeHint())
        self.task_assign_frame.addItem(list_item)
        self.task_assign_frame.setItemWidget(list_item, task_widget)

    def remove_assigned_task(self, ot, process, date):
        """Eliminar la fecha asignada a una OT y recargar la interfaz."""
        if not self.api_url:
            QMessageBox.warning(self, "Error", "No hay URL configurada para Programación de Tareas.")
            return

        url = f'{self.api_url}?action=remove&process={process}&ot={ot}'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                self.load_process_data()
                self.load_tasks_for_date(self.calendar.selectedDate())
            else:
                print(f"Error al eliminar la fecha: {response.status_code}")
        except Exception as e:
            print(f"Error al conectar con la API: {str(e)}")

    def send_task_to_api(self, ot, process, date):
        """Enviar una tarea a la API y actualizar la interfaz."""
        if not self.api_url:
            QMessageBox.warning(self, "Error", "No hay URL configurada para Programación de Tareas.")
            return

        url = f'{self.api_url}?action=assign&process={process}&ot={ot}&date={date}'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                self.add_task_to_schedule(ot, date, process)
                self.load_process_data()
                self.load_tasks_for_date(self.calendar.selectedDate())
            else:
                print(f"Error al asignar la OT: {response.status_code}")
        except Exception as e:
            print(f"Error al conectar con la API para asignar la tarea: {str(e)}")

    def add_task_to_schedule(self, ot, date, process):
        if date not in self.tasks_by_date:
            self.tasks_by_date[date] = []
        self.tasks_by_date[date].append({"ot": ot, "process": process})
        self.add_task_widget(ot, date, process)

    def start_drag_ot_list(self, supportedActions):
        item = self.ot_list.currentItem()
        if item:
            mime_data = QMimeData()
            mime_data.setText(item.text())
            drag = QDrag(self.ot_list)
            drag.setMimeData(mime_data)
            drag.exec_(Qt.MoveAction)

    def return_to_dashboard(self):
        if self.parent():
            self.parent().showFullScreen()
        self.close()


class TaskAssignListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.parent_window = parent

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        ot_text = event.mimeData().text()
        ot_number = ot_text.split(": ")[1]
        self.parent_window.assign_ot_to_selected_date(ot_number)
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskWindow()
    window.showFullScreen()
    sys.exit(app.exec_())
