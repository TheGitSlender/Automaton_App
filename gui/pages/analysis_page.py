"""
Analysis page for automata properties and transformations.
"""
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
    """
    Page for analyzing automata properties and performing transformations.
    """
    def __init__(self, parent):
        """
        Initialize the page.
        
        Args:
            parent: The parent widget
        """
        # Important: Initialize as QWidget first without setting up layout
        QWidget.__init__(self, parent)
        self.parent = parent
        
        # Reference to the current automaton (shared across pages)
        self.automaton = None
        
        # Reference to the loaded automaton for analysis
        self.analysis_automaton = None
        
        # Current automaton file path
        self.current_automaton_path = None
        
        # Ensure the save directory exists
        os.makedirs(AUTOMATA_SAVE_DIR, exist_ok=True)
        
        # Set up the UI
        self.setup_ui()
    
    def setup_ui(self):
        """
        Set up the UI elements for the page.
        """
        # Create main frame
        layout = QVBoxLayout(self)
        
        # Create paned window
        self.splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(self.splitter)
        
        # Left panel: Analysis options
        self.left_frame = QWidget()
        self.left_layout = QVBoxLayout(self.left_frame)
        self.splitter.addWidget(self.left_frame)
        
        # Automaton selector
        self.selector_group = QGroupBox("Automaton Selection")
        selector_layout = QVBoxLayout(self.selector_group)
        
        # Automaton dropdown and refresh button
        selector_frame = QWidget()
        selector_frame_layout = QHBoxLayout(selector_frame)
        selector_frame_layout.setContentsMargins(0, 0, 0, 0)
        
        self.automaton_combo = QComboBox()
        selector_frame_layout.addWidget(self.automaton_combo)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_automaton_list)
        selector_frame_layout.addWidget(refresh_button)
        
        selector_layout.addWidget(selector_frame)
        
        # Load, save, and delete buttons
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
        
        # After transformation actions
        self.action_group = QGroupBox("Actions")
        action_layout = QVBoxLayout(self.action_group)
        
        # Save transformed automaton button
        save_transformed_button = QPushButton("Save Transformed Automaton")
        save_transformed_button.clicked.connect(self.save_automaton)
        action_layout.addWidget(save_transformed_button)
        
        self.left_layout.addWidget(self.action_group)
        
        # Add vertical stretch to push everything to the top
        self.left_layout.addStretch()
        
        # Right panel: Automaton visualization
        self.right_frame = QWidget()
        self.right_layout = QVBoxLayout(self.right_frame)
        self.splitter.addWidget(self.right_frame)
        
        # Canvas for visualization
        self.canvas = AutomataCanvas()
        self.right_layout.addWidget(self.canvas)
        
        # Results text area
        self.results_group = QGroupBox("Results")
        results_layout = QVBoxLayout(self.results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)
        
        self.right_layout.addWidget(self.results_group)
        
        # Set the splitter sizes
        self.splitter.setSizes([300, 700])
    
    def on_automaton_changed(self):
        """
        Update the page when the automaton changes.
        """
        # Refresh the automaton list when the shared automaton changes
        self.refresh_automaton_list()
    
    def refresh_automaton_list(self):
        """
        Refresh the list of available automata in the Automates directory.
        """
        self.automaton_combo.clear()
        
        # Get all JSON files in the Automates directory
        automaton_files = glob.glob(os.path.join(AUTOMATA_SAVE_DIR, "*.json"))
        
        if not automaton_files:
            self.automaton_combo.addItem("No automata available")
            self.automaton_combo.setEnabled(False)
            return
        
        self.automaton_combo.setEnabled(True)
        
        # Add each file to the combo box
        for file_path in automaton_files:
            file_name = os.path.basename(file_path)
            self.automaton_combo.addItem(file_name, file_path)
        
        # Select the first item
        self.automaton_combo.setCurrentIndex(0)
    
    def load_selected_automaton(self):
        """
        Load the selected automaton for analysis.
        """
        if self.automaton_combo.count() == 0 or not self.automaton_combo.isEnabled():
            show_warning(self, "No Automaton Available", "No automaton files available for analysis.")
            return
        
        # Get the selected file path
        file_path = self.automaton_combo.currentData()
        
        if not file_path or not os.path.exists(file_path):
            show_error(self, "Error", "Could not find the selected automaton file.")
            return
        
        try:
            # Load the automaton
            self.analysis_automaton = load_automaton(file_path)
            self.current_automaton_path = file_path
            
            # Update the UI
            self.update_analysis()
            
            show_info(self, "Automaton Loaded", f"Loaded {os.path.basename(file_path)} for analysis.")
        except Exception as e:
            show_error(self, "Error Loading Automaton", str(e))
    
    def update_analysis(self):
        """
        Update the analysis information.
        """
        # Clear results
        self.results_text.clear()
        
        # Reset properties
        self.determinism_value.setText("N/A")
        self.completeness_value.setText("N/A")
        self.states_value.setText("0")
        self.transitions_value.setText("0")
        self.alphabet_value.setText("0")
        
        # Update canvas
        self.canvas.update_automaton(self.analysis_automaton)
        
        if self.analysis_automaton is None:
            return
        
        # Update basic properties
        self.states_value.setText(str(len(self.analysis_automaton.states)))
        self.transitions_value.setText(str(len(self.analysis_automaton.transitions)))
        self.alphabet_value.setText(str(len(self.analysis_automaton.alphabet.symbols)))
    
    def check_determinism(self):
        """
        Check if the automaton is deterministic.
        """
        if self.analysis_automaton is None:
            show_error(self, "Error", "No automaton to analyze. Please load an automaton first.")
            return
        
        try:
            deterministic = is_deterministic(self.analysis_automaton)
            self.determinism_value.setText("Yes" if deterministic else "No")
            
            # Update results text
            self.results_text.clear()
            
            if deterministic:
                self.results_text.append("The automaton is deterministic.\n")
                self.results_text.append("A deterministic automaton has:")
                self.results_text.append("- Exactly one initial state")
                self.results_text.append("- At most one transition for each state and symbol")
            else:
                self.results_text.append("The automaton is non-deterministic.\n")
                
                # Find reasons for non-determinism
                reasons = []
                
                # Check for multiple initial states
                initial_states = [s for s in self.analysis_automaton.states.values() if s.is_initial]
                if len(initial_states) > 1:
                    reasons.append(f"There are {len(initial_states)} initial states")
                
                # Check for states with multiple transitions for the same symbol
                for state in self.analysis_automaton.states.values():
                    # Skip final states
                    if state.is_final:
                        continue
                        
                    symbols_seen = {}
                    for t in self.analysis_automaton.transitions:
                        if t.src == state:
                            if t.symbol in symbols_seen:
                                reasons.append(f"State '{state.name}' has multiple transitions for symbol '{t.symbol}'")
                                break
                            symbols_seen[t.symbol] = True
                
                # Show reasons
                if reasons:
                    self.results_text.append("Reasons:")
                    for reason in reasons:
                        self.results_text.append(f"- {reason}")
        except Exception as e:
            self.results_text.setText(f"Error: {str(e)}")
    
    def check_completeness(self):
        """
        Check if the automaton is complete.
        """
        if self.analysis_automaton is None:
            show_error(self, "Error", "No automaton to analyze. Please load an automaton first.")
            return
        
        try:
            complete = is_complete(self.analysis_automaton)
            self.completeness_value.setText("Yes" if complete else "No")
            
            # Update results text
            self.results_text.clear()
            
            if complete:
                self.results_text.append("The automaton is complete.\n")
                self.results_text.append("A complete automaton has a transition defined")
                self.results_text.append("for every state and every symbol in the alphabet.")
            else:
                self.results_text.append("The automaton is not complete.\n")
                
                # Find missing transitions
                missing = []
                
                for state in self.analysis_automaton.states.values():
                    # Check all states, including final states
                    for symbol in self.analysis_automaton.alphabet.symbols:
                        has_transition = False
                        for t in self.analysis_automaton.transitions:
                            if t.src == state and t.symbol == symbol:
                                has_transition = True
                                break
                        
                        if not has_transition:
                            missing.append(f"State '{state.name}' has no transition for symbol '{symbol}'")
                
                # Show missing transitions
                if missing:
                    self.results_text.append("Missing transitions:")
                    for m in missing:
                        self.results_text.append(f"- {m}")
        except Exception as e:
            self.results_text.setText(f"Error: {str(e)}")
    
    def convert_to_dfa(self):
        """
        Convert the automaton to a DFA.
        """
        if self.analysis_automaton is None:
            show_error(self, "Error", "No automaton to convert. Please load an automaton first.")
            return
        
        try:
            # Check if already deterministic
            if is_deterministic(self.analysis_automaton):
                show_info(self, "Info", "The automaton is already deterministic")
                return
            
            # Convert to DFA
            dfa = nfa_to_dfa(self.analysis_automaton)
            
            # Update the automaton
            self.analysis_automaton = dfa
            
            # Update UI
            self.update_analysis()
            
            # Show results
            self.results_text.clear()
            self.results_text.append("Successfully converted NFA to DFA.")
            self.results_text.append(f"The DFA has {len(dfa.states)} states and {len(dfa.transitions)} transitions.")
            
            # Update main window
            self.notify_automaton_changed()
        except Exception as e:
            self.results_text.setText(f"Error: {str(e)}")
    
    def make_automaton_complete(self):
        """
        Make the automaton complete.
        """
        if self.analysis_automaton is None:
            show_error(self, "Error", "No automaton to complete. Please load an automaton first.")
            return
        
        try:
            # Check if already complete
            if is_complete(self.analysis_automaton):
                show_info(self, "Info", "The automaton is already complete")
                return
            
            # Make complete
            complete_automaton = make_complete(self.analysis_automaton)
            
            # Update the automaton
            self.analysis_automaton = complete_automaton
            
            # Update UI
            self.update_analysis()
            
            # Show results
            self.results_text.clear()
            self.results_text.append("Successfully made the automaton complete.")
            self.results_text.append(f"Added a sink state and {len(complete_automaton.transitions) - len(self.analysis_automaton.transitions)} transitions.")
            
            # Update main window
            self.notify_automaton_changed()
        except Exception as e:
            self.results_text.setText(f"Error: {str(e)}")
    
    def minimize_automaton(self):
        """
        Minimize the automaton.
        """
        if self.analysis_automaton is None:
            show_error(self, "Error", "No automaton to minimize. Please load an automaton first.")
            return
        
        try:
            # Check if deterministic
            if not is_deterministic(self.analysis_automaton):
                show_error(self, "Error", "Only deterministic automata can be minimized.\nConvert to DFA first.")
                return
            
            # Minimize
            minimized = minimize_automaton(self.analysis_automaton)
            
            # Update the automaton
            self.analysis_automaton = minimized
            
            # Update UI
            self.update_analysis()
            
            # Show results
            self.results_text.clear()
            self.results_text.append("Successfully minimized the automaton.")
            self.results_text.append(f"The minimized automaton has {len(minimized.states)} states and {len(minimized.transitions)} transitions.")
            
            # Update main window
            self.notify_automaton_changed()
        except Exception as e:
            self.results_text.setText(f"Error: {str(e)}")
    
    def notify_automaton_changed(self):
        """
        Notify the parent that the automaton has changed.
        """
        # Update automaton in main window and other pages
        if hasattr(self.window(), "automata_page") and hasattr(self.window().automata_page, "on_automaton_changed"):
            self.window().automata_page.update_automaton(self.analysis_automaton)
        
        if hasattr(self.window(), "advanced_page") and hasattr(self.window().advanced_page, "on_automaton_changed"):
            self.window().advanced_page.update_automaton(self.analysis_automaton)
    
    def save_automaton(self):
        """
        Save the current analysis automaton to a file.
        """
        if not self.analysis_automaton:
            show_warning(self, "No Automaton", "No automaton to save.")
            return
        
        # Show file dialog
        file_path = choose_file_save(
            self,
            "Save Automaton",
            [("JSON Files", "*.json"), ("All Files", "*.*")],
            ".json"
        )
        
        if not file_path:
            return  # Canceled
        
        # Add .json extension if not already present
        if not file_path.endswith(".json"):
            file_path += ".json"
        
        # Save the automaton
        try:
            save_automaton(self.analysis_automaton, file_path)
            self.current_automaton_path = file_path
            show_info(self, "Automaton Saved", f"Automaton saved successfully to {file_path}.")
            
            # Refresh automaton lists
            self.refresh_automaton_list()
        except Exception as e:
            show_error(self, "Error Saving Automaton", str(e))
    
    def delete_automaton(self):
        """
        Delete the selected automaton.
        """
        if self.automaton_combo.count() == 0 or not self.automaton_combo.isEnabled():
            show_warning(self, "No Automaton Selected", "No automaton selected for deletion.")
            return
        
        # Get the selected file path
        file_path = self.automaton_combo.currentData()
        file_name = os.path.basename(file_path)
        
        if not file_path or not os.path.exists(file_path):
            show_error(self, "Error", "Could not find the selected automaton file.")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            f"Are you sure you want to delete '{file_name}'?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            # Delete the file
            os.remove(file_path)
            
            # If the deleted file was currently loaded, reset the analysis view
            if self.current_automaton_path == file_path:
                self.analysis_automaton = None
                self.current_automaton_path = None
                self.update_analysis()
            
            # Refresh automaton lists
            self.refresh_automaton_list()
            
            show_info(self, "Automaton Deleted", f"Automaton {file_name} deleted successfully.")
        except Exception as e:
            show_error(self, "Error Deleting Automaton", str(e)) 