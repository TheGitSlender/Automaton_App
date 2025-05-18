from typing import Dict, List, Set, Tuple, Optional, Any, Iterator
from itertools import product
from collections import deque

from .models import State, Alphabet, Transition, Automaton


def is_deterministic(automaton: Automaton) -> bool:
    initial_states = [s for s in automaton.states.values() if s.is_initial]
    if len(initial_states) != 1:
        return False
    
    for state_name in automaton.states:
        for symbol in automaton.alphabet:
            next_states = automaton.next_states(state_name, symbol)
            if len(next_states) > 1:
                return False
    
    return True


def is_complete(automaton: Automaton) -> bool:
    for state_name, state in automaton.states.items():
        for symbol in automaton.alphabet:
            next_states = automaton.next_states(state_name, symbol)
            if not next_states:
                return False
    
    return True


def make_complete(automaton: Automaton) -> Automaton:
    if is_complete(automaton):
        return automaton  # Already complete
    
    # Create a copy of the states and transitions
    states = [State(s.name, s.is_initial, s.is_final) for s in automaton.states.values()]
    transitions = [
        Transition(
            next(s for s in states if s.name == t.src.name),
            t.symbol,
            next(s for s in states if s.name == t.dest.name)
        ) for t in automaton.transitions
    ]
    
    # Add a sink state
    sink_name = "sink"
    while sink_name in automaton.states:
        sink_name = f"_{sink_name}"
    
    sink_state = State(sink_name, False, False)
    states.append(sink_state)
    
    # Add missing transitions to sink state for all states
    for state in states:
        if state.name == sink_name:
            continue  # Skip the sink state itself
        
        for symbol in automaton.alphabet:
            if not automaton.next_states(state.name, symbol):
                transitions.append(Transition(state, symbol, sink_state))
    
    # Add self-transitions for sink state on all symbols
    for symbol in automaton.alphabet:
        transitions.append(Transition(sink_state, symbol, sink_state))
    
    # Create new automaton
    return Automaton(f"{automaton.name}_complete", automaton.alphabet, states, transitions)


def nfa_to_dfa(automaton: Automaton) -> Automaton:
    if is_deterministic(automaton):
        return automaton  # Already deterministic
    
    # Get initial state and create a set of its name
    initial_state = automaton.get_initial()
    initial_set = frozenset([initial_state.name])
    
    # Map from state sets to DFA state names
    state_sets: Dict[frozenset, str] = {initial_set: "q0"}
    
    # List of state sets to process
    queue = deque([initial_set])
    
    # New DFA states and transitions
    dfa_states: List[State] = []
    dfa_transitions: List[Transition] = []
    
    # Create initial state for DFA
    is_initial_final = any(automaton.states[name].is_final for name in initial_set)
    dfa_states.append(State("q0", True, is_initial_final))
    
    # Process state sets
    while queue:
        current_set = queue.popleft()
        current_name = state_sets[current_set]
        
        # For each symbol, compute next state set
        for symbol in automaton.alphabet:
            next_set = set()
            for state_name in current_set:
                next_set.update(automaton.next_states(state_name, symbol))
            
            if not next_set:
                continue  # No transition for this symbol
            
            next_frozen = frozenset(next_set)
            
            # Create new DFA state if needed
            if next_frozen not in state_sets:
                new_name = f"q{len(state_sets)}"
                state_sets[next_frozen] = new_name
                
                # Check if the new state should be final
                is_final = any(automaton.states[name].is_final for name in next_set)
                
                dfa_states.append(State(new_name, False, is_final))
                queue.append(next_frozen)
            
            # Add transition
            src_state = next(s for s in dfa_states if s.name == current_name)
            dest_state = next(s for s in dfa_states if s.name == state_sets[next_frozen])
            dfa_transitions.append(Transition(src_state, symbol, dest_state))
    
    # Create new automaton
    return Automaton(f"{automaton.name}_dfa", automaton.alphabet, dfa_states, dfa_transitions)


def _get_clean_name(name: str) -> str:
    if len(name) < 30:
        return name
    
    operations = ["_dfa", "_min", "_complete", "_union", "_intersect", "_complement"]
    
    base_name = name
    for op in operations:
        if op in base_name:
            base_name = base_name.split(op)[0]
    
    return base_name


def minimize_automaton(automaton: Automaton) -> Automaton:
    # Ensure the automaton is deterministic and complete
    if not is_deterministic(automaton):
        automaton = nfa_to_dfa(automaton)
    
    if not is_complete(automaton):
        automaton = make_complete(automaton)
    
    # Get final and non-final states
    final_states = {s.name for s in automaton.states.values() if s.is_final}
    non_final_states = {s.name for s in automaton.states.values() if not s.is_final}
    
    # Initial partition
    partitions = []
    if final_states:
        partitions.append(final_states)
    if non_final_states:
        partitions.append(non_final_states)
    
    # Refine partitions
    changed = True
    while changed:
        changed = False
        new_partitions = []
        
        for partition in partitions:
            if len(partition) <= 1:
                new_partitions.append(partition)
                continue
            
            # Try to split the partition
            for symbol in automaton.alphabet:
                # Group states by their destination partitions
                groups: Dict[Tuple, Set[str]] = {}
                
                for state_name in partition:
                    # Get the destination state for this symbol
                    dest_names = automaton.next_states(state_name, symbol)
                    
                    # Find which partition the destination state belongs to
                    dest_partition_indices = []
                    for dest_name in dest_names:
                        for i, p in enumerate(partitions):
                            if dest_name in p:
                                dest_partition_indices.append(i)
                                break
                    
                    dest_key = tuple(sorted(dest_partition_indices))
                    
                    if dest_key not in groups:
                        groups[dest_key] = set()
                    groups[dest_key].add(state_name)
                
                # If we found a split
                if len(groups) > 1:
                    changed = True
                    new_partitions.extend(groups.values())
                    break
            else:
                # No split found for any symbol
                new_partitions.append(partition)
        
        partitions = new_partitions
    
    # Create new automaton from partitions
    states = []
    transitions = []
    partition_to_name = {}
    
    # Try to preserve original state names when a partition has only one state
    for i, partition in enumerate(partitions):
        # If the partition has only one state, keep its original name
        if len(partition) == 1:
            name = next(iter(partition))
        else:
            # For partitions with multiple states, try to use one of the original names
            # Prefer initial states or states with shorter names
            sorted_names = sorted(partition, key=lambda x: (not automaton.states[x].is_initial, len(x)))
            name = sorted_names[0] if sorted_names else f"q{i}"
            
        partition_to_name[frozenset(partition)] = name
        
        # Determine if this partition is initial or final
        is_initial = any(automaton.states[s].is_initial for s in partition)
        is_final = any(automaton.states[s].is_final for s in partition)
        
        states.append(State(name, is_initial, is_final))
    
    # Create transitions
    for partition in partitions:
        # Take a representative state from the partition
        rep_state_name = next(iter(partition))
        src_name = partition_to_name[frozenset(partition)]
        src_state = next(s for s in states if s.name == src_name)
        
        for symbol in automaton.alphabet:
            dest_names = automaton.next_states(rep_state_name, symbol)
            if not dest_names:
                continue
            
            dest_name = next(iter(dest_names))  # For a DFA, there's only one
            
            # Find which partition contains the destination state
            for p in partitions:
                if dest_name in p:
                    dest_partition = p
                    break
            
            dest_state_name = partition_to_name[frozenset(dest_partition)]
            dest_state = next(s for s in states if s.name == dest_state_name)
            
            transitions.append(Transition(src_state, symbol, dest_state))
    
    # Create new automaton with a clean name to prevent excessive name length
    clean_name = _get_clean_name(automaton.name)
    return Automaton(f"{clean_name}_min", automaton.alphabet, states, transitions)


def union(automaton1: Automaton, automaton2: Automaton) -> Automaton:
    # Check that alphabets are the same
    if set(automaton1.alphabet.symbols) != set(automaton2.alphabet.symbols):
        raise ValueError("Automata must have the same alphabet for union operation")
    
    # Convert to DFAs
    dfa1 = nfa_to_dfa(automaton1)
    dfa2 = nfa_to_dfa(automaton2)
    
    # Create product automaton
    alphabet = Alphabet(automaton1.alphabet.symbols)
    
    # Create simplified state names to prevent concatenating long names
    state_pairs = {}
    next_state_id = 0
    
    # Create states for the product automaton
    states = []
    for s1 in dfa1.states.values():
        for s2 in dfa2.states.values():
            # Use a simple Q-index naming scheme but track the state pair
            state_pair = (s1.name, s2.name)
            state_name = f"q{next_state_id}"
            next_state_id += 1
            state_pairs[state_pair] = state_name
            
            is_initial = s1.is_initial and s2.is_initial
            is_final = s1.is_final or s2.is_final  # Union: accept if either accepts
            states.append(State(state_name, is_initial, is_final))
    
    # Create transitions
    transitions = []
    for trans1 in dfa1.transitions:
        for trans2 in dfa2.transitions:
            if trans1.symbol == trans2.symbol:
                # Get the simple state names from our mapping
                src_pair = (trans1.src.name, trans2.src.name)
                dest_pair = (trans1.dest.name, trans2.dest.name)
                
                if src_pair in state_pairs and dest_pair in state_pairs:
                    src_name = state_pairs[src_pair]
                    dest_name = state_pairs[dest_pair]
                    
                    src_state = next(s for s in states if s.name == src_name)
                    dest_state = next(s for s in states if s.name == dest_name)
                    
                    transitions.append(Transition(src_state, trans1.symbol, dest_state))
    
    # Create result with clean names to prevent excessive name length
    name1 = _get_clean_name(dfa1.name)
    name2 = _get_clean_name(dfa2.name)
    result = Automaton(f"{name1}_union_{name2}", alphabet, states, transitions)
    return minimize_automaton(result)


def intersection(automaton1: Automaton, automaton2: Automaton) -> Automaton:
    # Check that alphabets are the same
    if set(automaton1.alphabet.symbols) != set(automaton2.alphabet.symbols):
        raise ValueError("Automata must have the same alphabet for intersection operation")
    
    # Convert to DFAs
    dfa1 = nfa_to_dfa(automaton1)
    dfa2 = nfa_to_dfa(automaton2)
    
    # Create product automaton
    alphabet = Alphabet(automaton1.alphabet.symbols)
    
    # Create simplified state names to prevent concatenating long names
    state_pairs = {}
    next_state_id = 0
    
    # Create states for the product automaton
    states = []
    for s1 in dfa1.states.values():
        for s2 in dfa2.states.values():
            # Use a simple Q-index naming scheme but track the state pair
            state_pair = (s1.name, s2.name)
            state_name = f"q{next_state_id}"
            next_state_id += 1
            state_pairs[state_pair] = state_name
            
            is_initial = s1.is_initial and s2.is_initial
            is_final = s1.is_final and s2.is_final  # Intersection: accept if both accept
            states.append(State(state_name, is_initial, is_final))
    
    # Create transitions
    transitions = []
    for trans1 in dfa1.transitions:
        for trans2 in dfa2.transitions:
            if trans1.symbol == trans2.symbol:
                # Get the simple state names from our mapping
                src_pair = (trans1.src.name, trans2.src.name)
                dest_pair = (trans1.dest.name, trans2.dest.name)
                
                if src_pair in state_pairs and dest_pair in state_pairs:
                    src_name = state_pairs[src_pair]
                    dest_name = state_pairs[dest_pair]
                    
                    src_state = next(s for s in states if s.name == src_name)
                    dest_state = next(s for s in states if s.name == dest_name)
                    
                    transitions.append(Transition(src_state, trans1.symbol, dest_state))
    
    # Create result with clean names to prevent excessive name length
    name1 = _get_clean_name(dfa1.name)
    name2 = _get_clean_name(dfa2.name)
    result = Automaton(f"{name1}_intersect_{name2}", alphabet, states, transitions)
    return minimize_automaton(result)


def complement(automaton: Automaton) -> Automaton:
    # Convert to DFA and make complete
    dfa = nfa_to_dfa(automaton)
    complete_dfa = make_complete(dfa)
    
    # Create states with inverted acceptance
    states = [
        State(s.name, s.is_initial, not s.is_final) 
        for s in complete_dfa.states.values()
    ]
    
    # Copy transitions
    transitions = [
        Transition(
            next(s for s in states if s.name == t.src.name),
            t.symbol,
            next(s for s in states if s.name == t.dest.name)
        ) for t in complete_dfa.transitions
    ]
    
    # Create new automaton with a clean name
    clean_name = _get_clean_name(automaton.name)
    return Automaton(f"{clean_name}_complement", automaton.alphabet, states, transitions)


def are_equivalent(automaton1: Automaton, automaton2: Automaton) -> bool:
    # Check that alphabets are the same
    if set(automaton1.alphabet.symbols) != set(automaton2.alphabet.symbols):
        raise ValueError("Automata must have the same alphabet to check equivalence")
    
    # Convert to minimal DFAs
    min_dfa1 = minimize_automaton(nfa_to_dfa(automaton1))
    min_dfa2 = minimize_automaton(nfa_to_dfa(automaton2))
    
    # Compare the number of states
    if len(min_dfa1.states) != len(min_dfa2.states):
        return False
    
    # Compare the number of final states
    finals1 = [s for s in min_dfa1.states.values() if s.is_final]
    finals2 = [s for s in min_dfa2.states.values() if s.is_final]
    if len(finals1) != len(finals2):
        return False
    
    # Compare transitions (this is a heuristic - we should use a proper isomorphism check)
    for symbol in min_dfa1.alphabet:
        transitions1 = [(t.src.name, t.dest.name) for t in min_dfa1.transitions if t.symbol == symbol]
        transitions2 = [(t.src.name, t.dest.name) for t in min_dfa2.transitions if t.symbol == symbol]
        if len(transitions1) != len(transitions2):
            return False
    
    # A more robust approach would be to check if the symmetric difference is empty
    # Symmetric difference: (A ∪ B) - (A ∩ B)
    diff = union(
        intersection(min_dfa1, complement(min_dfa2)),
        intersection(complement(min_dfa1), min_dfa2)
    )
    
    # If the symmetric difference has no final states, the languages are equivalent
    return not any(s.is_final for s in diff.states.values()) 