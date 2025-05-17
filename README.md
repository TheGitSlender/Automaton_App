# Automaton App

A Python application for creating, visualizing, and analyzing finite state automata (DFA/NFA).

## Features

- **Create and Edit Automata**: Intuitive interface for defining states and transitions
- **Visualization**: Visual representation of automata with states, transitions, and self-loops
- **Analysis Tools**:
  - Check determinism and completeness
  - Convert NFA to DFA
  - Minimize automata using Hopcroft's algorithm
- **Simulation**:
  - Test words against automata
  - Generate accepted or rejected words
- **Set Operations**:
  - Union of automata
  - Intersection of automata
  - Complement of an automaton
  - Test equivalence between automata
- **File Management**:
  - Save automata to JSON files
  - Load previously saved automata

## System Requirements

- Python 3.7 or higher
- Operating Systems: Windows, macOS, or Linux

## Installation

1. **Clone or download the repository**:
   ```bash
   git clone https://github.com/yourusername/Automaton_App.git
   cd Automaton_App
   ```

2. **Create and activate a virtual environment** (recommended):
   
   For Windows:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
   
   For macOS/Linux:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the application**:
   ```bash
   python -m gui.main
   ```

2. **Navigate between tabs**:
   - **Automata**: Create and edit automata
   - **Analysis**: Analyze properties and transform automata
   - **Advanced**: Simulate and perform set operations

## Using the Application

### Creating an Automaton

1. Click on the "Automata" tab
2. Click "New Automaton" to start a fresh automaton
3. Define the alphabet (e.g., "a,b")
4. Add states using the "Add State" button
   - Set initial state by checking "Initial"
   - Set final states by checking "Final"
5. Add transitions by selecting source state, input symbol, and destination state

### Analyzing an Automaton

1. Click on the "Analysis" tab
2. Click "Load Selected" to load an automaton
3. Use the buttons to:
   - Check determinism
   - Check completeness
   - Convert NFA to DFA
   - Minimize the automaton
4. After transformation, click "Save Transformed Automaton" to save the result

### Working with Set Operations

1. Click on the "Advanced" tab and select the "Set Operations" sub-tab
2. Load automata as "Primary" and "Secondary"
3. Use operation buttons (Union, Intersection, Complement) to perform set operations
4. View the result in the visualization panel
5. Click "Save Current Automaton" to save the result

### Testing Words

1. Click on the "Advanced" tab and select the "Simulation" sub-tab
2. Load an automaton
3. Enter a word in the "Test Word" field and click "Test"
4. For generating words:
   - Set "Max Length" and "Max Count"
   - Click "Generate Accepted Words" or "Generate Rejected Words"

## File Management

- Automata are saved in the "Automates" directory as JSON files
- The application automatically loads available automata from this directory
- Use the "Save" buttons to save your work regularly

## Example Workflow

1. Create a new automaton in the "Automata" tab
2. Define states and transitions
3. Save the automaton
4. Go to the "Analysis" tab to check properties
5. Transform (e.g., minimize) if needed
6. Test words or perform set operations in the "Advanced" tab

## Tips and Tricks

- Final states don't need outgoing transitions for completeness checking
- State names are preserved during minimization when possible
- For complex operations, create intermediate automata and save them
- Use the "Refresh" button to update the automaton list if files are added externally

## Troubleshooting

- If the application doesn't start, ensure all dependencies are installed correctly
- If automata operations produce unexpected results, check that the alphabets match
- For visualization issues, try resizing the window or adjusting the splitters

## Project Structure

```
Automaton_App/
├── Automates/          # Directory for saved automata
├── automata/           # Core automata functionality
│   ├── models.py       # Data models for automata
│   ├── operations.py   # Operations on automata
│   ├── storage.py      # Serialization/deserialization
│   └── simulation.py   # Simulation and word generation
├── gui/                # GUI components
│   ├── main.py         # Main application entry point
│   ├── pages/          # Application pages
│   │   ├── automata_page.py  # Automaton creation/editing
│   │   ├── analysis_page.py  # Analysis and transformations
│   │   └── advanced_page.py  # Simulation and set operations
│   └── widgets/        # Reusable UI components
│       ├── dialogs.py  # Dialog utilities
│       └── tree_canvas.py  # Canvas for visualizing automata
└── requirements.txt    # Project dependencies
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
