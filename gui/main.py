import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QLabel, 
    QMenu, QAction, QVBoxLayout, QWidget, QPushButton,
    QMessageBox, QDialog, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette

from .pages.automata_page import AutomataPage
from .pages.analysis_page import AnalysisPage
from .pages.advanced_page import AdvancedPage
from .pages.login_page import LoginPage


# Define app style constants
APP_STYLE = """
QMainWindow, QDialog {
    background-color: #f5f5f7;
}

QTabWidget::pane {
    border: 1px solid #c0c0c0;
    background-color: #ffffff;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #e0e0e5;
    color: #505050;
    border: 1px solid #c0c0c0;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 10px 20px;
    margin-right: 2px;
    font-weight: bold;
    min-width: 120px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #2c3e50;
    border-bottom: none;
}

QGroupBox {
    font-weight: bold;
    border: 1px solid #c0c0c0;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 16px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}

QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 15px;
    font-weight: bold;
    min-width: 100px;
    min-height: 30px;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #1c6ea4;
}

QPushButton:disabled {
    background-color: #cccccc;
    color: #666666;
}

QLineEdit {
    border: 1px solid #c0c0c0;
    border-radius: 4px;
    padding: 5px;
    background-color: white;
}

QLineEdit:focus {
    border: 1px solid #3498db;
}

QComboBox {
    border: 1px solid #c0c0c0;
    border-radius: 4px;
    padding: 5px;
    background-color: white;
}

QLabel {
    color: #2c3e50;
}

QTextEdit {
    border: 1px solid #c0c0c0;
    border-radius: 4px;
    background-color: white;
}

QCheckBox {
    spacing: 8px;
}

/* Special buttons */
QPushButton#delete-button {
    background-color: #e74c3c;
}

QPushButton#delete-button:hover {
    background-color: #c0392b;
}

#title-label {
    font-size: 16pt;
    color: #2c3e50;
    font-weight: bold;
}

#welcome-label {
    font-size: 12pt;
    color: #34495e;
}

QMenuBar {
    background-color: #2c3e50;
    color: white;
}

QMenuBar::item {
    background-color: transparent;
    color: white;
    padding: 6px 12px;
}

QMenuBar::item:selected {
    background-color: #3498db;
}

QMenu {
    background-color: #2c3e50;
    color: white;
    border: 1px solid #1c2833;
}

QMenu::item {
    padding: 6px 20px 6px 20px;
}

QMenu::item:selected {
    background-color: #3498db;
}

QMenu::separator {
    height: 1px;
    background: #1c2833;
    margin: 5px 15px;
}

QStatusBar {
    background-color: #2c3e50;
    color: white;
}
"""


class AutomataApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Automata App")
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)
        
        # Apply the stylesheet
        self.setStyleSheet(APP_STYLE)
        
        # Set application-wide font
        app_font = QFont("Segoe UI", 10)
        QApplication.setFont(app_font)
        
        # Set the application icon if available
        try:
            self.setWindowIcon(QIcon("resources/icon.ico"))
        except:
            pass
        
        # Create a central widget to hold either the login page or the main app
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Create and show the login page first
        self.login_page = LoginPage(self)
        self.layout.addWidget(self.login_page)
        
        # Initialize but don't create the main app yet
        self.main_app_widget = None
        self.notebook = None
        self.automata_page = None
        self.analysis_page = None
        self.advanced_page = None
        
        # Create status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Please login to continue")
        
        # Current user
        self.current_user = None
    
    def on_login_success(self, user):
        # Store the current user
        self.current_user = user
        
        # Remove the login page
        self.login_page.setParent(None)
        
        # Create the main application UI
        self.create_main_app()
    
    def create_main_app(self):
        # Create main app widget
        self.main_app_widget = QWidget()
        main_layout = QVBoxLayout(self.main_app_widget)
        
        # Create a notebook for tabs
        self.notebook = QTabWidget()
        main_layout.addWidget(self.notebook)
        
        # Create the pages
        self.automata_page = AutomataPage(self)
        self.analysis_page = AnalysisPage(self)
        self.advanced_page = AdvancedPage(self)
        
        # Add the pages to the notebook
        self.notebook.addTab(self.automata_page, "Automata")
        self.notebook.addTab(self.analysis_page, "Analysis")
        self.notebook.addTab(self.advanced_page, "Advanced")
        
        # Set up tab change event
        self.notebook.currentChanged.connect(self.on_tab_changed)
        
        # Add main app to layout
        self.layout.addWidget(self.main_app_widget)
        
        # Create menu
        self.create_menu()
        
        # Update status bar
        username = self.current_user.get("username", "User")
        role = self.current_user.get("role", "user")
        self.status_bar.showMessage(f"Logged in as {username} ({role})")
    
    def create_menu(self):
        # Create menu bar
        menu_bar = self.menuBar()
        
        # User menu
        user_menu = menu_bar.addMenu("User")
        
        # Show username in menu
        username = self.current_user.get("username", "Unknown")
        user_label_action = QAction(f"Logged in as: {username}", self)
        user_label_action.setEnabled(False)
        user_menu.addAction(user_label_action)
        
        user_menu.addSeparator()
        
        # Add logout action
        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.logout)
        user_menu.addAction(logout_action)
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        new_action = QAction("New Automaton", self)
        new_action.triggered.connect(self.automata_page.create_new_automaton)
        file_menu.addAction(new_action)
        
        load_action = QAction("Load Automaton", self)
        load_action.triggered.connect(self.automata_page.load_automaton)
        file_menu.addAction(load_action)
        
        save_action = QAction("Save Automaton", self)
        save_action.triggered.connect(self.automata_page.save_automaton)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")
        
        add_state_action = QAction("Add State", self)
        add_state_action.triggered.connect(self.automata_page.add_state)
        edit_menu.addAction(add_state_action)
        
        add_transition_action = QAction("Add Transition", self)
        add_transition_action.triggered.connect(self.automata_page.add_transition)
        edit_menu.addAction(add_transition_action)
        
        delete_selected_action = QAction("Delete Selected", self)
        delete_selected_action.triggered.connect(self.automata_page.delete_selected)
        edit_menu.addAction(delete_selected_action)
        
        # Analysis menu
        analysis_menu = menu_bar.addMenu("Analysis")
        
        check_determinism_action = QAction("Check Determinism", self)
        check_determinism_action.triggered.connect(self.analysis_page.check_determinism)
        analysis_menu.addAction(check_determinism_action)
        
        check_completeness_action = QAction("Check Completeness", self)
        check_completeness_action.triggered.connect(self.analysis_page.check_completeness)
        analysis_menu.addAction(check_completeness_action)
        
        minimize_action = QAction("Minimize", self)
        minimize_action.triggered.connect(self.analysis_page.minimize_automaton)
        analysis_menu.addAction(minimize_action)
        
        convert_to_dfa_action = QAction("Convert NFA to DFA", self)
        convert_to_dfa_action.triggered.connect(self.analysis_page.convert_to_dfa)
        analysis_menu.addAction(convert_to_dfa_action)
        
        # Simulation menu
        simulation_menu = menu_bar.addMenu("Simulation")
        
        test_word_action = QAction("Test Word", self)
        test_word_action.triggered.connect(self.advanced_page.test_word)
        simulation_menu.addAction(test_word_action)
        
        generate_words_action = QAction("Generate Words", self)
        generate_words_action.triggered.connect(self.advanced_page.generate_words)
        simulation_menu.addAction(generate_words_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def logout(self):
        reply = QMessageBox.question(
            self, "Logout", "Are you sure you want to logout?", 
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Log the action
            if self.current_user:
                from Security.security.logs import log_action
                log_action(self.current_user.get("username", "unknown"), "logout")
            
            # Remove main app
            if self.main_app_widget:
                self.main_app_widget.setParent(None)
                self.main_app_widget = None
            
            # Clear menu
            self.menuBar().clear()
            
            # Reset current user
            self.current_user = None
            
            # Create new login page
            self.login_page = LoginPage(self)
            self.layout.addWidget(self.login_page)
            
            # Update status bar
            self.status_bar.showMessage("Please login to continue")
    
    def on_tab_changed(self, index):
        tab_text = self.notebook.tabText(index)
        
        if tab_text == "Analysis":
            self.analysis_page.update_analysis()
        elif tab_text == "Advanced":
            self.advanced_page.update_advanced()
    
    def show_about(self):
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle("About Automata App")
        about_dialog.setFixedSize(500, 400)
        
        layout = QVBoxLayout(about_dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Create a card-like container
        content_widget = QWidget()
        content_widget.setObjectName("about-container")
        content_widget.setStyleSheet("""
            #about-container {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        
        # Add title
        title_label = QLabel("Automata App")
        title_label.setObjectName("title-label")
        title_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(title_label)
        
        # Add description
        desc_label = QLabel("A Python application for working with finite automata (DFA/NFA) with integrated security features.")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(desc_label)
        
        # Add horizontal line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #e0e0e0;")
        content_layout.addWidget(separator)
        
        # Add version
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(version_label)
        
        # Add creators
        creators_label = QLabel("Created by CSCC-12 Group")
        creators_label.setAlignment(Qt.AlignCenter)
        creators_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        content_layout.addWidget(creators_label)
        
        # Add project details
        project_label = QLabel("Group Project for Pr. Kamouss and Pr. Lazaiz")
        project_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(project_label)
        
        # Add copyright
        copyright_label = QLabel("© 2025 CSCC-12")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("color: #7f8c8d;")
        content_layout.addWidget(copyright_label)
        
        # Add the content widget to the main layout
        layout.addWidget(content_widget)
        
        # Add close button with styling
        close_button = QPushButton("Close")
        close_button.setMinimumHeight(40)
        close_button.clicked.connect(about_dialog.close)
        layout.addWidget(close_button)
        
        about_dialog.exec_()
    
    def show_message(self, message, message_type="info"):
        self.status_bar.showMessage(message)


def main():
    app = QApplication(sys.argv)
    window = AutomataApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 