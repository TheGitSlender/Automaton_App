from PyQt5.QtWidgets import QWidget, QVBoxLayout


class BasePage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Reference to the current automaton (shared across pages)
        self.automaton = None
        
        # Set up the UI
        self.setup_ui()
    
    def setup_ui(self):
        pass
    
    def update_automaton(self, automaton):
        self.automaton = automaton
        self.on_automaton_changed()
    
    def on_automaton_changed(self):
        pass
    
    def show_message(self, message, message_type="info"):
        # Navigate up to the main window to access the status bar
        main_window = self.window()
        
        if hasattr(main_window, "show_message"):
            main_window.show_message(message, message_type)
    
    def clear_message(self):
        self.show_message("") 