import json
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict
import time
import os


class Tape:
    
    def __init__(self, input_string: str, blank_symbol: str = '_'):
        self.blank_symbol = blank_symbol
        self.tape = defaultdict(lambda: blank_symbol)
        
        for i, symbol in enumerate(input_string):
            self.tape[i] = symbol
        
        self.head_position = 0
        self.leftmost = 0
        self.rightmost = len(input_string) - 1 if input_string else 0
    
    def read(self) -> str:
        return self.tape[self.head_position]
    
    def write(self, symbol: str):
        self.tape[self.head_position] = symbol
        self.leftmost = min(self.leftmost, self.head_position)
        self.rightmost = max(self.rightmost, self.head_position)
    
    def move(self, direction: str):
        if direction == 'L':
            self.head_position -= 1
        elif direction == 'R':
            self.head_position += 1
        else:
            raise ValueError(f"Dirección inválida: {direction}")
        
        self.leftmost = min(self.leftmost, self.head_position)
        self.rightmost = max(self.rightmost, self.head_position)
    
    def get_tape_string(self, context: int = 10) -> str:
        start = min(self.leftmost, self.head_position - context)
        end = max(self.rightmost, self.head_position + context)
        
        tape_content = ''.join(self.tape[i] for i in range(start, end + 1))
        head_indicator = ' ' * (self.head_position - start) + '^'
        
        return f"Cinta: {tape_content}\n       {head_indicator}"


class TransitionFunction:
    
    def __init__(self):
        self.transitions: Dict[Tuple[str, str], Tuple[str, str, str]] = {}
    
    def add_transition(self, current_state: str, read_symbol: str,
                      next_state: str, write_symbol: str, direction: str):
        if direction not in ['L', 'R']:
            raise ValueError(f"Dirección debe ser 'L' o 'R', se recibió: {direction}")
        
        self.transitions[(current_state, read_symbol)] = (next_state, write_symbol, direction)
    
    def get_transition(self, state: str, symbol: str) -> Optional[Tuple[str, str, str]]:
        return self.transitions.get((state, symbol))
    
    def has_transition(self, state: str, symbol: str) -> bool:
        return (state, symbol) in self.transitions


class TuringMachine:
    
    
    def __init__(self, states: Set[str], input_alphabet: Set[str],
                 tape_alphabet: Set[str], transition_function: TransitionFunction,
                 initial_state: str, blank_symbol: str, accept_states: Set[str]):
        
        if initial_state not in states:
            raise ValueError("El estado inicial debe estar en el conjunto de estados")
        
        if not accept_states.issubset(states):
            raise ValueError("Los estados de aceptación deben estar en el conjunto de estados")
        
        if not input_alphabet.issubset(tape_alphabet):
            raise ValueError("El alfabeto de entrada debe ser subconjunto del alfabeto de la cinta")
        
        if blank_symbol not in tape_alphabet:
            raise ValueError("El símbolo en blanco debe estar en el alfabeto de la cinta")
        
        self.states = states
        self.input_alphabet = input_alphabet
        self.tape_alphabet = tape_alphabet
        self.transition_function = transition_function
        self.initial_state = initial_state
        self.blank_symbol = blank_symbol
        self.accept_states = accept_states
        
        self.current_state = initial_state
        self.tape: Optional[Tape] = None
        self.step_count = 0
        self.execution_history: List[Tuple[str, int, str]] = []
    
    def reset(self, input_string: str):
        for symbol in input_string:
            if symbol not in self.input_alphabet:
                raise ValueError(f"Símbolo '{symbol}' no está en el alfabeto de entrada")
        
        self.tape = Tape(input_string, self.blank_symbol)
        self.current_state = self.initial_state
        self.step_count = 0
        self.execution_history = []
        self._save_configuration()
    
    def _save_configuration(self):
        if self.tape:
            self.execution_history.append((
                self.current_state,
                self.tape.head_position,
                self.tape.get_tape_string()
            ))
    
    def step(self) -> bool:
        
        if self.tape is None:
            raise RuntimeError("La máquina no ha sido inicializada con una cadena de entrada")
        
        if self.current_state in self.accept_states:
            return False
        
     
        current_symbol = self.tape.read()
        
        transition = self.transition_function.get_transition(self.current_state, current_symbol)
        
        if transition is None:
            return False
        
        next_state, write_symbol, direction = transition
        self.tape.write(write_symbol)
        self.tape.move(direction)
        self.current_state = next_state
        self.step_count += 1
        
        self._save_configuration()
        
        return True
    
    def run(self, input_string: str, max_steps: int = 10000, step_by_step: bool = False):
        
        self.reset(input_string)
        
        print(f"\n{'='*70}")
        print(f"EJECUTANDO MÁQUINA DE TURING")
        print(f"{'='*70}")
        print(f"Cadena de entrada: '{input_string}'")
        print(f"Estado inicial: {self.initial_state}")
        print(f"{'='*70}\n")
        
        if step_by_step:
            self._print_configuration(0)
            input("Presiona Enter para continuar...")
        
        while self.step_count < max_steps:
            can_continue = self.step()
            
            if step_by_step:
                self._print_configuration(self.step_count)
                if can_continue:
                    input("Presiona Enter para continuar...")
            
            if not can_continue:
                break
        
        print(f"\n{'='*70}")
        self._print_result()
        print(f"{'='*70}\n")
    
    def _print_configuration(self, step: int):
        """Imprime la configuración actual de la máquina"""
        print(f"\n--- Paso {step} ---")
        print(f"Estado: {self.current_state}")
        print(self.tape.get_tape_string())
        print()
    
    def _print_result(self):
        if self.current_state in self.accept_states:
            print("RESULTADO: ACEPTADA ✓")
            print(f"La cadena fue ACEPTADA en el estado: {self.current_state}")
        else:
            print("RESULTADO: RECHAZADA ✗")
            print(f"La máquina se detuvo en el estado: {self.current_state}")
        
        print(f"Número total de pasos: {self.step_count}")
    
    def get_result(self) -> str:
        if self.current_state in self.accept_states:
            return "Acepta"
        else:
            return "Rechaza"


def load_machine_from_json(filepath: str) -> TuringMachine:
    with open(filepath, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    transition_function = TransitionFunction()
    for trans in config['transitions']:
        transition_function.add_transition(
            trans['current_state'],
            trans['read_symbol'],
            trans['next_state'],
            trans['write_symbol'],
            trans['direction']
        )
    
    tm = TuringMachine(
        states=set(config['states']),
        input_alphabet=set(config['input_alphabet']),
        tape_alphabet=set(config['tape_alphabet']),
        transition_function=transition_function,
        initial_state=config['initial_state'],
        blank_symbol=config['blank_symbol'],
        accept_states=set(config['accept_states'])
    )
    
    return tm


def create_balanced_01_machine() -> TuringMachine:
    
    states = {'q0', 'q1', 'q2', 'q3', 'q4', 'q_accept', 'q_reject'}
    input_alphabet = {'0', '1'}
    tape_alphabet = {'0', '1', 'X', 'Y', '_'}
    blank_symbol = '_'
    initial_state = 'q0'
    accept_states = {'q_accept'}
    
    tf = TransitionFunction()
    
    tf.add_transition('q0', '0', 'q1', 'X', 'R')  
    tf.add_transition('q0', 'Y', 'q0', 'Y', 'R')  
    tf.add_transition('q0', '_', 'q4', '_', 'L')  
    
    tf.add_transition('q1', '0', 'q1', '0', 'R')  
    tf.add_transition('q1', '1', 'q2', 'Y', 'L')  
    tf.add_transition('q1', 'Y', 'q1', 'Y', 'R')  
    tf.add_transition('q1', '_', 'q_reject', '_', 'R')
    
    tf.add_transition('q2', '0', 'q2', '0', 'L')
    tf.add_transition('q2', 'Y', 'q2', 'Y', 'L')
    tf.add_transition('q2', 'X', 'q2', 'X', 'L')
    tf.add_transition('q2', '_', 'q0', '_', 'R')
    
    tf.add_transition('q4', 'X', 'q4', 'X', 'L')
    tf.add_transition('q4', 'Y', 'q4', 'Y', 'L')
    tf.add_transition('q4', '_', 'q_accept', '_', 'R')
    tf.add_transition('q4', '0', 'q_reject', '0', 'R')
    tf.add_transition('q4', '1', 'q_reject', '1', 'R')
    
    tm = TuringMachine(
        states=states,
        input_alphabet=input_alphabet,
        tape_alphabet=tape_alphabet,
        transition_function=tf,
        initial_state=initial_state,
        blank_symbol=blank_symbol,
        accept_states=accept_states
    )
    
    return tm


def interactive_menu():
    print("""
╔══════════════════════════════════════════════════════════════╗
║             SIMULADOR DE MÁQUINA DE TURING                   ║
║          Implementación Formal según definición              ║
║          M = (Q, Σ, Γ, δ, q0, B, F)                          ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("\nCargando máquina: Igual número de 0s y 1s")
    tm = create_balanced_01_machine()
    
    print("\nMáquina cargada exitosamente!")
    print(f"- Estados: {len(tm.states)}")
    print(f"- Alfabeto de entrada: {tm.input_alphabet}")
    print(f"- Alfabeto de cinta: {tm.tape_alphabet}")
    print(f"- Estado inicial: {tm.initial_state}")
    print(f"- Estados de aceptación: {tm.accept_states}")
    
    while True:
        print(f"\n{'='*60}")
        print("Opciones:")
        print("1. Ejecutar con cadena de entrada (modo automático)")
        print("2. Ejecutar paso a paso")
        print("3. Ejecutar pruebas de ejemplo")
        print("4. Salir")
        print("="*60)
        
        choice = input("\nSelecciona una opción: ").strip()
        
        if choice == '1':
            input_string = input("\nIngresa la cadena de entrada (solo 0s y 1s): ").strip()
            try:
                tm.run(input_string, step_by_step=False)
            except Exception as e:
                print(f"Error: {e}")
        
        elif choice == '2':
            input_string = input("\nIngresa la cadena de entrada (solo 0s y 1s): ").strip()
            try:
                tm.run(input_string, step_by_step=True)
            except Exception as e:
                print(f"Error: {e}")
        
        elif choice == '3':
            test_cases = [
                ("", "Cadena vacía"),
                ("01", "Una pareja"),
                ("0011", "Dos 0s, dos 1s"),
                ("001", "Debe rechazar (más 0s)"),
                ("1100", "Debe rechazar (diferente orden)"),
                ("0101", "Dos parejas alternadas"),
                ("000111", "Tres 0s, tres 1s")
            ]
            
            print("\n" + "="*70)
            print("Ejecutando Pruebas...")
            print("="*70)
            
            for test_input, description in test_cases:
                print(f"\nPrueba: {description}")
                print(f"Entrada: '{test_input}'")
                try:
                    tm.run(test_input, step_by_step=False)
                except Exception as e:
                    print(f"Error: {e}")
                print("-" * 70)
        
        elif choice == '4':
            print("\n¡Hasta luego!")
            break
        
        else:
            print("Opción inválida. Intenta de nuevo.")


if __name__ == "__main__":
    interactive_menu()