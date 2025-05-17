"""
Base page class for all pages in the application.
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout


class BasePage(QWidget):
    """
    Base class for all pages in the application.
    """
    def __init__(self, parent):
        """
        Initialize the page.
        
        Args:
            parent: The parent widget
        """
        super().__init__(parent)
        self.parent = parent
        
        # Reference to the current automaton (shared across pages)
        self.automaton = None
        
        # Set up the UI
        self.setup_ui()
    
    def setup_ui(self):
        """
        Set up the UI elements for the page.
        This method should be overridden by subclasses.
        
        Note: Subclasses should create their own layout in this method.
        """
        pass
    
    def update_automaton(self, automaton):
        """
        Update the current automaton reference.
        
        Args:
            automaton: The new automaton
        """
        self.automaton = automaton
        self.on_automaton_changed()
    
    def on_automaton_changed(self):
        """
        Handle automaton change event.
        This method should be overridden by subclasses.
        """
        pass
    
    def show_message(self, message, message_type="info"):
        """
        Show a message in the status bar.
        
        Args:
            message: The message to show
            message_type: The type of message ("info", "warning", "error")
        """
        # Navigate up to the main window to access the status bar
        main_window = self.window()
        
        if hasattr(main_window, "show_message"):
            main_window.show_message(message, message_type)
    
    def clear_message(self):
        """
        Clear the message in the status bar.
        """
        self.show_message("") 