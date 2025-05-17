"""
Main entry point for the Automata GUI application.
"""
import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QLabel, 
    QMenu, QAction, QVBoxLayout, QWidget, QPushButton,
    QMessageBox, QDialog, QHBoxLayout
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont

from .pages.automata_page import AutomataPage
from .pages.analysis_page import AnalysisPage
from .pages.advanced_page import AdvancedPage


class AutomataApp(QMainWindow):
    """
    Main application class for the Automata GUI.
    """
    def __init__(self):
        """
        Initialize the application.
        """
        super().__init__()
        self.setWindowTitle("Automata App")
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)
        
        # Set the application icon if available
        try:
            self.setWindowIcon(QIcon("resources/icon.ico"))
        except:
            pass  # Icon not found, ignore
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Set up the main layout
        main_layout = QVBoxLayout(central_widget)
        
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
        
        # Create menu
        self.create_menu()
        
        # Create status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
    
    def create_menu(self):
        """
        Create the application menu.
        """
        # Create menu bar
        menu_bar = self.menuBar()
        
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
    
    def on_tab_changed(self, index):
        """
        Handle tab change event.
        
        Args:
            index: The index of the selected tab
        """
        tab_text = self.notebook.tabText(index)
        
        if tab_text == "Analysis":
            self.analysis_page.update_analysis()
        elif tab_text == "Advanced":
            self.advanced_page.update_advanced()
    
    def show_about(self):
        """
        Show the about dialog.
        """
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle("About Automata App")
        about_dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout(about_dialog)
        
        # Add title
        title_label = QLabel("Automata App")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Add description
        desc_label = QLabel("A Python application for working with finite automata (DFA/NFA).")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        # Add version
        version_label = QLabel("Version 0.1.0")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # Add copyright
        copyright_label = QLabel("© 2023 Student Project")
        copyright_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(copyright_label)
        
        # Add close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(about_dialog.close)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        
        layout.addStretch()
        layout.addLayout(button_layout)
        
        about_dialog.exec_()
    
    def show_message(self, message, message_type="info"):
        """
        Show a message in the status bar.
        
        Args:
            message: The message to show
            message_type: The type of message ("info", "warning", "error")
        """
        self.status_bar.showMessage(message)


def main():
    """
    Main function for the application.
    """
    app = QApplication(sys.argv)
    window = AutomataApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 