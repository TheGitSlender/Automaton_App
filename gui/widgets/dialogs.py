"""
Dialog utilities for the application.
"""
from PyQt5.QtWidgets import (
    QMessageBox, QInputDialog, QFileDialog, QDialog,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QTextEdit, QComboBox,
    QListWidget, QAbstractItemView
)
from PyQt5.QtCore import Qt


def show_info(parent, title, message):
    """
    Show an information dialog.
    
    Args:
        parent: The parent widget
        title: The dialog title
        message: The message to show
    """
    QMessageBox.information(parent, title, message)


def show_warning(parent, title, message):
    """
    Show a warning dialog.
    
    Args:
        parent: The parent widget
        title: The dialog title
        message: The message to show
    """
    QMessageBox.warning(parent, title, message)


def show_error(parent, title, message):
    """
    Show an error dialog.
    
    Args:
        parent: The parent widget
        title: The dialog title
        message: The message to show
    """
    QMessageBox.critical(parent, title, message)


def ask_yes_no(parent, title, message):
    """
    Show a yes/no dialog.
    
    Args:
        parent: The parent widget
        title: The dialog title
        message: The message to show
    
    Returns:
        True if the user clicked Yes, False otherwise
    """
    reply = QMessageBox.question(
        parent, title, message, 
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
    )
    return reply == QMessageBox.Yes


def choose_file_open(parent, title, filetypes=None):
    """
    Show a file open dialog.
    
    Args:
        parent: The parent widget
        title: The dialog title
        filetypes: A list of filetypes to show, e.g., [("Text files", "*.txt"), ("All files", "*.*")]
    
    Returns:
        The selected file path or None if canceled
    """
    if filetypes:
        filter_str = ";;".join([f"{desc} ({ext})" for desc, ext in filetypes])
    else:
        filter_str = "All Files (*.*)"
    
    file_path, _ = QFileDialog.getOpenFileName(parent, title, "", filter_str)
    
    if file_path:
        return file_path
    return None


def choose_file_save(parent, title, filetypes=None, default_ext=None):
    """
    Show a file save dialog.
    
    Args:
        parent: The parent widget
        title: The dialog title
        filetypes: A list of filetypes to show, e.g., [("Text files", "*.txt"), ("All files", "*.*")]
        default_ext: The default extension to add
    
    Returns:
        The selected file path or None if canceled
    """
    if filetypes:
        filter_str = ";;".join([f"{desc} ({ext})" for desc, ext in filetypes])
    else:
        filter_str = "All Files (*.*)"
    
    file_path, _ = QFileDialog.getSaveFileName(parent, title, "", filter_str)
    
    if file_path:
        return file_path
    return None


class InputDialog(QDialog):
    """
    A dialog for simple input.
    """
    def __init__(self, parent, title, prompt, default=""):
        """
        Initialize the dialog.
        
        Args:
            parent: The parent widget
            title: The dialog title
            prompt: The prompt text
            default: The default value
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(300, 100)
        
        self.layout = QVBoxLayout(self)
        
        self.prompt = QLabel(prompt)
        self.layout.addWidget(self.prompt)
        
        self.input = QLineEdit(default)
        self.layout.addWidget(self.input)
        
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.layout.addLayout(button_layout)
    
    def get_input(self):
        """
        Get the input text.
        
        Returns:
            The input text or None if canceled
        """
        if self.exec_() == QDialog.Accepted:
            return self.input.text()
        return None


class ListSelectionDialog(QDialog):
    """
    Dialog for selecting an item from a list.
    """
    def __init__(self, parent, title, prompt, items):
        """
        Initialize the dialog.
        
        Args:
            parent: The parent widget
            title: The dialog title
            prompt: The prompt text
            items: List of items to select from
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(300, 300)
        self.items = items
        self.result = None
        
        layout = QVBoxLayout(self)
        
        self.prompt_label = QLabel(prompt)
        layout.addWidget(self.prompt_label)
        
        # Create listbox
        self.listbox = QListWidget()
        self.listbox.addItems(items)
        self.listbox.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.listbox)
        
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def accept(self):
        """
        Handle OK button click.
        """
        selected_items = self.listbox.selectedItems()
        if selected_items:
            item = selected_items[0]
            index = self.listbox.row(item)
            self.result = self.items[index]
        super().accept()
    
    def get_selection(self):
        """
        Get the selected item.
        
        Returns:
            The selected item or None if canceled
        """
        if self.exec_() == QDialog.Accepted:
            return self.result
        return None 