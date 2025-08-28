import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from logica import normalize_symbols, simplify_expression

class CustomLineEdit(QLineEdit):
    def keyPressEvent(self, event):
        pass

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simplificador de Expresiones Booleanas")
        self.setGeometry(100, 100, 700, 600)
        self.init_ui()
        self.expr = ""
        self.steps = []

    def init_ui(self):
        layout = QVBoxLayout()

        font_label = QFont("Arial", 16)
        font_input = QFont("Arial", 18)
        font_btn = QFont("Arial", 18)
        font_output = QFont("Consolas", 14)

        self.input_label = QLabel("Ingrese la expresión booleana:")
        self.input_label.setFont(font_label)
        self.input_edit = CustomLineEdit()
        self.input_edit.setFont(font_input)
        self.input_edit.setMinimumHeight(40)
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_edit)

        chars_layout = QHBoxLayout()
        for char in ['A', 'B', 'C', 'D', 'E', 'F', '0', '1']:
            btn = QPushButton(char)
            btn.setFont(font_btn)
            btn.setMinimumHeight(50)
            btn.setMinimumWidth(60)
            btn.clicked.connect(lambda _, c=char: self.input_edit.insert(c))
            chars_layout.addWidget(btn)
        btn_del = QPushButton("Eliminar")
        btn_del.setFont(font_btn)
        btn_del.setMinimumHeight(50)
        btn_del.setMinimumWidth(90)
        btn_del.clicked.connect(self.eliminar_caracter)
        chars_layout.addWidget(btn_del)
        layout.addLayout(chars_layout)

        logic_btn_layout = QHBoxLayout()
        self.btn_and = QPushButton("*")
        self.btn_or = QPushButton("+")
        self.btn_not = QPushButton("¬ (NOT)")
        self.btn_paren_open = QPushButton("(")
        self.btn_paren_close = QPushButton(")")
        for btn in [self.btn_and, self.btn_or, self.btn_not, self.btn_paren_open, self.btn_paren_close]:
            btn.setFont(font_btn)
            btn.setMinimumHeight(50)
            btn.setMinimumWidth(90)
            logic_btn_layout.addWidget(btn)
        layout.addLayout(logic_btn_layout)

        self.btn_and.clicked.connect(lambda: self.input_edit.insert("*"))
        self.btn_or.clicked.connect(lambda: self.input_edit.insert("+"))
        self.btn_not.clicked.connect(lambda: self.input_edit.insert("¬"))
        self.btn_paren_open.clicked.connect(lambda: self.input_edit.insert("("))
        self.btn_paren_close.clicked.connect(lambda: self.input_edit.insert(")"))

        btn_layout = QHBoxLayout()
        self.btn_ingresar = QPushButton("Ingresar expresión")
        self.btn_simplificar = QPushButton("Simplificar paso a paso")
        self.btn_resultado = QPushButton("Mostrar resultado final")
        self.btn_salir = QPushButton("Salir")
        for btn in [self.btn_ingresar, self.btn_simplificar, self.btn_resultado, self.btn_salir]:
            btn.setFont(font_btn)
            btn.setMinimumHeight(50)
            btn.setMinimumWidth(120)
            btn_layout.addWidget(btn)
        layout.addLayout(btn_layout)

        self.output = QTextEdit()
        self.output.setFont(font_output)
        self.output.setReadOnly(True)
        self.output.setMinimumHeight(200)
        layout.addWidget(QLabel("Salida:"))
        layout.addWidget(self.output)

        self.setLayout(layout)

        self.btn_ingresar.clicked.connect(self.ingresar_expresion)
        self.btn_simplificar.clicked.connect(self.simplificar_paso)
        self.btn_resultado.clicked.connect(self.mostrar_resultado)
        self.btn_salir.clicked.connect(self.close)

    def eliminar_caracter(self):
        text = self.input_edit.text()
        self.input_edit.setText(text[:-1])

    def ingresar_expresion(self):
        expr = self.input_edit.text().upper()
        try:
            expr_norm = normalize_symbols(expr)
            _, steps = simplify_expression(expr_norm)
        except Exception:
            QMessageBox.warning(self, "Expresión inválida", "La expresión ingresada no es válida.")
            self.input_edit.clear()
            self.expr = ""
            self.steps = []
            return
        self.expr = expr_norm
        self.steps = []
        self.output.clear()
        self.output.append(f"Expresión normalizada: {expr_norm}")

    def simplificar_paso(self):
        if not self.expr:
            QMessageBox.warning(self, "Atención", "Ingrese una expresión válida primero.")
            return
        try:
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
                self.output.append("<i>No hay más pasos.</i>\n")
        except Exception:
            QMessageBox.warning(self, "Expresión inválida", "La expresión ingresada no es válida.")
            self.input_edit.clear()
            self.expr = ""
            self.steps = []

    def mostrar_resultado(self):
        if not self.expr:
            QMessageBox.warning(self, "Ingrese una expresión válida primero")
            return
        self.input_edit.clear()
        try:
            resultado, steps = simplify_expression(self.expr)
            self.output.append("<b>Resultado final simplificado:</b>")
            self.output.append(f"<b>{resultado}</b>")
            self.output.append("<b>Pasos realizados:</b>")
            for i, paso in enumerate(steps):
                self.output.append(
                    f"Paso {i+1}: {paso['before']} → {paso['law']} → {paso['after']}"
                )
        except Exception:
            QMessageBox.warning(self, "La expresión ingresada no es válida")
            self.input_edit.clear()
            self.expr = ""
            self.steps = []

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())