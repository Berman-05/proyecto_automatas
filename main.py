import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt

from logica import normalize_symbols, simplify_expression

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simplificador de Expresiones Booleanas")
        self.setGeometry(100, 100, 600, 500)
        self.init_ui()
        self.expr = ""
        self.steps = []

    def init_ui(self):
        layout = QVBoxLayout()

        self.input_label = QLabel("Ingrese la expresión booleana:")
        self.input_edit = QLineEdit()
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_edit)

        btn_layout = QHBoxLayout()
        self.btn_ingresar = QPushButton("Ingresar expresión")
        self.btn_simplificar = QPushButton("Simplificar paso a paso")
        self.btn_resultado = QPushButton("Mostrar resultado final")
        self.btn_salir = QPushButton("Salir")
        btn_layout.addWidget(self.btn_ingresar)
        btn_layout.addWidget(self.btn_simplificar)
        btn_layout.addWidget(self.btn_resultado)
        btn_layout.addWidget(self.btn_salir)
        layout.addLayout(btn_layout)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(QLabel("Salida:"))
        layout.addWidget(self.output)

        self.setLayout(layout)

        self.btn_ingresar.clicked.connect(self.ingresar_expresion)
        self.btn_simplificar.clicked.connect(self.simplificar_paso)
        self.btn_resultado.clicked.connect(self.mostrar_resultado)
        self.btn_salir.clicked.connect(self.close)

    def ingresar_expresion(self):
        expr = self.input_edit.text()
        try:
            expr_norm = normalize_symbols(expr)
        except Exception as e:
            QMessageBox.critical(self, "Error de validación", str(e))
            return
        self.expr = expr_norm
        self.steps = []
        self.output.clear()
        self.output.append(f"Expresión normalizada: {expr_norm}")

    def simplificar_paso(self):
        if not self.expr:
            QMessageBox.warning(self, "Atención", "Ingrese una expresión válida primero.")
            return
        if not self.steps:
            _, steps = simplify_expression(self.expr)
            self.steps = steps
            self.current_step = 0
        if self.current_step < len(self.steps):
            paso = self.steps[self.current_step]
            self.output.append(
                f"<b>Paso {self.current_step+1}:</b><br>"
                f"<b>Antes:</b> {paso['before']}<br>"
                f"<b>Ley:</b> {paso['law']}<br>"
                f"<b>Después:</b> {paso['after']}<br>"
            )
            self.current_step += 1
        else:
            self.output.append("<i>No hay más pasos.</i>")

    def mostrar_resultado(self):
        if not self.expr:
            QMessageBox.warning(self, "Atención", "Ingrese una expresión válida primero.")
            return
        resultado, steps = simplify_expression(self.expr)
        self.output.append("<b>Resultado final simplificado:</b>")
        self.output.append(f"<b>{resultado}</b>")
        self.output.append("<b>Pasos realizados:</b>")
        for i, paso in enumerate(steps):
            self.output.append(
                f"Paso {i+1}: {paso['before']} → {paso['law']} → {paso['after']}"
            )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())