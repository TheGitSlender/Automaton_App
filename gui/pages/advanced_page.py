
import os
import glob
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QPushButton, QLineEdit, QTextEdit, 
    QGroupBox, QTabWidget, QComboBox
)
from PyQt5.QtCore import Qt

from automata.simulation import (
    simulate, generate_accepted_words, generate_rejected_words
)
from automata.operations import (
    union, intersection, complement, are_equivalent
)
from automata.storage import load_automaton, save_automaton

from .base_page import BasePage
from ..widgets.tree_canvas import AutomataCanvas
from ..widgets.dialogs import (
    show_info, show_error, InputDialog, choose_file_open, choose_file_save,
    show_warning, ask_yes_no
)

# Directory for saving automata
AUTOMATA_SAVE_DIR = "Automates"

class AdvancedPage(BasePage):
    def __init__(self, parent):
        # Important: Initialize as QWidget first without setting up layout
        QWidget.__init__(self, parent)
        self.parent = parent
        
        # Reference to the current automaton (shared across pages)
        self.automaton = None
        
        # Reference to the loaded automatons for operations
        self.primary_automaton = None
        self.secondary_automaton = None
        self.result_automaton = None
        
        # Current file paths
        self.primary_automaton_path = None
        self.secondary_automaton_path = None
        
        # Ensure the save directory exists
        os.makedirs(AUTOMATA_SAVE_DIR, exist_ok=True)
        
        # Set up the UI
        self.setup_ui()
    
    def setup_ui(self):
        # Create main layout
        layout = QVBoxLayout(self)
        
        # Create notebook for tabs
        self.notebook = QTabWidget()
        layout.addWidget(self.notebook)
        
        # Simulation tab
        simulation_tab = QWidget()
        self.notebook.addTab(simulation_tab, "Simulation")
        self.setup_simulation_tab(simulation_tab)
        
        # Set Operations tab
        set_ops_tab = QWidget()
        self.notebook.addTab(set_ops_tab, "Set Operations")
        self.setup_set_operations_tab(set_ops_tab)
        
        # Store reference to both splitters to keep layout consistent
        self.simulation_splitter = simulation_tab.layout().itemAt(0).widget()
        self.set_ops_splitter = set_ops_tab.layout().itemAt(0).widget()
        
        # Set the current splitter based on active tab
        self.splitter = self.simulation_splitter
        self.notebook.currentChanged.connect(self.on_tab_changed)
    
    def setup_simulation_tab(self, parent):
        # Create layout for the tab
        layout = QVBoxLayout(parent)
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel: Simulation options
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Set fixed width for left panel to prevent stretching
        left_panel.setMinimumWidth(300)
        left_panel.setMaximumWidth(350)
        
        splitter.addWidget(left_panel)
        
        # Automaton selection group
        selection_group = QGroupBox("Automaton Selection")
        selection_layout = QVBoxLayout(selection_group)
        
        # Automaton dropdown and refresh button
        automaton_frame = QWidget()
        automaton_layout = QHBoxLayout(automaton_frame)
        automaton_layout.setContentsMargins(0, 0, 0, 0)
        
        self.sim_automaton_combo = QComboBox()
        automaton_layout.addWidget(self.sim_automaton_combo)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_automaton_list)
        automaton_layout.addWidget(refresh_button)
        
        selection_layout.addWidget(automaton_frame)
        
        # Load and save buttons
        buttons_frame = QWidget()
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        load_button = QPushButton("Load Selected")
        load_button.clicked.connect(lambda: self.load_selected_automaton("simulation"))
        buttons_layout.addWidget(load_button)
        
        save_button = QPushButton("Save Automaton")
        save_button.clicked.connect(lambda: self.save_automaton("simulation"))
        buttons_layout.addWidget(save_button)
        
        selection_layout.addWidget(buttons_frame)
        
        new_button = QPushButton("New Automaton")
        new_button.clicked.connect(self.create_new_automaton)
        selection_layout.addWidget(new_button)
        
        left_layout.addWidget(selection_group)
        
        # Word Testing group
        testing_group = QGroupBox("Word Testing")
        testing_layout = QVBoxLayout(testing_group)
        left_layout.addWidget(testing_group)
        
        # Test word input
        test_word_widget = QWidget()
        test_word_layout = QHBoxLayout(test_word_widget)
        test_word_layout.setContentsMargins(0, 0, 0, 0)
        
        test_word_label = QLabel("Test Word:")
        test_word_layout.addWidget(test_word_label)
        
        self.test_word_edit = QLineEdit()
        test_word_layout.addWidget(self.test_word_edit)
        
        test_button = QPushButton("Test")
        test_button.clicked.connect(self.test_word)
        test_word_layout.addWidget(test_button)
        
        testing_layout.addWidget(test_word_widget)
        
        # Test result
        test_result_widget = QWidget()
        test_result_layout = QHBoxLayout(test_result_widget)
        test_result_layout.setContentsMargins(0, 0, 0, 0)
        
        test_result_label = QLabel("Result:")
        test_result_layout.addWidget(test_result_label)
        
        self.test_result_label = QLabel("")
        self.test_result_label.setMinimumWidth(100)
        test_result_layout.addWidget(self.test_result_label)
        
        test_result_layout.addStretch()
        
        testing_layout.addWidget(test_result_widget)
        
        # Word Generation group
        generation_group = QGroupBox("Word Generation")
        generation_layout = QVBoxLayout(generation_group)
        left_layout.addWidget(generation_group)
        
        # Max word length
        length_widget = QWidget()
        length_layout = QHBoxLayout(length_widget)
        length_layout.setContentsMargins(0, 0, 0, 0)
        
        length_label = QLabel("Max Length:")
        length_layout.addWidget(length_label)
        
        self.max_length_edit = QLineEdit("5")
        self.max_length_edit.setMaximumWidth(50)
        length_layout.addWidget(self.max_length_edit)
        
        length_layout.addStretch()
        
        generation_layout.addWidget(length_widget)
        
        # Max count
        count_widget = QWidget()
        count_layout = QHBoxLayout(count_widget)
        count_layout.setContentsMargins(0, 0, 0, 0)
        
        count_label = QLabel("Max Count:")
        count_layout.addWidget(count_label)
        
        self.max_count_edit = QLineEdit("10")
        self.max_count_edit.setMaximumWidth(50)
        count_layout.addWidget(self.max_count_edit)
        
        count_layout.addStretch()
        
        generation_layout.addWidget(count_widget)
        
        # Generation buttons
        generate_accepted_button = QPushButton("Generate Accepted Words")
        generate_accepted_button.clicked.connect(lambda: self.generate_words(True))
        generation_layout.addWidget(generate_accepted_button)
        
        generate_rejected_button = QPushButton("Generate Rejected Words")
        generate_rejected_button.clicked.connect(lambda: self.generate_words(False))
        generation_layout.addWidget(generate_rejected_button)
        
        # Add stretch to push widgets to the top
        left_layout.addStretch()
        
        # Right panel: Results
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        splitter.addWidget(right_panel)
        
        # Automaton visualization
        self.sim_canvas = AutomataCanvas()
        right_layout.addWidget(self.sim_canvas)
        
        # Results group
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout(results_group)
        
        # Results text area
        self.sim_results_text = QTextEdit()
        self.sim_results_text.setReadOnly(True)
        results_layout.addWidget(self.sim_results_text)
        
        right_layout.addWidget(results_group)
        
        # Set the splitter sizes
        splitter.setSizes([300, 700])
    
    def setup_set_operations_tab(self, parent):
        # Create layout for the tab
        layout = QVBoxLayout(parent)
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel: Set operations
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Set fixed width for left panel to prevent stretching
        left_panel.setMinimumWidth(300)
        left_panel.setMaximumWidth(350)
        
        splitter.addWidget(left_panel)
        
        # Primary automaton selection group
        primary_group = QGroupBox("Primary Automaton")
        primary_layout = QVBoxLayout(primary_group)
        
        # Automaton dropdown and refresh button
        primary_frame = QWidget()
        primary_frame_layout = QHBoxLayout(primary_frame)
        primary_frame_layout.setContentsMargins(0, 0, 0, 0)
        
        self.primary_automaton_combo = QComboBox()
        primary_frame_layout.addWidget(self.primary_automaton_combo)
        
        primary_refresh_button = QPushButton("Refresh")
        primary_refresh_button.clicked.connect(self.refresh_automaton_list)
        primary_frame_layout.addWidget(primary_refresh_button)
        
        primary_layout.addWidget(primary_frame)
        
        # Load button
        primary_load_button = QPushButton("Load Selected as Primary")
        primary_load_button.clicked.connect(lambda: self.load_selected_automaton("primary"))
        primary_layout.addWidget(primary_load_button)
        
        left_layout.addWidget(primary_group)
        
        # Secondary automaton selection group
        secondary_group = QGroupBox("Secondary Automaton")
        secondary_layout = QVBoxLayout(secondary_group)
        
        # Secondary automaton dropdown
        secondary_frame = QWidget()
        secondary_frame_layout = QHBoxLayout(secondary_frame)
        secondary_frame_layout.setContentsMargins(0, 0, 0, 0)
        
        self.secondary_automaton_combo = QComboBox()
        secondary_frame_layout.addWidget(self.secondary_automaton_combo)
        
        secondary_refresh_button = QPushButton("Refresh")
        secondary_refresh_button.clicked.connect(self.refresh_automaton_list)
        secondary_frame_layout.addWidget(secondary_refresh_button)
        
        secondary_layout.addWidget(secondary_frame)
        
        # Load button
        secondary_load_button = QPushButton("Load Selected as Secondary")
        secondary_load_button.clicked.connect(lambda: self.load_selected_automaton("secondary"))
        secondary_layout.addWidget(secondary_load_button)
        
        left_layout.addWidget(secondary_group)
        
        # File operations group
        file_ops_group = QGroupBox("File Operations")
        file_ops_layout = QVBoxLayout(file_ops_group)
        
        new_button = QPushButton("New Automaton")
        new_button.clicked.connect(self.create_new_automaton)
        file_ops_layout.addWidget(new_button)
        
        save_button = QPushButton("Save Result Automaton")
        save_button.clicked.connect(lambda: self.save_automaton("result"))
        file_ops_layout.addWidget(save_button)
        
        left_layout.addWidget(file_ops_group)
        
        # Operations group
        operations_group = QGroupBox("Operations")
        operations_layout = QVBoxLayout(operations_group)
        left_layout.addWidget(operations_group)
        
        # Status labels
        primary_status_frame = QWidget()
        primary_status_layout = QHBoxLayout(primary_status_frame)
        primary_status_layout.setContentsMargins(0, 0, 0, 0)
        
        primary_status_label = QLabel("Primary:")
        primary_status_layout.addWidget(primary_status_label)
        
        self.primary_automaton_label = QLabel("None")
        primary_status_layout.addWidget(self.primary_automaton_label)
        
        operations_layout.addWidget(primary_status_frame)
        
        secondary_status_frame = QWidget()
        secondary_status_layout = QHBoxLayout(secondary_status_frame)
        secondary_status_layout.setContentsMargins(0, 0, 0, 0)
        
        secondary_status_label = QLabel("Secondary:")
        secondary_status_layout.addWidget(secondary_status_label)
        
        self.secondary_automaton_label = QLabel("None")
        secondary_status_layout.addWidget(self.secondary_automaton_label)
        
        operations_layout.addWidget(secondary_status_frame)
        
        # Operations buttons
        union_button = QPushButton("Union")
        union_button.clicked.connect(self.perform_union)
        operations_layout.addWidget(union_button)
        
        intersection_button = QPushButton("Intersection")
        intersection_button.clicked.connect(self.perform_intersection)
        operations_layout.addWidget(intersection_button)
        
        complement_button = QPushButton("Complement")
        complement_button.clicked.connect(self.perform_complement)
        operations_layout.addWidget(complement_button)
        
        equivalence_button = QPushButton("Test Equivalence")
        equivalence_button.clicked.connect(self.test_equivalence)
        operations_layout.addWidget(equivalence_button)
        
        # Right panel: Multiple canvases and results
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        splitter.addWidget(right_panel)
        
        # Create a horizontal layout for the three canvases
        canvases_layout = QHBoxLayout()
        
        # Primary automaton visualization
        primary_canvas_group = QGroupBox("Primary Automaton")
        primary_canvas_layout = QVBoxLayout(primary_canvas_group)
        self.primary_canvas = AutomataCanvas()
        primary_canvas_layout.addWidget(self.primary_canvas)
        canvases_layout.addWidget(primary_canvas_group)
        
        # Secondary automaton visualization
        secondary_canvas_group = QGroupBox("Secondary Automaton")
        secondary_canvas_layout = QVBoxLayout(secondary_canvas_group)
        self.secondary_canvas = AutomataCanvas()
        secondary_canvas_layout.addWidget(self.secondary_canvas)
        canvases_layout.addWidget(secondary_canvas_group)
        
        # Result automaton visualization
        result_canvas_group = QGroupBox("Result Automaton")
        result_canvas_layout = QVBoxLayout(result_canvas_group)
        self.result_canvas = AutomataCanvas()
        result_canvas_layout.addWidget(self.result_canvas)
        canvases_layout.addWidget(result_canvas_group)
        
        # Add canvases layout to the right panel
        right_layout.addLayout(canvases_layout)
        
        # Results group
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout(results_group)
        
        # Results text area
        self.set_ops_results_text = QTextEdit()
        self.set_ops_results_text.setReadOnly(True)
        results_layout.addWidget(self.set_ops_results_text)
        
        right_layout.addWidget(results_group)
        
        # Set the splitter sizes
        splitter.setSizes([300, 700])
        
        # Store reference to the old canvas for compatibility
        self.set_ops_canvas = self.result_canvas
    
    def refresh_automaton_list(self):
        # Clear all combo boxes
        self.sim_automaton_combo.clear()
        self.primary_automaton_combo.clear()
        self.secondary_automaton_combo.clear()
        
        # Get all JSON files in the Automates directory
        automaton_files = glob.glob(os.path.join(AUTOMATA_SAVE_DIR, "*.json"))
        
        if not automaton_files:
            # If no files are found, disable combo boxes
            self.sim_automaton_combo.addItem("No automata available")
            self.sim_automaton_combo.setEnabled(False)
            
            self.primary_automaton_combo.addItem("No automata available")
            self.primary_automaton_combo.setEnabled(False)
            
            self.secondary_automaton_combo.addItem("No automata available")
            self.secondary_automaton_combo.setEnabled(False)
            return
        
        # Enable combo boxes
        self.sim_automaton_combo.setEnabled(True)
        self.primary_automaton_combo.setEnabled(True)
        self.secondary_automaton_combo.setEnabled(True)
        
        # Add each file to all combo boxes
        for file_path in automaton_files:
            file_name = os.path.basename(file_path)
            self.sim_automaton_combo.addItem(file_name, file_path)
            self.primary_automaton_combo.addItem(file_name, file_path)
            self.secondary_automaton_combo.addItem(file_name, file_path)
        
        # Select the first item in each combo box
        self.sim_automaton_combo.setCurrentIndex(0)
        self.primary_automaton_combo.setCurrentIndex(0)
        self.secondary_automaton_combo.setCurrentIndex(0)
    
    def load_selected_automaton(self, target):
        """
        Load the selected automaton for the specified target.
        
        Args:
            target: The target to load for ("simulation", "primary", or "secondary")
        """
        if target == "simulation":
            combo_box = self.sim_automaton_combo
        elif target == "primary":
            combo_box = self.primary_automaton_combo
        elif target == "secondary":
            combo_box = self.secondary_automaton_combo
        else:
            return
        
        if combo_box.count() == 0 or not combo_box.isEnabled():
            show_warning(self, "No Automaton Available", "No automaton files available for loading.")
            return
        
        # Get the selected file path
        file_path = combo_box.currentData()
        
        if not file_path or not os.path.exists(file_path):
            show_error(self, "Error", "Could not find the selected automaton file.")
            return
        
        try:
            # Load the automaton
            loaded_automaton = load_automaton(file_path)
            
            # Update the appropriate reference
            if target == "simulation":
                self.primary_automaton = loaded_automaton
                self.primary_automaton_path = file_path
                self.sim_canvas.update_automaton(loaded_automaton)
                show_info(self, "Automaton Loaded", f"Loaded {os.path.basename(file_path)} for simulation.")
                
            elif target == "primary":
                self.primary_automaton = loaded_automaton
                self.primary_automaton_path = file_path
                self.primary_canvas.update_automaton(loaded_automaton)
                self.primary_automaton_label.setText(os.path.basename(file_path))
                show_info(self, "Automaton Loaded", f"Loaded {os.path.basename(file_path)} as primary automaton.")
                
            elif target == "secondary":
                self.secondary_automaton = loaded_automaton
                self.secondary_automaton_path = file_path
                self.secondary_canvas.update_automaton(loaded_automaton)
                self.secondary_automaton_label.setText(os.path.basename(file_path))
                show_info(self, "Automaton Loaded", f"Loaded {os.path.basename(file_path)} as secondary automaton.")
                
        except Exception as e:
            show_error(self, "Error Loading Automaton", str(e))
    
    def create_new_automaton(self):
        # Delegate to the automata page
        if hasattr(self.window(), "automata_page") and hasattr(self.window().automata_page, "create_new_automaton"):
            self.window().automata_page.create_new_automaton()
            # Switch to the automata tab
            self.window().notebook.setCurrentIndex(0)
    
    def save_automaton(self, source):
        automaton_to_save = None
        
        if source == "simulation":
            automaton_to_save = self.primary_automaton
        elif source == "set_ops":
            automaton_to_save = self.primary_automaton
        elif source == "result":
            # Get the result automaton that's displayed on the result canvas
            result_automaton = getattr(self, "result_automaton", None)
            if result_automaton:
                automaton_to_save = result_automaton
            else:
                show_warning(self, "No Result", "No result automaton available to save.")
                return
        
        if not automaton_to_save:
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
            save_automaton(automaton_to_save, file_path)
            show_info(self, "Automaton Saved", f"Automaton saved successfully to {file_path}.")
            
            # Refresh automaton lists
            self.refresh_automaton_list()
            
        except Exception as e:
            show_error(self, "Error Saving Automaton", str(e))
    
    def on_automaton_changed(self):
        self.automaton = self.window().automata_page.automaton if hasattr(self.window(), "automata_page") else None
        self.refresh_automaton_list()
        self.update_advanced()
    
    def update_advanced(self):
        # Clear results
        self.sim_results_text.clear()
        self.set_ops_results_text.clear()
        
        # Update canvas if needed
        if self.notebook.currentIndex() == 0:  # Simulation tab
            self.sim_canvas.update_automaton(self.primary_automaton)
        else:  # Set Operations tab
            # Update all three canvases with their respective automata
            self.primary_canvas.update_automaton(self.primary_automaton)
            self.secondary_canvas.update_automaton(self.secondary_automaton)
            # Only update result canvas if there's a result automaton
            if self.result_automaton:
                self.result_canvas.update_automaton(self.result_automaton)
            else:
                # Clear the result canvas if no result automaton
                self.result_canvas.clear_automaton()
    
    def test_word(self):
        if not self.primary_automaton:
            show_error(self, "Error", "No automaton loaded for simulation.")
            return
        
        # Get the word from the input field
        word = self.test_word_edit.text().strip()
        if not word and word != "":
            show_warning(self, "Empty Word", "Please enter a word to test.")
            return
        
        try:
            # Run the simulation
            accepted = simulate(self.primary_automaton, word)
            
            # Update the result label
            self.test_result_label.setText("Accepted" if accepted else "Rejected")
            
            # Update results text
            self.sim_results_text.clear()
            self.sim_results_text.append(f"Word: '{word}'")
            self.sim_results_text.append(f"Result: {'Accepted' if accepted else 'Rejected'}")
            
            # Include automaton info
            self.sim_results_text.append(f"\nAutomaton: {self.primary_automaton.name}")
            self.sim_results_text.append(f"States: {len(self.primary_automaton.states)}")
            self.sim_results_text.append(f"Alphabet: {', '.join(self.primary_automaton.alphabet.symbols)}")
        
        except Exception as e:
            self.test_result_label.setText("Error")
            self.sim_results_text.setText(f"Error: {str(e)}")
    
    def generate_words(self, accepted=True):
        if not self.primary_automaton:
            show_error(self, "Error", "No automaton loaded for simulation.")
            return
        
        try:
            # Parse the max length and count
            try:
                max_length = int(self.max_length_edit.text().strip())
                if max_length <= 0:
                    raise ValueError("Max length must be positive")
            except ValueError:
                show_error(self, "Invalid Input", "Max length must be a positive integer.")
                return
            
            try:
                max_count = int(self.max_count_edit.text().strip())
                if max_count <= 0:
                    raise ValueError("Max count must be positive")
            except ValueError:
                show_error(self, "Invalid Input", "Max count must be a positive integer.")
                return
            
            # Generate words
            if accepted:
                words = generate_accepted_words(self.primary_automaton, max_length, max_count)
                word_type = "Accepted"
            else:
                words = generate_rejected_words(self.primary_automaton, max_length, max_count)
                word_type = "Rejected"
            
            # Update results text
            self.sim_results_text.clear()
            self.sim_results_text.append(f"{word_type} Words (max length: {max_length}, max count: {max_count}):")
            
            if not words:
                self.sim_results_text.append("\nNo words generated.")
            else:
                for word in words:
                    self.sim_results_text.append(f"- '{word}'")
            
            # Include automaton info
            self.sim_results_text.append(f"\nAutomaton: {self.primary_automaton.name}")
        
        except Exception as e:
            self.sim_results_text.setText(f"Error: {str(e)}")
    
    def perform_union(self):
        if not self.primary_automaton or not self.secondary_automaton:
            show_error(self, "Error", "Both primary and secondary automata must be loaded.")
            return
        
        # Store the current splitter sizes
        splitter_sizes = self.splitter.sizes() if hasattr(self, 'splitter') else None
        
        try:
            # Get the short names of automata for display
            primary_name = self.primary_automaton.name.split('_')[0] if '_' in self.primary_automaton.name else self.primary_automaton.name
            secondary_name = self.secondary_automaton.name.split('_')[0] if '_' in self.secondary_automaton.name else self.secondary_automaton.name
            
            result = union(self.primary_automaton, self.secondary_automaton)
            
            # Store the result without changing the primary automaton
            self.result_automaton = result
            
            # Use a clean name for display
            display_name = result.name.split('_')[0] if '_' in result.name else result.name
            
            # Update result canvas only
            self.result_canvas.update_automaton(result)
            
            # Update results text
            self.set_ops_results_text.clear()
            self.set_ops_results_text.append(f"Union of '{primary_name}' and '{secondary_name}'")
            self.set_ops_results_text.append(f"\nResult: '{display_name}'")
            self.set_ops_results_text.append(f"States: {len(result.states)}")
            self.set_ops_results_text.append(f"Transitions: {len(result.transitions)}")
            self.set_ops_results_text.append(f"Alphabet: {', '.join(result.alphabet.symbols)}")
            
        except Exception as e:
            self.set_ops_results_text.setText(f"Error: {str(e)}")
            
        # Restore the splitter sizes
        if splitter_sizes:
            self.notebook.currentWidget().layout().itemAt(0).widget().setSizes(splitter_sizes)
    
    def perform_intersection(self):
        if not self.primary_automaton or not self.secondary_automaton:
            show_error(self, "Error", "Both primary and secondary automata must be loaded.")
            return
        
        # Store the current splitter sizes
        splitter_sizes = self.splitter.sizes() if hasattr(self, 'splitter') else None
        
        try:
            # Get the short names of automata for display
            primary_name = self.primary_automaton.name.split('_')[0] if '_' in self.primary_automaton.name else self.primary_automaton.name
            secondary_name = self.secondary_automaton.name.split('_')[0] if '_' in self.secondary_automaton.name else self.secondary_automaton.name
            
            result = intersection(self.primary_automaton, self.secondary_automaton)
            
            # Store the result without changing the primary automaton
            self.result_automaton = result
            
            # Use a clean name for display
            display_name = result.name.split('_')[0] if '_' in result.name else result.name
            
            # Update result canvas only
            self.result_canvas.update_automaton(result)
            
            # Update results text
            self.set_ops_results_text.clear()
            self.set_ops_results_text.append(f"Intersection of '{primary_name}' and '{secondary_name}'")
            self.set_ops_results_text.append(f"\nResult: '{display_name}'")
            self.set_ops_results_text.append(f"States: {len(result.states)}")
            self.set_ops_results_text.append(f"Transitions: {len(result.transitions)}")
            self.set_ops_results_text.append(f"Alphabet: {', '.join(result.alphabet.symbols)}")
            
        except Exception as e:
            self.set_ops_results_text.setText(f"Error: {str(e)}")
            
        # Restore the splitter sizes
        if splitter_sizes:
            self.notebook.currentWidget().layout().itemAt(0).widget().setSizes(splitter_sizes)
    
    def perform_complement(self):
        if not self.primary_automaton:
            show_error(self, "Error", "Primary automaton must be loaded.")
            return
        
        # Store the current splitter sizes
        splitter_sizes = self.splitter.sizes() if hasattr(self, 'splitter') else None
        
        try:
            # Get the short name of automaton for display
            primary_name = self.primary_automaton.name.split('_')[0] if '_' in self.primary_automaton.name else self.primary_automaton.name
            
            result = complement(self.primary_automaton)
            
            # Store the result without changing the primary automaton
            self.result_automaton = result
            
            # Use a clean name for display
            display_name = result.name.split('_')[0] if '_' in result.name else result.name
            
            # Update result canvas only
            self.result_canvas.update_automaton(result)
            
            # Update results text
            self.set_ops_results_text.clear()
            self.set_ops_results_text.append(f"Complement of '{primary_name}'")
            self.set_ops_results_text.append(f"\nResult: '{display_name}'")
            self.set_ops_results_text.append(f"States: {len(result.states)}")
            self.set_ops_results_text.append(f"Transitions: {len(result.transitions)}")
            self.set_ops_results_text.append(f"Alphabet: {', '.join(result.alphabet.symbols)}")
            
        except Exception as e:
            self.set_ops_results_text.setText(f"Error: {str(e)}")
            
        # Restore the splitter sizes
        if splitter_sizes:
            self.notebook.currentWidget().layout().itemAt(0).widget().setSizes(splitter_sizes)
    
    def test_equivalence(self):
        if not self.primary_automaton or not self.secondary_automaton:
            show_error(self, "Error", "Both primary and secondary automata must be loaded.")
            return
        
        # Store the current splitter sizes
        splitter_sizes = self.splitter.sizes() if hasattr(self, 'splitter') else None
        
        try:
            # Get the short names of automata for display
            primary_name = self.primary_automaton.name.split('_')[0] if '_' in self.primary_automaton.name else self.primary_automaton.name
            secondary_name = self.secondary_automaton.name.split('_')[0] if '_' in self.secondary_automaton.name else self.secondary_automaton.name
            
            equivalent = are_equivalent(self.primary_automaton, self.secondary_automaton)
            
            # Clear the result canvas since there's no result automaton
            self.result_automaton = None
            self.result_canvas.clear_automaton()
            
            # Update results text
            self.set_ops_results_text.clear()
            self.set_ops_results_text.append(f"Equivalence test between:")
            self.set_ops_results_text.append(f"- '{primary_name}'")
            self.set_ops_results_text.append(f"- '{secondary_name}'")
            self.set_ops_results_text.append(f"\nResult: {'Equivalent' if equivalent else 'Not Equivalent'}")
            
        except Exception as e:
            self.set_ops_results_text.setText(f"Error: {str(e)}")
            
        # Restore the splitter sizes
        if splitter_sizes:
            self.notebook.currentWidget().layout().itemAt(0).widget().setSizes(splitter_sizes)
    
    def notify_automaton_changed(self):
        # Update automaton in main window and other pages
        if hasattr(self.window(), "automata_page") and hasattr(self.window().automata_page, "on_automaton_changed"):
            self.window().automata_page.update_automaton(self.automaton)
        
        if hasattr(self.window(), "analysis_page") and hasattr(self.window().analysis_page, "on_automaton_changed"):
            self.window().analysis_page.update_automaton(self.automaton)
    
    def on_tab_changed(self, index):
        if index == 0:  # Simulation tab
            self.splitter = self.simulation_splitter
        else:  # Set Operations tab
            self.splitter = self.set_ops_splitter 