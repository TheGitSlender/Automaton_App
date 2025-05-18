# Automaton App

A Python application for creating, visualizing, and analyzing finite state automata (DFA/NFA) with integrated security features.

## Features

- **Security Features**:
  - User authentication with password hashing
  - Two-factor authentication (2FA) with setup keys
  - Role-based access control
  - Password reset functionality
  - Security event logging
  
- **Automata Tools**:
  - Create and edit automata
  - Visual representation of states and transitions
  - Analyze automata properties (determinism, completeness)
  - Convert NFA to DFA
  - Minimize automata
  - Simulate and test words
  - Set operations (union, intersection, complement)

## System Requirements

- Python 3.7 or higher
- Operating Systems: Windows, macOS, or Linux

## Installation

### Option 1: Using Virtual Environment

1. **Clone repository**:
   ```bash
   git clone https://github.com/TheGitSlender/Automaton_App.git
   cd Automaton_App
   ```

2. **Create and activate virtual environment**:
   
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

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Option 2: Using Conda

1. **Clone repository**:
   ```bash
   git clone https://github.com/TheGitSlender/Automaton_App.git
   cd Automaton_App
   ```

2. **Create and activate conda environment**:
   ```bash
   conda create -n automaton_app python=3.9
   conda activate automaton_app
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Start the application:
```bash
python -m gui.main
```

That's it! No additional setup or installation is needed.

## Using the Application

### Authentication

1. **Login**: Enter your username and password on the login screen
2. **Register**: Click "Register" to create a new account
   - Enable 2FA during registration for enhanced security
   - Copy the displayed secret key into your authenticator app (Google Authenticator, Microsoft Authenticator)
   - You can use the "Copy Secret Key" button to easily copy the key to your clipboard
3. **Password Reset**: Click "Forgot Password" if needed

### Creating and Analyzing Automata

1. **Automata Tab**: Create and edit automata
   - Define alphabet
   - Add states (initial/final)
   - Create transitions

2. **Analysis Tab**: Analyze and transform automata
   - Check determinism/completeness (considers all states including final states)
   - Convert NFA to DFA
   - Minimize automata

3. **Advanced Tab**: Simulation and set operations
   - Test words
   - Generate accepted/rejected words
   - Perform set operations (union, intersection, complement)

## Security Recommendations

- Enable 2FA for all accounts
- Use strong, unique passwords
- Regularly review the security logs
- Each user has specific access rights based on their role

## Project Structure

```
Automaton_App/
├── Automates/          # Saved automata
├── automata/           # Core automata functionality
├── Security/           # Security module
│   └── security/       # Authentication, access control, logs
├── gui/                # GUI components
│   ├── main.py         # Main application entry
│   └── pages/          # Application pages
│   └── widgets/        # Application widgets
└── requirements.txt    # Dependencies
```

## Troubleshooting

- **Login Problems**: Check your username and ensure 2FA code is entered correctly
- **Automata Operations**: Verify that automata have matching alphabets for set operations

Feel free to open an issue if you encounter any kind of problem.
