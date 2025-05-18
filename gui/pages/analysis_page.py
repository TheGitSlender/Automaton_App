from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QPushButton, QTextEdit, QFrame,
    QGroupBox, QFormLayout, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt
import os
import glob
from datetime import datetime

from automata.operations import (
    is_deterministic, is_complete, nfa_to_dfa, minimize_automaton,
    make_complete
)
from automata.storage import save_automaton, load_automaton

from .base_page import BasePage
from ..widgets.tree_canvas import AutomataCanvas
from ..widgets.dialogs import show_info, show_error, show_warning, choose_file_save

# Directory for saving automata before analysis
AUTOMATA_SAVE_DIR = "Automates"

class AnalysisPage(BasePage):
    def __init__(self, parent):
        
        QWidget.__init__(self, parent)
        self.parent = parent
        
        self.automaton = None
        
        self.analysis_automaton = None
        
        self.current_automaton_path = None
        
        os.makedirs(AUTOMATA_SAVE_DIR, exist_ok=True)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(self.splitter)
        
        self.left_frame = QWidget()
        self.left_layout = QVBoxLayout(self.left_frame)
        self.splitter.addWidget(self.left_frame)
        
        self.selector_group = QGroupBox("Automaton Selection")
        selector_layout = QVBoxLayout(self.selector_group)
        
        selector_frame = QWidget()
        selector_frame_layout = QHBoxLayout(selector_frame)
        selector_frame_layout.setContentsMargins(0, 0, 0, 0)
        
        self.automaton_combo = QComboBox()
        selector_frame_layout.addWidget(self.automaton_combo)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_automaton_list)
        selector_frame_layout.addWidget(refresh_button)
        
        selector_layout.addWidget(selector_frame)
        
        buttons_frame = QWidget()
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        load_button = QPushButton("Load Selected")
        load_button.setMinimumWidth(120)
        load_button.setMinimumHeight(30)
        load_button.clicked.connect(self.load_selected_automaton)
        buttons_layout.addWidget(load_button)
        
        save_button = QPushButton("Save Automaton")
        save_button.setMinimumWidth(120)
        save_button.setMinimumHeight(30)
        save_button.clicked.connect(self.save_automaton)
        buttons_layout.addWidget(save_button)
        
        selector_layout.addWidget(buttons_frame)
        
        # Add delete button in another row
        delete_frame = QWidget()
        delete_layout = QHBoxLayout(delete_frame)
        delete_layout.setContentsMargins(0, 0, 0, 0)
        
        delete_button = QPushButton("Delete Selected")
        delete_button.setObjectName("delete-button")  # Use the ID for styling from the main stylesheet
        delete_button.setMinimumWidth(120)
        delete_button.setMinimumHeight(30)
        delete_button.clicked.connect(self.delete_automaton)
        delete_layout.addWidget(delete_button)
        
        selector_layout.addWidget(delete_frame)
        
        self.left_layout.addWidget(self.selector_group)
        
        # Properties group
        self.properties_group = QGroupBox("Properties")
        self.properties_layout = QVBoxLayout(self.properties_group)
        self.left_layout.addWidget(self.properties_group)
        
        # Determinism
        determinism_frame = QWidget()
        determinism_layout = QHBoxLayout(determinism_frame)
        determinism_layout.setContentsMargins(0, 0, 0, 0)
        
        determinism_label = QLabel("Deterministic:")
        determinism_layout.addWidget(determinism_label)
        
        self.determinism_value = QLabel("N/A")
        self.determinism_value.setMinimumWidth(60)
        determinism_layout.addWidget(self.determinism_value)
        
        determinism_button = QPushButton("Check")
        determinism_button.setMinimumWidth(80)
        determinism_button.setMinimumHeight(30)
        determinism_button.clicked.connect(self.check_determinism)
        determinism_layout.addWidget(determinism_button)
        
        self.properties_layout.addWidget(determinism_frame)
        
        # Completeness
        completeness_frame = QWidget()
        completeness_layout = QHBoxLayout(completeness_frame)
        completeness_layout.setContentsMargins(0, 0, 0, 0)
        
        completeness_label = QLabel("Complete:")
        completeness_layout.addWidget(completeness_label)
        
        self.completeness_value = QLabel("N/A")
        self.completeness_value.setMinimumWidth(60)
        completeness_layout.addWidget(self.completeness_value)
        
        completeness_button = QPushButton("Check")
        completeness_button.setMinimumWidth(80)
        completeness_button.setMinimumHeight(30)
        completeness_button.clicked.connect(self.check_completeness)
        completeness_layout.addWidget(completeness_button)
        
        self.properties_layout.addWidget(completeness_frame)
        
        # Number of states
        states_frame = QWidget()
        states_layout = QHBoxLayout(states_frame)
        states_layout.setContentsMargins(0, 0, 0, 0)
        
        states_label = QLabel("States:")
        states_layout.addWidget(states_label)
        
        self.states_value = QLabel("0")
        self.states_value.setMinimumWidth(60)
        states_layout.addWidget(self.states_value)
        
        states_layout.addStretch()
        
        self.properties_layout.addWidget(states_frame)
        
        # Number of transitions
        transitions_frame = QWidget()
        transitions_layout = QHBoxLayout(transitions_frame)
        transitions_layout.setContentsMargins(0, 0, 0, 0)
        
        transitions_label = QLabel("Transitions:")
        transitions_layout.addWidget(transitions_label)
        
        self.transitions_value = QLabel("0")
        self.transitions_value.setMinimumWidth(60)
        transitions_layout.addWidget(self.transitions_value)
        
        transitions_layout.addStretch()
        
        self.properties_layout.addWidget(transitions_frame)
        
        # Alphabet size
        alphabet_frame = QWidget()
        alphabet_layout = QHBoxLayout(alphabet_frame)
        alphabet_layout.setContentsMargins(0, 0, 0, 0)
        
        alphabet_label = QLabel("Alphabet size:")
        alphabet_layout.addWidget(alphabet_label)
        
        self.alphabet_value = QLabel("0")
        self.alphabet_value.setMinimumWidth(60)
        alphabet_layout.addWidget(self.alphabet_value)
        
        alphabet_layout.addStretch()
        
        self.properties_layout.addWidget(alphabet_frame)
        
        # Transformations group
        self.transformations_group = QGroupBox("Transformations")
        self.transformations_layout = QVBoxLayout(self.transformations_group)
        self.left_layout.addWidget(self.transformations_group)
        
        # NFA to DFA
        nfa_to_dfa_frame = QWidget()
        nfa_to_dfa_layout = QHBoxLayout(nfa_to_dfa_frame)
        nfa_to_dfa_layout.setContentsMargins(0, 0, 0, 0)
        
        nfa_to_dfa_label = QLabel("Convert NFA to DFA:")
        nfa_to_dfa_layout.addWidget(nfa_to_dfa_label)
        
        nfa_to_dfa_button = QPushButton("Convert")
        nfa_to_dfa_button.setMinimumWidth(90)
        nfa_to_dfa_button.setMinimumHeight(30)
        nfa_to_dfa_button.clicked.connect(self.convert_to_dfa)
        nfa_to_dfa_layout.addWidget(nfa_to_dfa_button)
        
        self.transformations_layout.addWidget(nfa_to_dfa_frame)
        
        # Complete automaton
        complete_frame = QWidget()
        complete_layout = QHBoxLayout(complete_frame)
        complete_layout.setContentsMargins(0, 0, 0, 0)
        
        complete_label = QLabel("Make automaton complete:")
        complete_layout.addWidget(complete_label)
        
        complete_button = QPushButton("Complete")
        complete_button.setMinimumWidth(90)
        complete_button.setMinimumHeight(30)
        complete_button.clicked.connect(self.make_automaton_complete)
        complete_layout.addWidget(complete_button)
        
        self.transformations_layout.addWidget(complete_frame)
        
        # Minimize automaton
        minimize_frame = QWidget()
        minimize_layout = QHBoxLayout(minimize_frame)
        minimize_layout.setContentsMargins(0, 0, 0, 0)
        
        minimize_label = QLabel("Minimize automaton:")
        minimize_layout.addWidget(minimize_label)
        
        minimize_button = QPushButton("Minimize")
        minimize_button.setMinimumWidth(90)
        minimize_button.setMinimumHeight(30)
        minimize_button.clicked.connect(self.minimize_automaton)
        minimize_layout.addWidget(minimize_button)
        
        self.transformations_layout.addWidget(minimize_frame)
        
        self.left_layout.addStretch()
        
        # Right panel: Automaton visualization
        self.right_frame = QWidget()
        self.right_layout = QVBoxLayout(self.right_frame)
        self.splitter.addWidget(self.right_frame)
        
        # Canvas for drawing automaton
        self.canvas_frame = QGroupBox("Automaton Visualization")
        canvas_layout = QVBoxLayout(self.canvas_frame)
        
        self.canvas = AutomataCanvas(self)
        canvas_layout.addWidget(self.canvas)
        
        self.right_layout.addWidget(self.canvas_frame)
        
        # Details text area
        self.details_frame = QGroupBox("Details")
        details_layout = QVBoxLayout(self.details_frame)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        details_layout.addWidget(self.details_text)
        
        self.right_layout.addWidget(self.details_frame)
        
        # Set splitter sizes
        self.splitter.setSizes([300, 700])
        
        # Refresh the automaton list
        self.refresh_automaton_list()
    
    def on_automaton_changed(self):
        """
        Called when the automaton is changed in another page.
        """
        if self.parent and hasattr(self.parent, 'automata_page'):
            self.automaton = self.parent.automata_page.automaton
            self.update_analysis()
    
    def refresh_automaton_list(self):
        """
        Refresh the list of available automata.
        """
        self.automaton_combo.clear()
        
        automaton_files = glob.glob(os.path.join(AUTOMATA_SAVE_DIR, "*.json"))
        
        if not automaton_files:
            self.automaton_combo.addItem("No automata available")
            self.automaton_combo.setEnabled(False)
            return
        
        self.automaton_combo.setEnabled(True)
        
        for file_path in sorted(automaton_files):
            file_name = os.path.basename(file_path)
            self.automaton_combo.addItem(file_name, file_path)
        
        if self.current_automaton_path:
            file_name = os.path.basename(self.current_automaton_path)
            index = self.automaton_combo.findText(file_name)
            if index >= 0:
                self.automaton_combo.setCurrentIndex(index)
    
    def load_selected_automaton(self):
        """
        Load the selected automaton from the dropdown.
        """
        if self.automaton_combo.count() == 0 or not self.automaton_combo.isEnabled():
            show_warning(self, "No automaton available", "There are no automata to load.")
            return
        
        file_path = self.automaton_combo.currentData()
        if not file_path:
            return
        
        try:
            self.analysis_automaton = load_automaton(file_path)
            self.current_automaton_path = file_path
            
            # Log the creator of this automaton
            creator = self.analysis_automaton.creator_id if hasattr(self.analysis_automaton, 'creator_id') else "unknown"
            creator_info = f"Created by: {creator}" if creator else "Creator: unknown"
            
            self.update_analysis()
            
            show_info(self, "Automaton Loaded", f"Automaton loaded from {os.path.basename(file_path)}\n{creator_info}")
            
            # Log the action
            if self.parent and hasattr(self.parent, 'current_user'):
                from Security.security.logs import log_action
                username = self.parent.current_user.get("username", "unknown")
                log_action(username, "load_automaton", f"File: {os.path.basename(file_path)}, {creator_info}")
                
        except Exception as e:
            show_error(self, "Error Loading Automaton", str(e))
    
    def update_analysis(self):
        """
        Update the analysis display with the current automaton.
        """
        if self.analysis_automaton:
            automaton = self.analysis_automaton
        elif self.automaton:
            automaton = self.automaton
        else:
            # Clear the canvas and details
            self.canvas.clear_automaton()
            self.details_text.clear()
            self.states_value.setText("0")
            self.transitions_value.setText("0")
            self.alphabet_value.setText("0")
            self.determinism_value.setText("N/A")
            self.completeness_value.setText("N/A")
            return
        
        # Update the canvas
        self.canvas.update_automaton(automaton)
        
        # Update the details
        self.states_value.setText(str(len(automaton.states)))
        self.transitions_value.setText(str(len(automaton.transitions)))
        self.alphabet_value.setText(str(len(automaton.alphabet)))
        
        # Perform analysis
        is_det = is_deterministic(automaton)
        is_comp = is_complete(automaton)
        
        # Update the UI indicators
        if is_det:
            self.determinism_value.setText("Yes")
            self.determinism_value.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.determinism_value.setText("No")
            self.determinism_value.setStyleSheet("color: red; font-weight: bold;")
            
        if is_comp:
            self.completeness_value.setText("Yes")
            self.completeness_value.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.completeness_value.setText("No")
            self.completeness_value.setStyleSheet("color: red; font-weight: bold;")
        
        # Create comprehensive analysis
        details = f"Analysis of automaton:\n\n"
        
        # Determinism details
        details += f"DETERMINISM: {'Yes' if is_det else 'No'}\n"
        if is_det:
            details += (
                "The automaton is deterministic.\n"
                "Properties of a deterministic automaton:\n"
                "- Each state has at most one transition for each symbol\n"
                "- No epsilon transitions\n"
                "- Exactly one initial state\n"
            )
        else:
            details += (
                "The automaton is non-deterministic.\n"
                "Reasons for non-determinism could include:\n"
                "- Multiple transitions with the same symbol from a state\n"
                "- Presence of epsilon transitions\n"
                "- Multiple initial states\n"
            )
        
        details += "\n"
        
        # Completeness details
        details += f"COMPLETENESS: {'Yes' if is_comp else 'No'}\n"
        if is_comp:
            details += (
                "The automaton is complete.\n"
                "Properties of a complete automaton:\n"
                "- Each state has exactly one transition for each symbol in the alphabet\n"
                "- All possible inputs are handled from every state\n"
            )
        else:
            details += (
                "The automaton is incomplete.\n"
                "Reasons for incompleteness:\n"
                "- Some states don't have transitions for all symbols in the alphabet\n"
                "- Some input sequences may lead to undefined behavior\n"
            )
        
        # Update the details text
        self.details_text.setText(details)
    
    def check_determinism(self, show_message=True):
        """
        Check if the automaton is deterministic.
        
        Args:
            show_message: Whether to show a message with the result
        
        Returns:
            bool: True if deterministic, False otherwise
        """
        if self.analysis_automaton:
            automaton = self.analysis_automaton
        elif self.automaton:
            automaton = self.automaton
        else:
            if show_message:
                show_warning(self, "No Automaton", "No automaton is loaded or created.")
            return
        
        try:
            result = is_deterministic(automaton)
            
            if result:
                self.determinism_value.setText("Yes")
                self.determinism_value.setStyleSheet("color: green; font-weight: bold;")
                
                details = (
                    "The automaton is deterministic.\n\n"
                    "Properties of a deterministic automaton:\n"
                    "- Each state has at most one transition for each symbol\n"
                    "- No epsilon transitions\n"
                    "- Exactly one initial state"
                )
                self.details_text.setText(details)
                
                if show_message:
                    show_info(self, "Determinism Check", "The automaton is deterministic.")
            else:
                self.determinism_value.setText("No")
                self.determinism_value.setStyleSheet("color: red; font-weight: bold;")
                
                details = (
                    "The automaton is non-deterministic.\n\n"
                    "Reasons for non-determinism could include:\n"
                    "- Multiple transitions with the same symbol from a state\n"
                    "- Presence of epsilon transitions\n"
                    "- Multiple initial states"
                )
                self.details_text.setText(details)
                
                if show_message:
                    show_info(self, "Determinism Check", "The automaton is non-deterministic.")
            
            # Log the action
            if show_message and self.parent and hasattr(self.parent, 'current_user'):
                from Security.security.logs import log_action
                username = self.parent.current_user.get("username", "unknown")
                log_action(username, "check_determinism", f"Result: {result}")
                
            return result
            
        except Exception as e:
            if show_message:
                show_error(self, "Error Checking Determinism", str(e))
            return False
    
    def check_completeness(self, show_message=True):
        """
        Check if the automaton is complete.
        
        Args:
            show_message: Whether to show a message with the result
        
        Returns:
            bool: True if complete, False otherwise
        """
        if self.analysis_automaton:
            automaton = self.analysis_automaton
        elif self.automaton:
            automaton = self.automaton
        else:
            if show_message:
                show_warning(self, "No Automaton", "No automaton is loaded or created.")
            return
        
        try:
            result = is_complete(automaton)
            
            if result:
                self.completeness_value.setText("Yes")
                self.completeness_value.setStyleSheet("color: green; font-weight: bold;")
                
                details = (
                    "The automaton is complete.\n\n"
                    "Properties of a complete automaton:\n"
                    "- Each state has exactly one transition for each symbol in the alphabet\n"
                    "- All possible inputs are handled from every state"
                )
                self.details_text.setText(details)
                
                if show_message:
                    show_info(self, "Completeness Check", "The automaton is complete.")
            else:
                self.completeness_value.setText("No")
                self.completeness_value.setStyleSheet("color: red; font-weight: bold;")
                
                details = (
                    "The automaton is incomplete.\n\n"
                    "Reasons for incompleteness:\n"
                    "- Some states don't have transitions for all symbols in the alphabet\n"
                    "- Some input sequences may lead to undefined behavior"
                )
                self.details_text.setText(details)
                
                if show_message:
                    show_info(self, "Completeness Check", "The automaton is incomplete.")
            
            # Log the action
            if show_message and self.parent and hasattr(self.parent, 'current_user'):
                from Security.security.logs import log_action
                username = self.parent.current_user.get("username", "unknown")
                log_action(username, "check_completeness", f"Result: {result}")
                
            return result
            
        except Exception as e:
            if show_message:
                show_error(self, "Error Checking Completeness", str(e))
            return False
    
    def convert_to_dfa(self):
        """
        Convert the current automaton from NFA to DFA.
        """
        if self.analysis_automaton:
            automaton = self.analysis_automaton
        elif self.automaton:
            automaton = self.automaton
        else:
            show_warning(self, "No Automaton", "No automaton is loaded or created.")
            return
        
        try:
            # Check if already deterministic
            if is_deterministic(automaton):
                show_info(self, "Already Deterministic", "The automaton is already deterministic.")
                return
            
            # Convert to DFA
            dfa = nfa_to_dfa(automaton)
            
            # Preserve creator_id or set it to current user
            if hasattr(automaton, 'creator_id') and automaton.creator_id:
                dfa.creator_id = automaton.creator_id
            elif self.parent and hasattr(self.parent, 'current_user'):
                dfa.creator_id = self.parent.current_user.get("username", "unknown")
            
            # Save the DFA
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(AUTOMATA_SAVE_DIR, f"dfa_{timestamp}.json")
            save_automaton(dfa, file_path)
            
            # Load the DFA for analysis
            self.analysis_automaton = dfa
            self.current_automaton_path = file_path
            
            # Update the UI
            self.update_analysis()
            self.refresh_automaton_list()
            
            # Show success message
            show_info(self, "Conversion Complete", "NFA successfully converted to DFA.")
            
            # Log the action
            if self.parent and hasattr(self.parent, 'current_user'):
                from Security.security.logs import log_action
                username = self.parent.current_user.get("username", "unknown")
                log_action(username, "convert_to_dfa", f"File: {os.path.basename(file_path)}")
                
        except Exception as e:
            show_error(self, "Error Converting to DFA", str(e))
    
    def make_automaton_complete(self):
        """
        Make the current automaton complete.
        """
        if self.analysis_automaton:
            automaton = self.analysis_automaton
        elif self.automaton:
            automaton = self.automaton
        else:
            show_warning(self, "No Automaton", "No automaton is loaded or created.")
            return
        
        try:
            # Check if already complete
            if is_complete(automaton):
                show_info(self, "Already Complete", "The automaton is already complete.")
                return
            
            # Make complete
            complete_automaton = make_complete(automaton)
            
            # Preserve creator_id or set it to current user
            if hasattr(automaton, 'creator_id') and automaton.creator_id:
                complete_automaton.creator_id = automaton.creator_id
            elif self.parent and hasattr(self.parent, 'current_user'):
                complete_automaton.creator_id = self.parent.current_user.get("username", "unknown")
            
            # Save the complete automaton
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(AUTOMATA_SAVE_DIR, f"complete_{timestamp}.json")
            save_automaton(complete_automaton, file_path)
            
            # Load the complete automaton for analysis
            self.analysis_automaton = complete_automaton
            self.current_automaton_path = file_path
            
            # Update the UI
            self.update_analysis()
            self.refresh_automaton_list()
            
            # Show success message
            show_info(self, "Completion Done", "Automaton successfully made complete.")
            
            # Log the action
            if self.parent and hasattr(self.parent, 'current_user'):
                from Security.security.logs import log_action
                username = self.parent.current_user.get("username", "unknown")
                log_action(username, "make_complete", f"File: {os.path.basename(file_path)}")
                
        except Exception as e:
            show_error(self, "Error Making Automaton Complete", str(e))
    
    def minimize_automaton(self):
        """
        Minimize the current automaton.
        """
        if self.analysis_automaton:
            automaton = self.analysis_automaton
        elif self.automaton:
            automaton = self.automaton
        else:
            show_warning(self, "No Automaton", "No automaton is loaded or created.")
            return
        
        try:
            # Check if automaton is deterministic
            if not is_deterministic(automaton):
                reply = QMessageBox.question(
                    self, "Non-Deterministic Automaton",
                    "The automaton is non-deterministic. Convert to DFA first?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    automaton = nfa_to_dfa(automaton)
                else:
                    return
            
            # Minimize the automaton
            minimized = minimize_automaton(automaton)
            
            # Preserve creator_id or set it to current user
            if hasattr(automaton, 'creator_id') and automaton.creator_id:
                minimized.creator_id = automaton.creator_id
            elif self.parent and hasattr(self.parent, 'current_user'):
                minimized.creator_id = self.parent.current_user.get("username", "unknown")
            
            # Save the minimized automaton
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(AUTOMATA_SAVE_DIR, f"minimized_{timestamp}.json")
            save_automaton(minimized, file_path)
            
            # Load the minimized automaton for analysis
            self.analysis_automaton = minimized
            self.current_automaton_path = file_path
            
            # Update the UI
            self.update_analysis()
            self.refresh_automaton_list()
            
            # Show success message
            show_info(self, "Minimization Complete", "Automaton successfully minimized.")
            
            # Log the action
            if self.parent and hasattr(self.parent, 'current_user'):
                from Security.security.logs import log_action
                username = self.parent.current_user.get("username", "unknown")
                log_action(username, "minimize_automaton", f"File: {os.path.basename(file_path)}")
                
        except Exception as e:
            show_error(self, "Error Minimizing Automaton", str(e))
    
    def notify_automaton_changed(self):
        """
        Notify other pages that the automaton has changed.
        """
        if self.parent and hasattr(self.parent, 'automata_page'):
            self.parent.automata_page.automaton = self.analysis_automaton
            
            # Notify other pages
            if hasattr(self.parent, 'advanced_page'):
                self.parent.advanced_page.on_automaton_changed()
    
    def save_automaton(self):
        """
        Save the current automaton to a file.
        """
        if self.analysis_automaton:
            automaton = self.analysis_automaton
        elif self.automaton:
            automaton = self.automaton
        else:
            show_warning(self, "No Automaton", "No automaton is loaded or created.")
            return
        
        try:
            # Ask for file path
            file_path = choose_file_save(
                self, 
                "Save Automaton", 
                AUTOMATA_SAVE_DIR, 
                "JSON Files (*.json)"
            )
            
            if not file_path:
                return
            
            # Ensure extension
            if not file_path.endswith('.json'):
                file_path += '.json'
            
            # Set creator_id if not already set
            if not hasattr(automaton, 'creator_id') or automaton.creator_id is None:
                if self.parent and hasattr(self.parent, 'current_user'):
                    automaton.creator_id = self.parent.current_user.get("username", "unknown")
            
            # Save the automaton
            save_automaton(automaton, file_path)
            
            # Update current path
            self.current_automaton_path = file_path
            
            # Refresh the list
            self.refresh_automaton_list()
            
            # Show success message
            show_info(self, "Save Successful", f"Automaton saved to {os.path.basename(file_path)}")
            
            # Log the action
            if self.parent and hasattr(self.parent, 'current_user'):
                from Security.security.logs import log_action
                username = self.parent.current_user.get("username", "unknown")
                log_action(username, "save_automaton", f"File: {os.path.basename(file_path)}")
                
        except Exception as e:
            show_error(self, "Error Saving Automaton", str(e))
    
    def delete_automaton(self):
        """
        Delete the selected automaton file.
        """
        if self.automaton_combo.count() == 0 or not self.automaton_combo.isEnabled():
            show_warning(self, "No Automaton", "No automaton is available to delete.")
            return
        
        file_path = self.automaton_combo.currentData()
        if not file_path:
            return
        
        file_name = os.path.basename(file_path)
        
        # Load the automaton to check permissions
        try:
            automaton = load_automaton(file_path)
            
            # Check user permissions
            if self.parent and hasattr(self.parent, 'current_user'):
                current_username = self.parent.current_user.get("username", "unknown")
                current_role = self.parent.current_user.get("role", "user")
                
                # Check if the user has permission to delete (is admin or creator)
                if current_role != "admin" and automaton.creator_id != current_username:
                    show_error(self, "Permission Denied", 
                              "You don't have permission to delete this automaton. "
                              "Only administrators and the creator of the automaton can delete it.")
                    return
            
            reply = QMessageBox.question(
                self, "Delete Automaton",
                f"Are you sure you want to delete '{file_name}'?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    os.remove(file_path)
                    
                    # If the deleted file was the current one, clear it
                    if self.current_automaton_path == file_path:
                        self.current_automaton_path = None
                        self.analysis_automaton = None
                        self.update_analysis()
                    
                    # Refresh the list
                    self.refresh_automaton_list()
                    
                    # Show success message
                    show_info(self, "Delete Successful", f"Automaton '{file_name}' deleted.")
                    
                    # Log the action
                    if self.parent and hasattr(self.parent, 'current_user'):
                        from Security.security.logs import log_action
                        username = self.parent.current_user.get("username", "unknown")
                        log_action(username, "delete_automaton", f"File: {file_name}")
                        
                except Exception as e:
                    show_error(self, "Error Deleting Automaton", str(e))
                    
        except Exception as e:
            show_error(self, "Error Loading Automaton", 
                      f"Could not load automaton for permission check: {str(e)}") 