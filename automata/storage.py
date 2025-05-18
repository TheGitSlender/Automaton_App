"""
Functions for loading and saving automata to/from JSON files.
"""
import json
import os
from typing import Dict, List, Any, Optional, Union, TextIO

from .models import State, Alphabet, Transition, Automaton


def save_automaton(automaton: Automaton, file_path: str) -> None:
    # Create JSON representation
    data = {
        "name": automaton.name,
        "alphabet": automaton.alphabet.symbols,
        "states": list(automaton.states.keys()),
        "initial": automaton.get_initial().name,
        "finals": [s.name for s in automaton.get_finals()],
        "transitions": [
            [t.src.name, t.symbol, t.dest.name] for t in automaton.transitions
        ],
        "creator_id": automaton.creator_id  # Add creator_id to the saved data
    }
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    # Write to file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def load_automaton(file_path: str) -> Automaton:
    # Read from file
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Validate required fields
    required_fields = ["name", "alphabet", "states", "initial", "finals", "transitions"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    # Get creator_id (might be missing in older files)
    creator_id = data.get("creator_id")
    
    # Create states
    states = []
    for state_name in data["states"]:
        is_initial = state_name == data["initial"]
        is_final = state_name in data["finals"]
        states.append(State(state_name, is_initial, is_final))
    
    # Create alphabet
    alphabet = Alphabet(data["alphabet"])
    
    # Create state lookup for transitions
    state_lookup = {s.name: s for s in states}
    
    # Create transitions
    transitions = []
    for t_data in data["transitions"]:
        if len(t_data) != 3:
            raise ValueError(f"Invalid transition format: {t_data}")
        
        src_name, symbol, dest_name = t_data
        
        if src_name not in state_lookup:
            raise ValueError(f"Unknown source state: {src_name}")
        if dest_name not in state_lookup:
            raise ValueError(f"Unknown destination state: {dest_name}")
        if symbol not in alphabet:
            raise ValueError(f"Symbol not in alphabet: {symbol}")
        
        transitions.append(Transition(
            state_lookup[src_name],
            symbol,
            state_lookup[dest_name]
        ))
    
    # Create automaton
    return Automaton(data["name"], alphabet, states, transitions, creator_id)


def automaton_to_dict(automaton: Automaton) -> Dict[str, Any]:
    return {
        "name": automaton.name,
        "alphabet": automaton.alphabet.symbols,
        "states": list(automaton.states.keys()),
        "initial": automaton.get_initial().name,
        "finals": [s.name for s in automaton.get_finals()],
        "transitions": [
            [t.src.name, t.symbol, t.dest.name] for t in automaton.transitions
        ],
        "creator_id": automaton.creator_id
    }


def dict_to_automaton(data: Dict[str, Any]) -> Automaton:
    # Validate required fields
    required_fields = ["name", "alphabet", "states", "initial", "finals", "transitions"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    # Get creator_id (optional)
    creator_id = data.get("creator_id")
    
    # Create states
    states = []
    for state_name in data["states"]:
        is_initial = state_name == data["initial"]
        is_final = state_name in data["finals"]
        states.append(State(state_name, is_initial, is_final))
    
    # Create alphabet
    alphabet = Alphabet(data["alphabet"])
    
    # Create state lookup for transitions
    state_lookup = {s.name: s for s in states}
    
    # Create transitions
    transitions = []
    for t_data in data["transitions"]:
        if len(t_data) != 3:
            raise ValueError(f"Invalid transition format: {t_data}")
        
        src_name, symbol, dest_name = t_data
        
        if src_name not in state_lookup:
            raise ValueError(f"Unknown source state: {src_name}")
        if dest_name not in state_lookup:
            raise ValueError(f"Unknown destination state: {dest_name}")
        if symbol not in alphabet:
            raise ValueError(f"Symbol not in alphabet: {symbol}")
        
        transitions.append(Transition(
            state_lookup[src_name],
            symbol,
            state_lookup[dest_name]
        ))
    
    # Create automaton
    return Automaton(data["name"], alphabet, states, transitions, creator_id) 