from PyQt5.QtWidgets import (
    QMessageBox, QInputDialog, QFileDialog, QDialog,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QTextEdit, QComboBox,
    QListWidget, QAbstractItemView
)
from PyQt5.QtCore import Qt


def show_info(parent, title, message):
    QMessageBox.information(parent, title, message)


def show_warning(parent, title, message):
    QMessageBox.warning(parent, title, message)


def show_error(parent, title, message):
    QMessageBox.critical(parent, title, message)


def ask_yes_no(parent, title, message):
    reply = QMessageBox.question(
        parent, title, message, 
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
    )
    return reply == QMessageBox.Yes


def choose_file_open(parent, title, filetypes=None):
    if filetypes:
        filter_str = ";;".join([f"{desc} ({ext})" for desc, ext in filetypes])
    else:
        filter_str = "All Files (*.*)"
    
    file_path, _ = QFileDialog.getOpenFileName(parent, title, "", filter_str)
    
    if file_path:
        return file_path
    return None


def choose_file_save(parent, title, filetypes=None, default_ext=None):
    if filetypes:
        filter_str = ";;".join([f"{desc} ({ext})" for desc, ext in filetypes])
    else:
        filter_str = "All Files (*.*)"
    
    file_path, _ = QFileDialog.getSaveFileName(parent, title, "", filter_str)
    
    if file_path:
        return file_path
    return None


class InputDialog(QDialog):
    def __init__(self, parent, title, prompt, default=""):
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
        if self.exec_() == QDialog.Accepted:
            return self.input.text()
        return None


class ListSelectionDialog(QDialog):
    def __init__(self, parent, title, prompt, items):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(300, 300)
        self.items = items
        self.result = None
        
        layout = QVBoxLayout(self)
        
        self.prompt_label = QLabel(prompt)
        layout.addWidget(self.prompt_label)
        
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
        selected_items = self.listbox.selectedItems()
        if selected_items:
            item = selected_items[0]
            index = self.listbox.row(item)
            self.result = self.items[index]
        super().accept()
    
    def get_selection(self):
        if self.exec_() == QDialog.Accepted:
            return self.result
        return None 