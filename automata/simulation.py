from typing import List, Set, Tuple, Optional, Generator
from collections import deque
import random

from .models import Automaton
from .operations import is_deterministic, nfa_to_dfa

# Maximum length for generated words
MAX_WORD_LENGTH = 10
# Maximum attempts when generating words
MAX_ATTEMPTS = 1000


def simulate(automaton: Automaton, word: str) -> bool:
    # Convert to DFA for simpler simulation if needed
    if not is_deterministic(automaton):
        dfa = nfa_to_dfa(automaton)
    else:
        dfa = automaton
    
    # Start with the initial state
    current_state_name = dfa.get_initial().name
    
    # Process each symbol in the word
    for symbol in word:
        if symbol not in dfa.alphabet:
            raise ValueError(f"Symbol {symbol} not in alphabet")
        
        # Get next state
        next_states = dfa.next_states(current_state_name, symbol)
        if not next_states:
            return False  # No transition, reject
        
        current_state_name = next(iter(next_states))  # For a DFA, there's only one
    
    # Check if final state
    return dfa.states[current_state_name].is_final


def _generate_words_dfs(
    automaton: Automaton, 
    max_length: int = MAX_WORD_LENGTH,
    should_accept: bool = True,
    max_count: int = 10
) -> List[str]:
    # Convert to DFA for simpler generation
    if not is_deterministic(automaton):
        dfa = nfa_to_dfa(automaton)
    else:
        dfa = automaton
    
    result = []
    stack = [("", dfa.get_initial().name)]
    
    while stack and len(result) < max_count:
        word, state_name = stack.pop()
        
        # If we're at max length, check if it should be accepted
        if len(word) == max_length:
            is_final = dfa.states[state_name].is_final
            if is_final == should_accept and word not in result:
                result.append(word)
            continue
        
        # Get all possible transitions from the current state
        transitions = dfa.get_transitions_from(state_name)
        
        # Shuffle transitions for more diverse words
        random.shuffle(transitions)
        
        for t in transitions:
            new_word = word + t.symbol
            new_state = t.dest.name
            
            # Check if this word can be accepted now
            if len(new_word) >= 1:
                is_final = dfa.states[new_state].is_final
                if is_final == should_accept and new_word not in result:
                    result.append(new_word)
                    if len(result) >= max_count:
                        break
            
            # Continue searching
            if len(new_word) < max_length:
                stack.append((new_word, new_state))
    
    return result


def _generate_words_bfs(
    automaton: Automaton, 
    max_length: int = MAX_WORD_LENGTH,
    should_accept: bool = True,
    max_count: int = 10
) -> List[str]:
    # Convert to DFA for simpler generation
    if not is_deterministic(automaton):
        dfa = nfa_to_dfa(automaton)
    else:
        dfa = automaton
    
    result = []
    queue = deque([("", dfa.get_initial().name)])
    visited = set()
    
    while queue and len(result) < max_count:
        word, state_name = queue.popleft()
        
        # Track visited state-word combinations to avoid loops
        if (word, state_name) in visited:
            continue
        visited.add((word, state_name))
        
        # Check if this word should be accepted
        if len(word) > 0:
            is_final = dfa.states[state_name].is_final
            if is_final == should_accept and word not in result:
                result.append(word)
                if len(result) >= max_count:
                    break
        
        # If we're at max length, don't explore further
        if len(word) >= max_length:
            continue
        
        # Get all possible transitions from the current state
        transitions = dfa.get_transitions_from(state_name)
        
        # Shuffle transitions for more diverse words
        transitions_list = list(transitions)
        random.shuffle(transitions_list)
        
        for t in transitions_list:
            new_word = word + t.symbol
            new_state = t.dest.name
            
            # Continue searching
            queue.append((new_word, new_state))
    
    return result


def generate_accepted_words(
    automaton: Automaton, 
    max_length: int = MAX_WORD_LENGTH,
    max_count: int = 10,
    method: str = "bfs"
) -> List[str]:
    if method.lower() == "bfs":
        return _generate_words_bfs(automaton, max_length, True, max_count)
    else:
        return _generate_words_dfs(automaton, max_length, True, max_count)


def generate_rejected_words(
    automaton: Automaton, 
    max_length: int = MAX_WORD_LENGTH,
    max_count: int = 10,
    method: str = "random"
) -> List[str]:
    if method.lower() == "random":
        return _generate_random_rejected_words(automaton, max_length, max_count)
    elif method.lower() == "bfs":
        return _generate_words_bfs(automaton, max_length, False, max_count)
    else:
        return _generate_words_dfs(automaton, max_length, False, max_count)


def _generate_random_rejected_words(
    automaton: Automaton, 
    max_length: int = MAX_WORD_LENGTH,
    max_count: int = 10
) -> List[str]:
    result = []
    attempts = 0
    
    while len(result) < max_count and attempts < MAX_ATTEMPTS:
        attempts += 1
        
        # Generate a random word
        length = random.randint(1, max_length)
        word = "".join(random.choice(automaton.alphabet.symbols) for _ in range(length))
        
        # Check if the automaton rejects this word
        if not simulate(automaton, word) and word not in result:
            result.append(word)
    
    return result 