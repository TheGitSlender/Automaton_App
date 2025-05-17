"""
Models for automata representation.
"""
from typing import Dict, List, Set, Optional, Iterator, Tuple


class State:
    """
    Represents a state in an automaton.
    """
    def __init__(self, name: str, is_initial: bool = False, is_final: bool = False):
        """
        Initialize a state.
        
        Args:
            name: Unique identifier for the state
            is_initial: Whether this is the initial state
            is_final: Whether this is a final/accepting state
        """
        self.name = name
        self.is_initial = is_initial
        self.is_final = is_final
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"State({self.name}, initial={self.is_initial}, final={self.is_final})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, State):
            return False
        return self.name == other.name
    
    def __hash__(self) -> int:
        return hash(self.name)


class Alphabet:
    """
    Represents the alphabet of symbols for an automaton.
    """
    def __init__(self, symbols: List[str]):
        """
        Initialize an alphabet.
        
        Args:
            symbols: List of symbols in the alphabet
        """
        self.symbols = sorted(set(symbols))  # Ensure uniqueness
    
    def __str__(self) -> str:
        return f"{{{', '.join(self.symbols)}}}"
    
    def __repr__(self) -> str:
        return f"Alphabet({self.symbols})"
    
    def __contains__(self, symbol: str) -> bool:
        return symbol in self.symbols
    
    def __iter__(self) -> Iterator[str]:
        return iter(self.symbols)
    
    def __len__(self) -> int:
        return len(self.symbols)


class Transition:
    """
    Represents a transition between states in an automaton.
    """
    def __init__(self, src: State, symbol: str, dest: State):
        """
        Initialize a transition.
        
        Args:
            src: Source state
            symbol: Symbol that triggers the transition
            dest: Destination state
        """
        self.src = src
        self.symbol = symbol
        self.dest = dest
    
    def __str__(self) -> str:
        return f"δ({self.src}, {self.symbol}) = {self.dest}"
    
    def __repr__(self) -> str:
        return f"Transition({self.src.name}, {self.symbol}, {self.dest.name})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Transition):
            return False
        return (self.src == other.src and 
                self.symbol == other.symbol and 
                self.dest == other.dest)
    
    def __hash__(self) -> int:
        return hash((self.src, self.symbol, self.dest))


class Automaton:
    """
    Represents a finite automaton (DFA or NFA).
    """
    def __init__(self, name: str, alphabet: Alphabet, states: List[State], transitions: List[Transition]):
        """
        Initialize an automaton.
        
        Args:
            name: Name of the automaton
            alphabet: Alphabet of the automaton
            states: List of states in the automaton
            transitions: List of transitions between states
        """
        self.name = name
        self.alphabet = alphabet
        self.states = {s.name: s for s in states}  # Map state names to State objects
        self.transitions = transitions
        
        # Build transition function for faster lookup
        self.delta: Dict[Tuple[str, str], Set[str]] = {}
        for t in transitions:
            key = (t.src.name, t.symbol)
            if key not in self.delta:
                self.delta[key] = set()
            self.delta[key].add(t.dest.name)
    
    def add_state(self, state: State) -> None:
        """
        Add a state to the automaton.
        
        Args:
            state: The state to add
        """
        self.states[state.name] = state
    
    def add_transition(self, transition: Transition) -> None:
        """
        Add a transition to the automaton.
        
        Args:
            transition: The transition to add
        """
        self.transitions.append(transition)
        
        # Update transition function
        key = (transition.src.name, transition.symbol)
        if key not in self.delta:
            self.delta[key] = set()
        self.delta[key].add(transition.dest.name)
    
    def get_initial(self) -> State:
        """
        Get the initial state of the automaton.
        
        Returns:
            The initial state
        
        Raises:
            ValueError: If no initial state or multiple initial states are found
        """
        initials = [s for s in self.states.values() if s.is_initial]
        if len(initials) != 1:
            raise ValueError(f"Expected exactly one initial state, found {len(initials)}")
        return initials[0]
    
    def get_finals(self) -> List[State]:
        """
        Get all final states of the automaton.
        
        Returns:
            List of final states
        """
        return [s for s in self.states.values() if s.is_final]
    
    def get_transitions_from(self, state_name: str, symbol: Optional[str] = None) -> List[Transition]:
        """
        Get all transitions from a state, optionally filtered by symbol.
        
        Args:
            state_name: Name of the source state
            symbol: Optional symbol to filter transitions
            
        Returns:
            List of matching transitions
        """
        if symbol is None:
            return [t for t in self.transitions if t.src.name == state_name]
        return [t for t in self.transitions if t.src.name == state_name and t.symbol == symbol]
    
    def next_states(self, state_name: str, symbol: str) -> Set[str]:
        """
        Get all possible next states from a state on a given symbol.
        
        Args:
            state_name: Current state name
            symbol: Input symbol
            
        Returns:
            Set of next state names
        """
        key = (state_name, symbol)
        return self.delta.get(key, set())
    
    def __str__(self) -> str:
        return f"Automaton {self.name} with {len(self.states)} states and {len(self.transitions)} transitions" 