"""
Automata Module for defining, manipulating, and simulating finite automata.
"""

from .models import State, Alphabet, Transition, Automaton
from .operations import (
    is_deterministic, is_complete, nfa_to_dfa, minimize_automaton,
    union, intersection, complement, are_equivalent
)
from .simulation import simulate, generate_accepted_words, generate_rejected_words
from .storage import save_automaton, load_automaton

__all__ = [
    'State', 'Alphabet', 'Transition', 'Automaton',
    'is_deterministic', 'is_complete', 'nfa_to_dfa', 'minimize_automaton',
    'union', 'intersection', 'complement', 'are_equivalent',
    'simulate', 'generate_accepted_words', 'generate_rejected_words',
    'save_automaton', 'load_automaton'
] 