from typing import List, Dict, Set, Optional, Tuple, Iterator


class State:
    def __init__(self, name: str, is_initial: bool = False, is_final: bool = False):
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
    def __init__(self, symbols: List[str]):
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
    def __init__(self, src: State, symbol: str, dest: State):
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
    def __init__(self, name: str, alphabet: Alphabet, states: List[State], transitions: List[Transition], creator_id: Optional[str] = None):
        self.name = name
        self.alphabet = alphabet
        self.states = {s.name: s for s in states}  # Map state names to State objects
        self.transitions = transitions
        self.creator_id = creator_id
        
        # Build transition function for faster lookup
        self.delta: Dict[Tuple[str, str], Set[str]] = {}
        for t in transitions:
            key = (t.src.name, t.symbol)
            if key not in self.delta:
                self.delta[key] = set()
            self.delta[key].add(t.dest.name)
    
    def add_state(self, state: State) -> None:
        self.states[state.name] = state
    
    def add_transition(self, transition: Transition) -> None:
        self.transitions.append(transition)
        
        # Update transition function
        key = (transition.src.name, transition.symbol)
        if key not in self.delta:
            self.delta[key] = set()
        self.delta[key].add(transition.dest.name)
    
    def get_initial(self) -> State:
        initials = [s for s in self.states.values() if s.is_initial]
        if len(initials) != 1:
            raise ValueError(f"Expected exactly one initial state, found {len(initials)}")
        return initials[0]
    
    def get_finals(self) -> List[State]:
        return [s for s in self.states.values() if s.is_final]
    
    def get_transitions_from(self, state_name: str, symbol: Optional[str] = None) -> List[Transition]:
        if symbol is None:
            return [t for t in self.transitions if t.src.name == state_name]
        return [t for t in self.transitions if t.src.name == state_name and t.symbol == symbol]
    
    def next_states(self, state_name: str, symbol: str) -> Set[str]:
        key = (state_name, symbol)
        return self.delta.get(key, set())
    
    def __str__(self) -> str:
        return f"Automaton {self.name} with {len(self.states)} states and {len(self.transitions)} transitions" 