"""
Login page for user authentication.
"""
import os
import sys
import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QFormLayout, QDialog, QMessageBox,
    QGroupBox, QCheckBox, QApplication, QFrame
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon

# Add Security module to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Security.security.authentification import verify_user_credentials
from Security.security.user_data_manager import add_user, get_user, update_user, set_temporary_password
from Security.security.logs import log_action
from Security.security.otp import generate_otp_secret, verify_otp
from Security.security.notifications import send_temporary_password_email
from Security.security.password import hash_password, generate_strong_password

class SetupKeyDialog(QDialog):
    """Dialog for displaying 2FA setup key."""
    def __init__(self, parent=None, otp_secret=None, username=None, email=None):
        super().__init__(parent)
        self.setWindowTitle("2FA Setup - Secret Key")
        self.setMinimumWidth(500)
        self.setMinimumHeight(350)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title_label = QLabel("Two-Factor Authentication Setup")
        title_label.setObjectName("title-label")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        instructions = QLabel(
            "To set up two-factor authentication, enter this secret key in your authenticator app "
            "(Google Authenticator, Microsoft Authenticator, Authy, etc.)."
        )
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)
        
        # Generate URI for manual entry
        import pyotp
        totp = pyotp.TOTP(otp_secret)
        provisioning_uri = totp.provisioning_uri(name=email, issuer_name="Automaton App")
        
        uri_container = QWidget()
        uri_container.setObjectName("uri-container")
        uri_container.setStyleSheet("""
            #uri-container {
                background-color: #f8f9fa;
                border-radius: 6px;
                border: 1px solid #e0e0e0;
            }
        """)
        uri_layout = QVBoxLayout(uri_container)
        
        uri_label = QLabel("You can manually add this URI to your authenticator app:")
        uri_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        uri_layout.addWidget(uri_label)
        
        uri_display = QLabel(provisioning_uri)
        uri_display.setWordWrap(True)
        uri_display.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        uri_display.setStyleSheet("background-color: white; padding: 10px; border-radius: 4px; border: 1px solid #ddd;")
        uri_layout.addWidget(uri_display)
        
        layout.addWidget(uri_container)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #e0e0e0;")
        layout.addWidget(separator)
        
        key_container = QWidget()
        key_container.setObjectName("key-container")
        key_container.setStyleSheet("""
            #key-container {
                background-color: #e8f4fc;
                border-radius: 6px;
                border: 1px solid #bde0f7;
            }
        """)
        key_layout = QVBoxLayout(key_container)
        
        manual_key_label = QLabel("Or enter this secret key manually:")
        manual_key_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        manual_key_label.setAlignment(Qt.AlignCenter)
        key_layout.addWidget(manual_key_label)
        
        secret_key_label = QLabel(otp_secret)
        secret_key_label.setAlignment(Qt.AlignCenter)
        secret_key_font = QFont("Courier New", 16, QFont.Bold)
        secret_key_label.setFont(secret_key_font)
        secret_key_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        secret_key_label.setStyleSheet("padding: 15px; letter-spacing: 2px;")
        key_layout.addWidget(secret_key_label)
        
        layout.addWidget(key_container)
        
        copy_button = QPushButton("Copy Secret Key")
        copy_button.setIcon(QIcon.fromTheme("edit-copy"))
        copy_button.clicked.connect(lambda: self._copy_to_clipboard(otp_secret))
        layout.addWidget(copy_button)
        
        close_button = QPushButton("Close")
        close_button.setMinimumWidth(100)
        close_button.setMinimumHeight(35)
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
    
    def _copy_to_clipboard(self, text):
        """Copy text to clipboard and show confirmation."""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        QMessageBox.information(self, "Copied", "Secret key copied to clipboard!")

class OTPDialog(QDialog):
    """Dialog for 2FA authentication with OTP."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Two-Factor Authentication")
        self.setMinimumWidth(300)
        self.result_code = None
        
        layout = QVBoxLayout(self)
        
        instructions = QLabel("Enter the verification code from your authenticator app:")
        layout.addWidget(instructions)
        
        self.otp_input = QLineEdit()
        self.otp_input.setPlaceholderText("6-digit code")
        self.otp_input.setMaxLength(6)
        layout.addWidget(self.otp_input)
        
        buttons_layout = QHBoxLayout()
        self.verify_button = QPushButton("Verify")
        self.verify_button.setMinimumWidth(100)
        self.verify_button.setMinimumHeight(35)
        self.verify_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumWidth(100)
        self.cancel_button.setMinimumHeight(35)
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.verify_button)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
    
    def get_code(self):
        return self.otp_input.text()

class ChangePasswordDialog(QDialog):
    """Dialog for changing password."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Change Password")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        form_layout.addRow("New Password:", self.new_password)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Confirm Password:", self.confirm_password)
        
        layout.addLayout(form_layout)
        
        req_group = QGroupBox("Password Requirements")
        req_layout = QVBoxLayout(req_group)
        req_layout.addWidget(QLabel("• At least 8 characters"))
        req_layout.addWidget(QLabel("• At least one uppercase letter"))
        req_layout.addWidget(QLabel("• At least one lowercase letter"))
        req_layout.addWidget(QLabel("• At least one number"))
        req_layout.addWidget(QLabel("• At least one special character"))
        layout.addWidget(req_group)
        
        buttons_layout = QHBoxLayout()
        self.change_button = QPushButton("Change Password")
        self.change_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.change_button)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
    
    def get_passwords(self):
        return self.new_password.text(), self.confirm_password.text()

class RegisterDialog(QDialog):
    """Dialog for registering a new user."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register New User")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        form_layout.addRow("Username:", self.username_input)
        
        self.email_input = QLineEdit()
        form_layout.addRow("Email:", self.email_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Password:", self.password_input)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Confirm Password:", self.confirm_password_input)
        
        self.enable_2fa = QCheckBox("Enable Two-Factor Authentication")
        self.enable_2fa.setChecked(True)
        form_layout.addRow("", self.enable_2fa)
        
        layout.addLayout(form_layout)
        
        req_group = QGroupBox("Password Requirements")
        req_layout = QVBoxLayout(req_group)
        req_layout.addWidget(QLabel("• At least 8 characters"))
        req_layout.addWidget(QLabel("• At least one uppercase letter"))
        req_layout.addWidget(QLabel("• At least one lowercase letter"))
        req_layout.addWidget(QLabel("• At least one number"))
        req_layout.addWidget(QLabel("• At least one special character"))
        layout.addWidget(req_group)
        
        self.generate_button = QPushButton("Generate Strong Password")
        self.generate_button.setMinimumWidth(200)
        self.generate_button.setMinimumHeight(35)
        self.generate_button.clicked.connect(self.generate_password)
        layout.addWidget(self.generate_button)
        
        buttons_layout = QHBoxLayout()
        self.register_button = QPushButton("Register")
        self.register_button.setMinimumWidth(120)
        self.register_button.setMinimumHeight(35)
        self.register_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumWidth(120)
        self.cancel_button.setMinimumHeight(35)
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.register_button)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
    
    def generate_password(self):
        """Generate a strong password and set it in both password fields."""
        password = generate_strong_password()
        self.password_input.setText(password)
        self.confirm_password_input.setText(password)
        QMessageBox.information(self, "Password Generated", 
                               f"A strong password has been generated: {password}\n\nPlease make sure to save this password in a secure location.")
    
    def get_registration_data(self):
        return {
            'username': self.username_input.text(),
            'email': self.email_input.text(),
            'password': self.password_input.text(),
            'confirm_password': self.confirm_password_input.text(),
            'enable_2fa': self.enable_2fa.isChecked()
        }

class ForgotPasswordDialog(QDialog):
    """Dialog for resetting password."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reset Password")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        
        instructions = QLabel("Enter your username and email to receive a temporary password:")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        form_layout.addRow("Username:", self.username_input)
        
        self.email_input = QLineEdit()
        form_layout.addRow("Email:", self.email_input)
        
        layout.addLayout(form_layout)
        
        buttons_layout = QHBoxLayout()
        self.reset_button = QPushButton("Reset Password")
        self.reset_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
    
    def get_reset_data(self):
        return self.username_input.text(), self.email_input.text()

class LoginPage(QWidget):
    """
    Page for user authentication.
    """
    def __init__(self, parent=None):
        """
        Initialize the page.
        """
        super().__init__(parent)
        self.parent = parent
        self.current_user = None
        self.setup_ui()
    
    def setup_ui(self):
        """
        Set up the UI elements for the page.
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)
        
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel("Automaton App")
        title_label.setObjectName("title-label")
        title_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(title_label)
        
        desc_label = QLabel("Please login to access the application")
        desc_label.setObjectName("welcome-label")
        desc_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(desc_label)
        
        layout.addWidget(logo_container)
        
        form_container = QWidget()
        form_container.setObjectName("form-container")
        form_container.setStyleSheet("""
            #form-container {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        form_internal_layout = QFormLayout()
        form_internal_layout.setSpacing(10)
        form_internal_layout.setLabelAlignment(Qt.AlignLeft)
        form_internal_layout.setFormAlignment(Qt.AlignLeft)
        
        username_label = QLabel("Username")
        username_label.setFont(QFont("Segoe UI", 10))
        self.username_input = QLineEdit()
        self.username_input.setMinimumHeight(30)
        self.username_input.setPlaceholderText("Enter your username")
        form_internal_layout.addRow(username_label, self.username_input)
        
        password_label = QLabel("Password")
        password_label.setFont(QFont("Segoe UI", 10))
        self.password_input = QLineEdit()
        self.password_input.setMinimumHeight(30)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter your password")
        form_internal_layout.addRow(password_label, self.password_input)
        
        form_layout.addLayout(form_internal_layout)
        
        self.login_button = QPushButton("Login")
        self.login_button.setMinimumHeight(40)
        self.login_button.setMinimumWidth(150)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 12pt;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.login_button.clicked.connect(self.login)
        form_layout.addWidget(self.login_button)
        
        layout.addWidget(form_container)
        
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        self.register_button = QPushButton("Register")
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3498db;
                border: none;
                text-decoration: underline;
                font-weight: normal;
            }
            QPushButton:hover {
                color: #2980b9;
                background-color: transparent;
            }
        """)
        self.register_button.clicked.connect(self.show_register)
        buttons_layout.addWidget(self.register_button)
        
        buttons_layout.addStretch()
        
        self.forgot_button = QPushButton("Forgot Password")
        self.forgot_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3498db;
                border: none;
                text-decoration: underline;
                font-weight: normal;
            }
            QPushButton:hover {
                color: #2980b9;
                background-color: transparent;
            }
        """)
        self.forgot_button.clicked.connect(self.show_forgot_password)
        buttons_layout.addWidget(self.forgot_button)
        
        layout.addWidget(buttons_container)
        
        layout.addStretch()
    
    def login(self):
        """
        Handle login button click.
        """
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Login Error", "Please enter both username and password.")
            return
        
        try:
            auth_result = verify_user_credentials(username, password)
            status = auth_result.get("status")
            user = auth_result.get("user")
            
            if status == "must_change_password":
                self.show_change_password(username)
                return
            
            if status == "success":
                if user.get("require_2fa", False) and user.get("otp_secret"):
                    if not self.verify_otp(username):
                        return
                
                log_action(username, "login_success")
                
                update_user(username, "login_count", user.get("login_count", 0) + 1)
                update_user(username, "last_login", int(time.time()))
                
                self.current_user = user
                
                QMessageBox.information(self, "Login Successful", f"Welcome, {username}!")
                if self.parent:
                    self.parent.on_login_success(user)
                
        except ValueError as e:
            QMessageBox.warning(self, "Login Failed", str(e))
            log_action(username, "login_failed", str(e))
    
    def verify_otp(self, username):
        """
        Verify OTP code for 2FA.
        """
        otp_dialog = OTPDialog(self)
        if otp_dialog.exec_() == QDialog.Accepted:
            otp_code = otp_dialog.get_code()
            try:
                verify_otp(username, otp_code)
                return True
            except ValueError as e:
                QMessageBox.warning(self, "2FA Verification Failed", str(e))
                log_action(username, "otp_failed", str(e))
                return False
        return False
    
    def show_change_password(self, username):
        """
        Show dialog to change password after temporary password login.
        """
        dialog = ChangePasswordDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_password, confirm_password = dialog.get_passwords()
            
            if new_password != confirm_password:
                QMessageBox.warning(self, "Password Error", "Passwords do not match.")
                return self.show_change_password(username)
            
            if len(new_password) < 8 or not any(c.isupper() for c in new_password) or \
               not any(c.islower() for c in new_password) or not any(c.isdigit() for c in new_password) or \
               not any(c in "!@#$%^&*()-_=+[]}{;:,.<>?" for c in new_password):
                QMessageBox.warning(self, "Password Error", "Password does not meet complexity requirements.")
                return self.show_change_password(username)
            
            try:
                update_user(username, "password_hash", hash_password(new_password).decode())
                update_user(username, "must_change_password", False)
                update_user(username, "temp_password_created_at", None)
                
                QMessageBox.information(self, "Password Changed", "Your password has been changed successfully. Please login with your new password.")
                log_action(username, "password_changed")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
                log_action(username, "password_change_failed", str(e))
    
    def show_register(self):
        """
        Show dialog to register a new user.
        """
        dialog = RegisterDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            reg_data = dialog.get_registration_data()
            
            if not reg_data['username'] or not reg_data['email'] or not reg_data['password']:
                QMessageBox.warning(self, "Registration Error", "All fields are required.")
                return self.show_register()
            
            if reg_data['password'] != reg_data['confirm_password']:
                QMessageBox.warning(self, "Registration Error", "Passwords do not match.")
                return self.show_register()
            
            if len(reg_data['password']) < 8 or not any(c.isupper() for c in reg_data['password']) or \
               not any(c.islower() for c in reg_data['password']) or not any(c.isdigit() for c in reg_data['password']) or \
               not any(c in "!@#$%^&*()-_=+[]}{;:,.<>?" for c in reg_data['password']):
                QMessageBox.warning(self, "Registration Error", "Password does not meet complexity requirements.")
                return self.show_register()
            
            if get_user(reg_data['username']):
                QMessageBox.warning(self, "Registration Error", "Username already exists.")
                return self.show_register()
            
            try:
                add_user(
                    reg_data['username'], 
                    reg_data['password'], 
                    reg_data['email'],
                    require_2fa=reg_data['enable_2fa']
                )
                
                if reg_data['enable_2fa']:
                    otp_secret = generate_otp_secret()
                    update_user(reg_data['username'], "otp_secret", otp_secret)
                    
                    self.show_qr_code(otp_secret, reg_data['username'], reg_data['email'])
                else:
                    QMessageBox.information(self, "Registration Successful", "Your account has been created successfully. You can now login.")
                
                log_action(reg_data['username'], "user_registered")
            except Exception as e:
                QMessageBox.critical(self, "Registration Error", f"An error occurred: {str(e)}")
    
    def show_qr_code(self, otp_secret, username, email):
        """
        Show dialog to display setup key for 2FA setup.
        """
        setup_key_dialog = SetupKeyDialog(self, otp_secret, username, email)
        setup_key_dialog.exec_()
    
    def show_forgot_password(self):
        """
        Show dialog to reset password.
        """
        dialog = ForgotPasswordDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            username, email = dialog.get_reset_data()
            
            if not username or not email:
                QMessageBox.warning(self, "Reset Error", "Please enter both username and email.")
                return self.show_forgot_password()
            
            user = get_user(username)
            if not user:
                QMessageBox.warning(self, "Reset Error", "User not found.")
                return self.show_forgot_password()
            
            if user.get("email", "").lower() != email.lower():
                QMessageBox.warning(self, "Reset Error", "Email does not match.")
                return self.show_forgot_password()
            
            try:
                temp_password = set_temporary_password(username)
                
                try:
                    send_temporary_password_email(email, username, temp_password, 2)
                    QMessageBox.information(self, "Password Reset", 
                                          f"A temporary password has been sent to your email.\n"
                                          f"The temporary password is valid for 2 minutes.")
                except Exception as e:
                    QMessageBox.information(self, "Password Reset", 
                                          f"Email sending failed, but your temporary password is: {temp_password}\n"
                                          f"This password is valid for 2 minutes.")
                
                log_action(username, "password_reset")
            except Exception as e:
                QMessageBox.critical(self, "Reset Error", f"An error occurred: {str(e)}")
                log_action(username, "password_reset_failed", str(e)) 