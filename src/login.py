
from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QWidget,
)
from PyQt5.QtGui import QFont

from .core.auth import add_user, load_user
from .main_window import main_menu


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataForge — Log in")
        self.setGeometry(100, 50, 520, 700)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1d2e, stop:0.5 #16213e, stop:1 #0f1117);
            }
            QLabel {
                color: #e4e4e7;
                font-size: 11pt;
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }
            QLabel[title="true"] {
                font-size: 36pt;
                font-weight: 700;
                color: #818cf8;
                padding: 10px;
            }
            QLabel[subtitle="true"] {
                font-size: 13pt;
                color: #a1a5b4;
                padding: 5px;
                font-weight: 400;
            }
            QLineEdit {
                background-color: #1e2139;
                color: #e4e4e7;
                border: 2px solid #3b3f5c;
                border-radius: 10px;
                padding: 10px 16px;
                font-size: 12pt;
                font-weight: 500;
                line-height: 24px;
            }
            QLineEdit:focus {
                border: 2px solid #818cf8;
                background-color: #252842;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #818cf8, stop:1 #6366f1);
                color: #ffffff;
                border: none;
                border-radius: 10px;
                padding: 16px 28px;
                font-weight: 700;
                font-size: 12pt;
                min-height: 24px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #a5b4fc, stop:1 #818cf8);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6366f1, stop:1 #4f46e5);
            }
            QPushButton#secondary {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3b3f5c, stop:1 #2d3142);
                color: #818cf8;
            }
            QPushButton#secondary:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a4f6f, stop:1 #3b3f5c);
                color: #a5b4fc;
            }
        """)
        vbox = QVBoxLayout(self)
        vbox.setSpacing(16)
        vbox.setContentsMargins(60, 60, 60, 60)
        header_layout = QHBoxLayout()
        logo_label = QLabel("🔐")
        logo_label.setFont(QFont("Arial", 48))
        logo_label.setStyleSheet("padding: 0px; margin: 0px;")
        
        self.title_label = QLabel("DataForge")
        self.title_label.setProperty("title", True)
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.title_label.setStyleSheet("padding: 5px; margin: 0px;")
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        vbox.addLayout(header_layout)
        subtitle_label = QLabel("Welcome back to your data workspace")
        subtitle_label.setProperty("subtitle", True)
        vbox.addWidget(subtitle_label)
        vbox.addSpacing(28)
        email_title = QLabel("Email Address")
        email_title.setStyleSheet("color: #a5b4fc; font-weight: 700; padding: 12px 0px 8px 0px; font-size: 12pt; letter-spacing: 0.5px;")
        email_title.setWordWrap(True)
        vbox.addWidget(email_title)
        self.email_label = QLineEdit()
        self.email_label.setPlaceholderText("your.email@gmail.com")
        self.email_label.setMinimumHeight(60)
        self.email_label.setMaximumHeight(60)
        vbox.addWidget(self.email_label)
        vbox.addSpacing(6)
        password_title = QLabel("Password")
        password_title.setStyleSheet("color: #a5b4fc; font-weight: 700; padding: 12px 0px 8px 0px; font-size: 12pt; letter-spacing: 0.5px;")
        password_title.setWordWrap(True)
        vbox.addWidget(password_title)
        self.pasword_label = QLineEdit()
        self.pasword_label.setPlaceholderText("12-character password")
        self.pasword_label.setMinimumHeight(60)
        self.pasword_label.setMaximumHeight(60)
        self.pasword_label.setEchoMode(QLineEdit.Password)
        vbox.addWidget(self.pasword_label)
        vbox.addSpacing(20)
        self.login_button = QPushButton("SIGN IN")
        self.login_button.setMinimumHeight(56)
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        vbox.addWidget(self.login_button)
        vbox.addSpacing(12)
        register_label = QLabel("Don't have an account yet?")
        register_label.setProperty("subtitle", True)
        register_label.setAlignment(Qt.AlignCenter)
        vbox.addWidget(register_label)
        self.register_button = QPushButton("CREATE ACCOUNT")
        self.register_button.setObjectName("secondary")
        self.register_button.setMinimumHeight(56)
        self.register_button.setCursor(Qt.PointingHandCursor)
        self.register_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        vbox.addWidget(self.register_button)
        vbox.addStretch()
        footer = QLabel("Secure Data Analysis Platform")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #666674; font-size: 10pt; padding-top: 10px; font-weight: 500;")
        vbox.addWidget(footer)
        
        self.setLayout(vbox)
        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)

    def login(self):
        email = self.email_label.text().strip()
        password = self.pasword_label.text()
        if not email.endswith("@gmail.com"):
            QMessageBox.warning(self, "Erreur", "enter a valide email")
            return
        if not password:
            QMessageBox.warning(self, "Erreur", "Veuillez fournir un mot de passe")
            return
        if len(password) != 12:
            QMessageBox.warning(self, "Erreur", "Password should be 12 letter")
            return

        if not email or not password:
            QMessageBox.warning(self, "Erreur", "Veuillez fournir un email et mot de passe")
            return

        name = load_user(email, password)
        if name is None:
            QMessageBox.warning(self, "Erreur", "user not found")
        else:
            self.mainmenu = main_menu(name)
            self.mainmenu.show()
            self.hide()

    def register(self):
        self.register_window = register_page(self)
        self.register_window.show()
        self.hide()


class register_page(QWidget):
    def __init__(self, login_window):
        super().__init__()
        self.setWindowTitle("Register — DataForge")
        self.setGeometry(100, 50, 520, 750)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1d2e, stop:0.5 #16213e, stop:1 #0f1117);
            }
            QLabel {
                color: #e4e4e7;
                font-size: 11pt;
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }
            QLabel[title="true"] {
                font-size: 36pt;
                font-weight: 700;
                color: #818cf8;
                padding: 10px;
            }
            QLabel[subtitle="true"] {
                font-size: 13pt;
                color: #a1a5b4;
                padding: 5px;
                font-weight: 400;
            }
            QLineEdit {
                background-color: #1e2139;
                color: #e4e4e7;
                border: 2px solid #3b3f5c;
                border-radius: 10px;
                padding: 10px 16px;
                font-size: 12pt;
                font-weight: 500;
                line-height: 24px;
            }
            QLineEdit:focus {
                border: 2px solid #818cf8;
                background-color: #252842;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #818cf8, stop:1 #6366f1);
                color: #ffffff;
                border: none;
                border-radius: 10px;
                padding: 16px 28px;
                font-weight: 700;
                font-size: 12pt;
                min-height: 24px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #a5b4fc, stop:1 #818cf8);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6366f1, stop:1 #4f46e5);
            }
        """)
        self.login_window = login_window
        vbox2 = QVBoxLayout(self)
        vbox2.setSpacing(16)
        vbox2.setContentsMargins(60, 60, 60, 60)
        header_layout = QHBoxLayout()
        logo_label = QLabel("🔐")
        logo_label.setFont(QFont("Arial", 36))
        logo_label.setStyleSheet("padding: 0px; margin: 0px;")
        
        self.title_label = QLabel("Join DataForge")
        self.title_label.setProperty("title", True)
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.title_label.setStyleSheet("padding: 5px; margin: 0px;")
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        vbox2.addLayout(header_layout)
        subtitle_label = QLabel("Create your secure account today")
        subtitle_label.setProperty("subtitle", True)
        vbox2.addWidget(subtitle_label)
        vbox2.addSpacing(28)
        username_title = QLabel("Username")
        username_title.setStyleSheet("color: #a5b4fc; font-weight: 700; padding: 12px 0px 8px 0px; font-size: 12pt; letter-spacing: 0.5px;")
        username_title.setWordWrap(True)
        vbox2.addWidget(username_title)
        self.user_label = QLineEdit()
        self.user_label.setPlaceholderText("Choose a unique username")
        self.user_label.setMinimumHeight(60)
        self.user_label.setMaximumHeight(60)
        vbox2.addWidget(self.user_label)
        vbox2.addSpacing(6)
        email_title = QLabel("Email Address")
        email_title.setStyleSheet("color: #a5b4fc; font-weight: 700; padding: 12px 0px 8px 0px; font-size: 12pt; letter-spacing: 0.5px;")
        email_title.setWordWrap(True)
        vbox2.addWidget(email_title)
        self.email_label = QLineEdit()
        self.email_label.setPlaceholderText("your.email@gmail.com")
        self.email_label.setMinimumHeight(60)
        self.email_label.setMaximumHeight(60)
        vbox2.addWidget(self.email_label)
        vbox2.addSpacing(6)
        password_title = QLabel("Password")
        password_title.setStyleSheet("color: #a5b4fc; font-weight: 700; padding: 12px 0px 8px 0px; font-size: 12pt; letter-spacing: 0.5px;")
        password_title.setWordWrap(True)
        vbox2.addWidget(password_title)
        self.pasword_label = QLineEdit()
        self.pasword_label.setPlaceholderText("Exactly 12 characters required")
        self.pasword_label.setMinimumHeight(60)
        self.pasword_label.setMaximumHeight(60)
        self.pasword_label.setEchoMode(QLineEdit.Password)
        vbox2.addWidget(self.pasword_label)
        vbox2.addSpacing(20)
        self.register_button = QPushButton("CREATE ACCOUNT")
        self.register_button.setMinimumHeight(56)
        self.register_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.register_button.setCursor(Qt.PointingHandCursor)
        vbox2.addWidget(self.register_button)
        vbox2.addStretch()
        footer = QLabel("Already have an account? Sign in from the login screen")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #666674; font-size: 10pt; padding-top: 10px; font-weight: 500;")
        vbox2.addWidget(footer)
        
        self.setLayout(vbox2)
        self.register_button.clicked.connect(self.try_register)

    def try_register(self):
        name = self.user_label.text().strip()
        email = self.email_label.text().strip()
        password = self.pasword_label.text().strip()
        if not name or not email or not password:
            QMessageBox.warning(self, "Erreur", "All fields are required")
            return
        if not email.endswith("@gmail.com"):
            QMessageBox.warning(self, "Erreur", "Enter a valid Gmail address")
            return
        if len(password) != 12:
            QMessageBox.warning(self, "Erreur", "Password must be exactly 12 characters")
            return
        if add_user(name, password, email):
            self.title_label.setText("Account Created!")
            self.user_label.setEnabled(False)
            self.email_label.setEnabled(False)
            self.pasword_label.setEnabled(False)
            self.register_button.disconnect()
            self.register_button.setText("Back to Login")
            self.register_button.clicked.connect(self.go_to_login)
            QMessageBox.information(self, "Success", "Successfully registered! Click 'Back to Login' to proceed.")
        else:
            QMessageBox.warning(self, "Erreur", "Registration failed (user may already exist)")

    def go_to_login(self):
        self.close()
        self.login_window.show()

