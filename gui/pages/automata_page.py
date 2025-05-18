
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
    QLabel, QLineEdit, QPushButton, QTabWidget, 
    QFrame, QListWidget, QToolBar, QScrollArea,
    QListWidgetItem, QAbstractItemView
)
from PyQt5.QtCore import Qt, pyqtSignal

from automata.models import State, Alphabet, Transition, Automaton
from automata.storage import save_automaton, load_automaton

from .base_page import BasePage
from ..widgets.tree_canvas import AutomataCanvas
from ..widgets.form import StateForm, TransitionForm
from ..widgets.dialogs import (
    show_info, show_warning, show_error,
    ask_yes_no, choose_file_open, choose_file_save,
    InputDialog
)

# Directory for saving automata before analysis
AUTOMATA_SAVE_DIR = "Automates"

class AutomataPage(BasePage):
    """
    Page for creating, loading, saving, and editing automata.
    """
    # Signal to indicate page switching
    page_exiting = pyqtSignal()
    
    def __init__(self, parent):
        """
        Initialize the page.
        
        Args:
            parent: The parent widget
        """
        # Important: Initialize as QWidget first without setting up layout
        QWidget.__init__(self, parent)
        self.parent = parent
        
        # Shared automaton reference
        self.automaton = None
        
        # Flag to track changes to the automaton
        self.automaton_modified = False
        
        # Current file path for the automaton
        self.current_file_path = None
        
        # Ensure the save directory exists
        os.makedirs(AUTOMATA_SAVE_DIR, exist_ok=True)
        
        # Setup UI
        self.setup_ui()
        
        # Update the UI
        self.update_ui()
        
        # Connect the page exiting signal to save method
        self.page_exiting.connect(self.save_automaton_if_modified)
    
    def setup_ui(self):
        # Create main layout - this is the only layout applied to 'self'
        layout = QVBoxLayout(self)
        
        # Create paned window (splitter)
        self.paned = QSplitter(Qt.Horizontal)
        layout.addWidget(self.paned)
        
        # Left panel: Automaton properties
        self.left_frame = QWidget()
        self.left_layout = QVBoxLayout(self.left_frame)
        self.paned.addWidget(self.left_frame)
        
        # Automaton name
        self.name_frame = QWidget()
        self.name_layout = QHBoxLayout(self.name_frame)
        self.name_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.addWidget(self.name_frame)
        
        name_label = QLabel("Automaton Name:")
        self.name_layout.addWidget(name_label)
        
        self.name_edit = QLineEdit()
        self.name_layout.addWidget(self.name_edit)
        
        name_button = QPushButton("Rename")
        name_button.clicked.connect(self.rename_automaton)
        self.name_layout.addWidget(name_button)
        
        # Alphabet
        self.alphabet_frame = QWidget()
        self.alphabet_layout = QHBoxLayout(self.alphabet_frame)
        self.alphabet_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.addWidget(self.alphabet_frame)
        
        alphabet_label = QLabel("Alphabet:")
        self.alphabet_layout.addWidget(alphabet_label)
        
        self.alphabet_edit = QLineEdit()
        self.alphabet_layout.addWidget(self.alphabet_edit)
        
        alphabet_button = QPushButton("Update")
        alphabet_button.clicked.connect(self.update_alphabet)
        self.alphabet_layout.addWidget(alphabet_button)
        
        # States and transitions notebook
        self.notebook = QTabWidget()
        self.left_layout.addWidget(self.notebook)
        
        # States tab
        self.states_frame = QWidget()
        self.states_layout = QVBoxLayout(self.states_frame)
        self.notebook.addTab(self.states_frame, "States")
        
        # States toolbar
        self.states_toolbar = QWidget()
        self.states_toolbar_layout = QHBoxLayout(self.states_toolbar)
        self.states_toolbar_layout.setContentsMargins(0, 0, 0, 0)
        self.states_layout.addWidget(self.states_toolbar)
        
        add_state_button = QPushButton("Add State")
        add_state_button.setMinimumWidth(100)
        add_state_button.setMinimumHeight(30)
        add_state_button.clicked.connect(self.add_state)
        self.states_toolbar_layout.addWidget(add_state_button)
        
        edit_state_button = QPushButton("Edit State")
        edit_state_button.setMinimumWidth(100)
        edit_state_button.setMinimumHeight(30)
        edit_state_button.clicked.connect(self.edit_state)
        self.states_toolbar_layout.addWidget(edit_state_button)
        
        delete_state_button = QPushButton("Delete State")
        delete_state_button.setMinimumWidth(100)
        delete_state_button.setMinimumHeight(30)
        delete_state_button.clicked.connect(self.delete_state)
        self.states_toolbar_layout.addWidget(delete_state_button)
        
        # States list
        self.states_listbox = QListWidget()
        self.states_listbox.setSelectionMode(QAbstractItemView.SingleSelection)
        self.states_layout.addWidget(self.states_listbox)
        
        # Transitions tab
        self.transitions_frame = QWidget()
        self.transitions_layout = QVBoxLayout(self.transitions_frame)
        self.notebook.addTab(self.transitions_frame, "Transitions")
        
        # Transitions toolbar
        self.transitions_toolbar = QWidget()
        self.transitions_toolbar_layout = QHBoxLayout(self.transitions_toolbar)
        self.transitions_toolbar_layout.setContentsMargins(0, 0, 0, 0)
        self.transitions_layout.addWidget(self.transitions_toolbar)
        
        add_transition_button = QPushButton("Add Transition")
        add_transition_button.setMinimumWidth(120)
        add_transition_button.setMinimumHeight(30)
        add_transition_button.clicked.connect(self.add_transition)
        self.transitions_toolbar_layout.addWidget(add_transition_button)
        
        edit_transition_button = QPushButton("Edit Transition")
        edit_transition_button.setMinimumWidth(120)
        edit_transition_button.setMinimumHeight(30)
        edit_transition_button.clicked.connect(self.edit_transition)
        self.transitions_toolbar_layout.addWidget(edit_transition_button)
        
        delete_transition_button = QPushButton("Delete Transition")
        delete_transition_button.setMinimumWidth(120)
        delete_transition_button.setMinimumHeight(30)
        delete_transition_button.clicked.connect(self.delete_transition)
        self.transitions_toolbar_layout.addWidget(delete_transition_button)
        
        # Transitions list
        self.transitions_listbox = QListWidget()
        self.transitions_listbox.setSelectionMode(QAbstractItemView.SingleSelection)
        self.transitions_layout.addWidget(self.transitions_listbox)
        
        # Right panel: Automaton visualization
        self.right_frame = QWidget()
        self.right_layout = QVBoxLayout(self.right_frame)
        self.paned.addWidget(self.right_frame)
        
        # Canvas for visualization
        self.canvas = AutomataCanvas()
        self.right_layout.addWidget(self.canvas)
        
        # Set the splitter sizes
        self.paned.setSizes([300, 700])
        
        # Bottom toolbar
        self.toolbar = QWidget()
        self.toolbar_layout = QHBoxLayout(self.toolbar)
        self.toolbar_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toolbar)
        
        new_button = QPushButton("New Automaton")
        new_button.setMinimumWidth(130)
        new_button.setMinimumHeight(30)
        new_button.clicked.connect(self.create_new_automaton)
        self.toolbar_layout.addWidget(new_button)
        
        load_button = QPushButton("Load Automaton")
        load_button.setMinimumWidth(130)
        load_button.setMinimumHeight(30)
        load_button.clicked.connect(self.load_automaton)
        self.toolbar_layout.addWidget(load_button)
        
        save_button = QPushButton("Save Automaton")
        save_button.setMinimumWidth(130)
        save_button.setMinimumHeight(30)
        save_button.clicked.connect(self.save_automaton)
        self.toolbar_layout.addWidget(save_button)
        
        # Stretch at the end to align buttons to the left
        self.toolbar_layout.addStretch()
    
    def update_ui(self):
        # Clear the lists
        self.states_listbox.clear()
        self.transitions_listbox.clear()
        
        if self.automaton is None:
            self.name_edit.setText("")
            self.alphabet_edit.setText("")
            self.canvas.update_automaton(None)
            return
        
        # Update name
        self.name_edit.setText(self.automaton.name)
        
        # Update alphabet
        self.alphabet_edit.setText(", ".join(self.automaton.alphabet.symbols))
        
        # Update states list
        for state in self.automaton.states.values():
            label = state.name
            if state.is_initial:
                label = f"→ {label}"
            if state.is_final:
                label = f"{label} *"
            self.states_listbox.addItem(label)
        
        # Update transitions list
        for transition in self.automaton.transitions:
            label = f"{transition.src.name} --({transition.symbol})--> {transition.dest.name}"
            self.transitions_listbox.addItem(label)
        
        # Update canvas
        self.canvas.update_automaton(self.automaton)
        
        # Notify parent
        self.notify_automaton_changed()
        
        # If we updated the UI, it's not considered a modification
        if self.automaton is not None:
            self.automaton_modified = False
    
    def on_automaton_changed(self):
        """
        Handle automaton change event.
        """
        self.update_ui()
    
    def mark_automaton_modified(self):
        """
        Mark the automaton as modified.
        """
        if self.automaton is not None:
            self.automaton_modified = True
    
    def notify_automaton_changed(self):
        """
        Notify the parent that the automaton has changed.
        """
        # Find siblings and update them if they implement on_automaton_changed
        if hasattr(self.window(), "analysis_page") and hasattr(self.window().analysis_page, "on_automaton_changed"):
            self.window().analysis_page.update_automaton(self.automaton)
        
        if hasattr(self.window(), "advanced_page") and hasattr(self.window().advanced_page, "on_automaton_changed"):
            self.window().advanced_page.update_automaton(self.automaton)
        
        # Mark as modified
        self.mark_automaton_modified()
    
    def hideEvent(self, event):
        """
        Handle the hide event when switching away from this tab.
        
        Args:
            event: The hide event
        """
        # Emit the page exiting signal to trigger autosave
        self.page_exiting.emit()
        super().hideEvent(event)
    
    def create_new_automaton(self):
        """
        Create a new automaton.
        """
        # Ask for confirmation if there's already an automaton
        if self.automaton:
            confirm = ask_yes_no(
                self,
                "Create New Automaton",
                "This will discard the current automaton. Continue?"
            )
            if not confirm:
                return
        
        # Ask for a name using InputDialog
        dialog = InputDialog(self, "New Automaton", "Enter automaton name:", "New Automaton")
        name = dialog.get_input()
        
        if not name:
            return  # Canceled
        
        # Ask for alphabet
        dialog = InputDialog(
            self, 
            "Alphabet", 
            "Enter alphabet symbols (comma-separated):", 
            "a, b"
        )
        alphabet_str = dialog.get_input()
        
        if not alphabet_str:
            return  # Canceled
        
        # Parse the alphabet
        alphabet_symbols = [s.strip() for s in alphabet_str.split(",")]
        
        # Create automaton with initial state
        alphabet = Alphabet(alphabet_symbols)
        initial_state = State("q0", True, False)
        states = [initial_state]
        transitions = []
        
        self.automaton = Automaton(name, alphabet, states, transitions)
        
        # Update UI
        self.update_ui()
        
        # Show success message
        show_info(self, "Automaton Created", f"Automaton '{name}' created successfully.")
        
        # Mark as modified
        self.mark_automaton_modified()
    
    def load_automaton(self):
        """
        Load an automaton from a file.
        """
        # Ask for confirmation if there's already an automaton
        if self.automaton:
            confirm = ask_yes_no(
                self,
                "Load Automaton",
                "This will discard the current automaton. Continue?"
            )
            if not confirm:
                return
        
        # Show file dialog
        file_path = choose_file_open(
            self,
            "Load Automaton",
            [("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return  # Canceled
        
        # Load the automaton
        try:
            self.automaton = load_automaton(file_path)
            self.update_ui()
            show_info(self, "Automaton Loaded", f"Automaton loaded successfully from {file_path}.")
            
            # Remember the file path
            self.current_file_path = file_path
            
            # Reset modification flag since we just loaded it
            self.automaton_modified = False
        except Exception as e:
            show_error(self, "Error Loading Automaton", str(e))
    
    def save_automaton(self):
        """
        Save the automaton to a file.
        """
        if not self.automaton:
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
            save_automaton(self.automaton, file_path)
            show_info(self, "Automaton Saved", f"Automaton saved successfully to {file_path}.")
            
            # Update the current file path and reset modified flag
            self.current_file_path = file_path
            self.automaton_modified = False
        except Exception as e:
            show_error(self, "Error Saving Automaton", str(e))
    
    def save_automaton_if_modified(self):
        """
        Save the automaton if it has been modified since the last save.
        This is called automatically when switching away from the tab.
        """
        if not self.automaton or not self.automaton_modified:
            return
        
        # First check if we have a current file path
        if self.current_file_path:
            try:
                save_automaton(self.automaton, self.current_file_path)
                self.automaton_modified = False
                return
            except Exception:
                pass  # If this fails, we'll try with the Automates directory
        
        # If no current file path or saving to it failed, use the Automates directory
        try:
            safe_name = self.automaton.name.replace(" ", "_").replace("/", "_").replace("\\", "_")
            file_path = os.path.join(AUTOMATA_SAVE_DIR, f"{safe_name}.json")
            
            # Save the automaton
            save_automaton(self.automaton, file_path)
            self.current_file_path = file_path
            self.automaton_modified = False
        except Exception as e:
            print(f"Error auto-saving automaton: {str(e)}")
    
    def rename_automaton(self):
        """
        Rename the current automaton.
        """
        if not self.automaton:
            show_warning(self, "No Automaton", "No automaton to rename.")
            return
        
        # Ask for a name using InputDialog
        dialog = InputDialog(
            self, 
            "Rename Automaton", 
            "Enter new automaton name:", 
            self.automaton.name
        )
        name = dialog.get_input()
        
        if not name:
            return  # Canceled
        
        # Update the automaton
        self.automaton.name = name
        
        # Update UI
        self.update_ui()
        
        # Mark as modified
        self.mark_automaton_modified()
    
    def update_alphabet(self):
        """
        Update the alphabet of the current automaton.
        """
        if not self.automaton:
            show_warning(self, "No Automaton", "No automaton to update.")
            return
        
        # Get the current alphabet symbols as comma-separated string
        current_symbols = ", ".join(self.automaton.alphabet.symbols)
        
        # Ask for the new alphabet
        dialog = InputDialog(
            self, 
            "Update Alphabet", 
            "Enter alphabet symbols (comma-separated):", 
            current_symbols
        )
        alphabet_str = dialog.get_input()
        
        if not alphabet_str:
            return  # Canceled
        
        # Parse the alphabet
        new_symbols = [s.strip() for s in alphabet_str.split(",")]
        
        # Check if all symbols in transitions are in the new alphabet
        all_symbols_used = set()
        for transition in self.automaton.transitions:
            all_symbols_used.add(transition.symbol)
        
        symbols_not_in_new = all_symbols_used - set(new_symbols)
        
        if symbols_not_in_new:
            confirm = ask_yes_no(
                self,
                "Warning: Symbols Removed",
                f"The following symbols are used in transitions but are not in the new alphabet: {', '.join(symbols_not_in_new)}. "
                f"This will remove all transitions using these symbols. Continue?"
            )
            if not confirm:
                return
        
        # Update the alphabet
        self.automaton.alphabet = Alphabet(new_symbols)
        
        # Remove transitions with symbols not in the new alphabet
        self.automaton.transitions = [
            t for t in self.automaton.transitions 
            if t.symbol in new_symbols
        ]
        
        # Update UI
        self.update_ui()
        
        # Mark as modified
        self.mark_automaton_modified()
    
    def add_state(self):
        """
        Add a new state to the automaton.
        """
        if not self.automaton:
            show_warning(self, "No Automaton", "No automaton to add a state to.")
            return
        
        # Create a form
        form = StateForm(self, "Add State")
        if form.exec_() == form.Accepted:
            result = form.result
            
            # Check if state name already exists
            if result["name"] in self.automaton.states:
                show_error(self, "Error", f"State '{result['name']}' already exists.")
                return
            
            # Create the state
            state = State(
                result["name"],
                result["is_initial"],
                result["is_final"]
            )
            
            # If this is an initial state, update other states
            if state.is_initial:
                for other_state in self.automaton.states.values():
                    other_state.is_initial = False
            
            # Add the state to the automaton
            self.automaton.add_state(state)
            
            # Update UI
            self.update_ui()
            
            # Mark as modified
            self.mark_automaton_modified()
    
    def edit_state(self):
        """
        Edit the selected state.
        """
        if not self.automaton:
            show_warning(self, "No Automaton", "No automaton to edit a state in.")
            return
        
        # Get the selected state
        selected_items = self.states_listbox.selectedItems()
        if not selected_items:
            show_warning(self, "No Selection", "Please select a state to edit.")
            return
        
        item = selected_items[0]
        index = self.states_listbox.row(item)
        
        # Get the state name (remove initial/final indicators)
        item_text = item.text().replace("→ ", "").replace(" *", "")
        
        # Find the state in the automaton
        state = self.automaton.states.get(item_text)
        if not state:
            show_error(self, "Error", f"State '{item_text}' not found.")
            return
        
        # Create a form to edit the state
        form = StateForm(self, "Edit State", state)
        if form.exec_() == form.Accepted:
            result = form.result
            
            # Check if the new name already exists (if changed)
            if result["name"] != state.name and result["name"] in self.automaton.states:
                show_error(self, "Error", f"State '{result['name']}' already exists.")
                return
            
            # Handle initial state changes
            was_initial = state.is_initial
            will_be_initial = result["is_initial"]
            
            if will_be_initial and not was_initial:
                # This state is becoming initial, update other states
                for other_state in self.automaton.states.values():
                    other_state.is_initial = False
            
            # Update the state
            old_name = state.name
            state.name = result["name"]
            state.is_initial = will_be_initial
            state.is_final = result["is_final"]
            
            # If the name changed, update the states dictionary
            if old_name != state.name:
                del self.automaton.states[old_name]
                self.automaton.states[state.name] = state
            
            # Update UI
            self.update_ui()
            
            # Mark as modified
            self.mark_automaton_modified()
    
    def delete_state(self):
        """
        Delete the selected state.
        """
        if not self.automaton:
            show_warning(self, "No Automaton", "No automaton to delete a state from.")
            return
        
        # Get the selected state
        selected_items = self.states_listbox.selectedItems()
        if not selected_items:
            show_warning(self, "No Selection", "Please select a state to delete.")
            return
        
        item = selected_items[0]
        
        # Get the state name (remove initial/final indicators)
        item_text = item.text().replace("→ ", "").replace(" *", "")
        
        # Find the state in the automaton
        state = self.automaton.states.get(item_text)
        if not state:
            show_error(self, "Error", f"State '{item_text}' not found.")
            return
        
        # Confirm deletion
        confirm = ask_yes_no(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete state '{state.name}'? "
            f"This will also remove all transitions involving this state."
        )
        
        if not confirm:
            return
        
        # Remove transitions involving this state
        self.automaton.transitions = [
            t for t in self.automaton.transitions
            if t.src != state and t.dest != state
        ]
        
        # Remove the state
        del self.automaton.states[state.name]
        
        # Update UI
        self.update_ui()
        
        # Mark as modified
        self.mark_automaton_modified()
    
    def add_transition(self):
        """
        Add a new transition to the automaton.
        """
        if not self.automaton:
            show_warning(self, "No Automaton", "No automaton to add a transition to.")
            return
        
        # Check if there are any states
        if not self.automaton.states:
            show_warning(self, "No States", "Please add some states first.")
            return
        
        # Check if there's an alphabet
        if not self.automaton.alphabet.symbols:
            show_warning(self, "No Alphabet", "Please define an alphabet first.")
            return
        
        # Create a form for the transition
        form = TransitionForm(
            self, 
            "Add Transition",
            list(self.automaton.states.values()),
            self.automaton.alphabet.symbols
        )
        
        if form.exec_() == form.Accepted:
            result = form.result
            
            # Get the states
            src_state = self.automaton.states.get(result["source"])
            dest_state = self.automaton.states.get(result["destination"])
            
            if not src_state or not dest_state:
                show_error(self, "Error", "Source or destination state not found.")
                return
            
            # Create the transition
            transition = Transition(src_state, result["symbol"], dest_state)
            
            # Check if the transition already exists
            for existing in self.automaton.transitions:
                if (existing.src == transition.src and 
                    existing.dest == transition.dest and 
                    existing.symbol == transition.symbol):
                    show_error(self, "Error", "This transition already exists.")
                    return
            
            # Add the transition
            self.automaton.add_transition(transition)
            
            # Update UI
            self.update_ui()
            
            # Mark as modified
            self.mark_automaton_modified()
    
    def edit_transition(self):
        """
        Edit the selected transition.
        """
        if not self.automaton:
            show_warning(self, "No Automaton", "No automaton to edit a transition in.")
            return
        
        # Get the selected transition
        selected_items = self.transitions_listbox.selectedItems()
        if not selected_items:
            show_warning(self, "No Selection", "Please select a transition to edit.")
            return
        
        item = selected_items[0]
        index = self.transitions_listbox.row(item)
        
        if index >= len(self.automaton.transitions):
            show_error(self, "Error", "Selected transition not found.")
            return
        
        transition = self.automaton.transitions[index]
        
        # Create a form to edit the transition
        form = TransitionForm(
            self, 
            "Edit Transition", 
            list(self.automaton.states.values()),
            self.automaton.alphabet.symbols,
            transition
        )
        
        if form.exec_() == form.Accepted:
            result = form.result
            
            # Get the states
            src_state = self.automaton.states.get(result["source"])
            dest_state = self.automaton.states.get(result["destination"])
            
            if not src_state or not dest_state:
                show_error(self, "Error", "Source or destination state not found.")
                return
            
            # Create the new transition
            new_transition = Transition(src_state, result["symbol"], dest_state)
            
            # Check if the new transition would be a duplicate
            for i, existing in enumerate(self.automaton.transitions):
                if (i != index and
                    existing.src == new_transition.src and 
                    existing.dest == new_transition.dest and 
                    existing.symbol == new_transition.symbol):
                    show_error(self, "Error", "This transition would be a duplicate.")
                    return
            
            # Replace the transition
            self.automaton.transitions[index] = new_transition
            
            # Update UI
            self.update_ui()
            
            # Mark as modified
            self.mark_automaton_modified()
    
    def delete_transition(self):
        """
        Delete the selected transition.
        """
        if not self.automaton:
            show_warning(self, "No Automaton", "No automaton to delete a transition from.")
            return
        
        # Get the selected transition
        selected_items = self.transitions_listbox.selectedItems()
        if not selected_items:
            show_warning(self, "No Selection", "Please select a transition to delete.")
            return
        
        item = selected_items[0]
        index = self.transitions_listbox.row(item)
        
        if index >= len(self.automaton.transitions):
            show_error(self, "Error", "Selected transition not found.")
            return
        
        transition = self.automaton.transitions[index]
        
        # Confirm deletion
        confirm = ask_yes_no(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the transition from '{transition.src.name}' "
            f"to '{transition.dest.name}' with symbol '{transition.symbol}'?"
        )
        
        if not confirm:
            return
        
        # Remove the transition
        del self.automaton.transitions[index]
        
        # Update UI
        self.update_ui()
        
        # Mark as modified
        self.mark_automaton_modified()
    
    def delete_selected(self):
        """
        Delete the selected item (state or transition).
        """
        # Determine which tab is active
        current_tab = self.notebook.currentIndex()
        
        if current_tab == 0:  # States tab
            self.delete_state()
        elif current_tab == 1:  # Transitions tab
            self.delete_transition() 