import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect
from PyQt5.QtGui import QFont

class GlowButton(QPushButton):
    def __init__(self, text, color):
        super().__init__(text)
        self.base_color = color
        self.hover_color = "#ffffff"
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 14px 20px;
                border-radius: 14px;
                font-size: 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #333333;
            }}
        """)

        # Animation on hover
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(150)

    def enterEvent(self, event):
        rect = self.geometry()
        self.anim.stop()
        self.anim.setStartValue(rect)
        self.anim.setEndValue(QRect(rect.x()-3, rect.y()-3, rect.width()+6, rect.height()+6))
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        rect = self.geometry()
        self.anim.stop()
        self.anim.setStartValue(rect)
        self.anim.setEndValue(QRect(rect.x()+3, rect.y()+3, rect.width()-6, rect.height()-6))
        self.anim.start()
        super().leaveEvent(event)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("✨ Razzle Dazzle UI ✨")
        self.setFixedSize(300, 220)
        self.setStyleSheet("background-color: #222222;")

        # Title
        self.title = QLabel("Control Panel")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("color: white; font-size: 20px;")
        self.title.setFont(QFont("Arial", 18))

        # Buttons
        self.start_btn = GlowButton("Start", "#28a745")
        self.stop_btn  = GlowButton("Stop", "#dc3545")

        # Connect actions
        self.start_btn.clicked.connect(lambda: print("✨ Start pressed"))
        self.stop_btn.clicked.connect(lambda: print("🛑 Stop pressed"))

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addSpacing(15)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
