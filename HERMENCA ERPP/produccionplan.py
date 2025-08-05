import sys
import os
import requests
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QTableWidget,
    QLabel, QTabWidget, QWidget, QPushButton, QHBoxLayout, QMessageBox,
    QTableWidgetItem
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from pathlib import Path

class ProductionPlanerWindow(QMainWindow):
    def __init__(self, parent=None, api_url=""):
        super().__init__(parent)
        self.api_url = api_url  # URL recibida

        self.setWindowTitle("Plan de Producción Semanal")
        self.showFullScreen()

        # Fecha de referencia (lunes de la semana actual)
        self.current_monday = QDate.currentDate().addDays(
            -(QDate.currentDate().dayOfWeek() - 1)
        )

        # Widget de pestañas
        self.tabs = QTabWidget()

        # Pestaña "Plan de Producción"
        self.tab_weekly_schedule = QWidget()
        self.setup_weekly_schedule_tab()
        self.tabs.addTab(self.tab_weekly_schedule, "Plan de Producción")

        # Botón "Volver"
        self.back_button = QPushButton("Volver")
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #FF5733;
                color: white;
                font-size: 16px;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #E74C3C;
            }
        """)
        self.back_button.setFixedSize(100, 40)
        self.back_button.clicked.connect(self.go_back_to_main)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.back_button, alignment=Qt.AlignLeft)
        main_layout.addWidget(self.tabs)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Diccionario para datos de procesos/tareas
        self.process_task_data = {}

        # Cargar datos desde la API
        self.load_process_data()

    def setup_weekly_schedule_tab(self):
        layout = QVBoxLayout()

        # Selector de semana
        week_selector_layout = QHBoxLayout()

        self.prev_week_button = QPushButton("Semana Anterior")
        self.prev_week_button.setStyleSheet("""
            QPushButton {
                background-color: #63c8aa;
                color: white;
                font-size: 14px;
                border-radius: 8px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #51a68b;
            }
        """)

        self.next_week_button = QPushButton("Semana Siguiente")
        self.next_week_button.setStyleSheet("""
            QPushButton {
                background-color: #63c8aa;
                color: white;
                font-size: 14px;
                border-radius: 8px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #51a68b;
            }
        """)

        self.prev_week_button.clicked.connect(self.show_previous_week)
        self.next_week_button.clicked.connect(self.show_next_week)

        self.week_label = QLabel()
        self.week_label.setAlignment(Qt.AlignCenter)
        self.week_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.update_week_label()

        week_selector_layout.addWidget(self.prev_week_button)
        week_selector_layout.addWidget(self.week_label)
        week_selector_layout.addWidget(self.next_week_button)
        layout.addLayout(week_selector_layout)

        # Etiqueta de la tabla
        label = QLabel("Plan de Producción Semanal por Proceso:")
        label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(label)

        # 6 columnas: Proceso, Lunes..Viernes
        self.weekly_schedule_table = QTableWidget(0, 6)
        self.weekly_schedule_table.setHorizontalHeaderLabels([
            "Proceso", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes"
        ])
        self.weekly_schedule_table.horizontalHeader().setStretchLastSection(True)
        self.weekly_schedule_table.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )

        # Word wrap
        self.weekly_schedule_table.setWordWrap(True)

        # Estilos
        self.weekly_schedule_table.setStyleSheet("""
            QHeaderView::section {
                background-color: #005BAC;
                color: white;
                font-weight: bold;
                font-size: 12pt;
                padding: 6px;
                border-radius: 5px;
                margin: 2px;
            }
            QTableWidget {
                background-color: #FFFFFF;
                gridline-color: #A9D1F7;
            }
        """)

        layout.addWidget(self.weekly_schedule_table)

        # Botón "Exportar a PDF"
        self.export_pdf_button = QPushButton("Exportar a PDF")
        self.export_pdf_button.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                font-size: 14px;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.export_pdf_button.clicked.connect(self.export_to_pdf)
        layout.addWidget(self.export_pdf_button, alignment=Qt.AlignRight)

        self.tab_weekly_schedule.setLayout(layout)

    def export_to_pdf(self):
        try:
            pdf_file_name = f"Plan_Produccion_Semanal_{self.current_monday.toString('dd_MM_yyyy')}.pdf"
            desktop_path = Path.home() / "Desktop"
            pdf_file = desktop_path / pdf_file_name

            doc = SimpleDocTemplate(str(pdf_file), pagesize=A4)
            elements = []

            styles = getSampleStyleSheet()
            title_style = styles['Title']
            header_style = styles['Heading4']
            cell_style = styles['BodyText']

            title = Paragraph("Plan de Producción Semanal", title_style)
            elements.append(title)

            data = []
            headers = ["Proceso", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
            data.append([Paragraph(h, header_style) for h in headers])

            row_count = self.weekly_schedule_table.rowCount()
            for row in range(row_count):
                row_data = []

                cell_widget = self.weekly_schedule_table.cellWidget(row, 0)
                process_name = cell_widget.text() if cell_widget else ""
                row_data.append(Paragraph(process_name, cell_style))

                for col in range(1, 6):
                    cw = self.weekly_schedule_table.cellWidget(row, col)
                    cell_text = cw.text() if cw else ""
                    row_data.append(Paragraph(cell_text, cell_style))

                data.append(row_data)

            from reportlab.platypus import Table, TableStyle
            from reportlab.lib import colors

            table = Table(data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#005BAC")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            elements.append(table)
            doc.build(elements)

            QMessageBox.information(
                self, "PDF Generado",
                f"El PDF ha sido generado en el escritorio: {pdf_file}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar el PDF: {str(e)}")

    def load_process_data(self):
        if not self.api_url:
            QMessageBox.warning(self, "Error", "No hay URL configurada para el Plan de Producción.")
            return

        try:
            response = requests.get(f'{self.api_url}?action=loadOTs')
            if response.status_code == 200:
                self.process_task_data = response.json()
                self.organize_data_by_week()
            else:
                QMessageBox.warning(self, "Error",
                    f"Error al cargar los procesos: {response.status_code}"
                )
        except Exception as e:
            QMessageBox.critical(self, "Error",
                f"Error al conectar con la API: {str(e)}"
            )

    def organize_data_by_week(self):
        if not self.process_task_data:
            QMessageBox.warning(self, "Advertencia",
                "No se recibieron datos de OTs o el formato es incorrecto.")
            return

        row_count = len(self.process_task_data)
        self.weekly_schedule_table.setRowCount(row_count)
        # Ocultar encabezado vertical
        self.weekly_schedule_table.verticalHeader().setVisible(False)

        dates = [
            self.current_monday.addDays(i).toString("yyyy-MM-dd")
            for i in range(5)
        ]

        for row, (process, ots) in enumerate(self.process_task_data.items()):
            # col 0 => "Proceso"
            label_process = QLabel(process)
            label_process.setAlignment(Qt.AlignCenter)
            label_process.setStyleSheet("""
                background-color: #005BAC;
                color: white;
                border: 1px solid #004080;
                border-radius: 8px;
                font-weight: bold;
                padding: 6px;
            """)
            self.weekly_schedule_table.setCellWidget(row, 0, label_process)

            task_by_date = {}
            for ot_data in ots:
                ot_number = str(ot_data[0])
                assigned_date = ot_data[1][:10]
                if assigned_date != "No asignada":
                    if assigned_date not in task_by_date:
                        task_by_date[assigned_date] = []
                    task_by_date[assigned_date].append(ot_number)

            for col, date in enumerate(dates, start=1):
                ots_for_date = task_by_date.get(date, ["Sin asignación"])
                cell_text = "\n".join([f"OT: {ot}" for ot in ots_for_date])
                cell_label = QLabel(cell_text)
                cell_label.setAlignment(Qt.AlignTop)
                cell_label.setWordWrap(True)
                self.weekly_schedule_table.setCellWidget(row, col, cell_label)

        # Ajustar alturas
        self.weekly_schedule_table.resizeRowsToContents()

    def show_previous_week(self):
        self.current_monday = self.current_monday.addDays(-7)
        self.update_week_label()
        self.organize_data_by_week()

    def show_next_week(self):
        self.current_monday = self.current_monday.addDays(7)
        self.update_week_label()
        self.organize_data_by_week()

    def update_week_label(self):
        end_of_week = self.current_monday.addDays(4)
        self.week_label.setText(
            f"Semana del {self.current_monday.toString('dd/MM/yyyy')} "
            f"al {end_of_week.toString('dd/MM/yyyy')}"
        )

    def go_back_to_main(self):
        """Regresar a la ventana principal en lugar de cerrar la app."""
        if self.parent():
            self.parent().showFullScreen()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Ejemplo: window = ProductionPlanerWindow(api_url="https://script.google.com/macros/s/TU-ENLACE/exec")
    window = ProductionPlanerWindow()
    window.showFullScreen()
    sys.exit(app.exec_())
