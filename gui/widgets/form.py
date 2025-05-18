from PyQt5.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QCheckBox, QPushButton,
    QComboBox, QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt


class Form(QDialog):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        
        # Setup layout
        self.layout = QVBoxLayout(self)
        
        # Form content - override in subclasses
        self.setup_form()
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # OK button
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.on_ok)
        button_layout.addWidget(self.ok_button)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel)
        button_layout.addWidget(self.cancel_button)
        
        self.layout.addLayout(button_layout)
    
    def setup_form(self):
        pass
    
    def on_ok(self):
        self.accept()
    
    def on_cancel(self):
        self.reject()


class StateForm(Form):
    def __init__(self, parent, title, state=None):
        self.state = state
        super().__init__(parent, title)
    
    def setup_form(self):
        form_layout = QFormLayout()
        self.layout.addLayout(form_layout)
        
        # Name field
        self.name_edit = QLineEdit()
        if self.state:
            self.name_edit.setText(self.state.name)
        form_layout.addRow("Name:", self.name_edit)
        
        # Initial state checkbox
        self.is_initial = QCheckBox("Initial State")
        if self.state and self.state.is_initial:
            self.is_initial.setChecked(True)
        self.layout.addWidget(self.is_initial)
        
        # Final state checkbox
        self.is_final = QCheckBox("Final State")
        if self.state and self.state.is_final:
            self.is_final.setChecked(True)
        self.layout.addWidget(self.is_final)
    
    def on_ok(self):
        self.result = {
            'name': self.name_edit.text(),
            'is_initial': self.is_initial.isChecked(),
            'is_final': self.is_final.isChecked()
        }
        self.accept()


class TransitionForm(Form):
    def __init__(self, parent, title, states, alphabet, transition=None):
        self.states = states
        self.alphabet = alphabet
        self.transition = transition
        super().__init__(parent, title)
    
    def setup_form(self):
        form_layout = QFormLayout()
        self.layout.addLayout(form_layout)
        
        # Source state dropdown
        self.source_combo = QComboBox()
        for state in self.states:
            self.source_combo.addItem(state.name)
        
        if self.transition and self.transition.src:
            index = self.source_combo.findText(self.transition.src.name)
            if index >= 0:
                self.source_combo.setCurrentIndex(index)
        
        form_layout.addRow("Source State:", self.source_combo)
        
        # Symbol dropdown
        self.symbol_combo = QComboBox()
        for symbol in self.alphabet:
            self.symbol_combo.addItem(symbol)
        
        if self.transition and self.transition.symbol:
            index = self.symbol_combo.findText(self.transition.symbol)
            if index >= 0:
                self.symbol_combo.setCurrentIndex(index)
        
        form_layout.addRow("Symbol:", self.symbol_combo)
        
        # Destination state dropdown
        self.dest_combo = QComboBox()
        for state in self.states:
            self.dest_combo.addItem(state.name)
        
        if self.transition and self.transition.dest:
            index = self.dest_combo.findText(self.transition.dest.name)
            if index >= 0:
                self.dest_combo.setCurrentIndex(index)
        
        form_layout.addRow("Destination State:", self.dest_combo)
    
    def on_ok(self):
        self.result = {
            'source': self.source_combo.currentText(),
            'symbol': self.symbol_combo.currentText(),
            'destination': self.dest_combo.currentText()
        }
        self.accept() 