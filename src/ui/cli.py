"""
Interfaz de línea de comandos para el juego de Buscaminas.
"""

import time
from typing import Dict, Any, Tuple
import numpy as np
import colorama
from colorama import Fore, Back, Style

from src.game.minesweeper import Minesweeper, GameEvent, GameStatus


class CLI:
    """
    Interfaz de línea de comandos para el juego de Buscaminas.
    
    Esta clase proporciona una forma de visualizar y jugar al Buscaminas en la consola.
    """
    
    # Caracteres para visualización
    HIDDEN_CELL = '■'
    MARKED_CELL = '⚑'
    MINE_CELL = '✹'
    EMPTY_CELL = ' '
    
    # Colores para los números
    NUMBER_COLORS = {
        1: Fore.BLUE,
        2: Fore.GREEN,
        3: Fore.RED,
        4: Fore.MAGENTA,
        5: Fore.YELLOW,
        6: Fore.CYAN,
        7: Fore.WHITE,
        8: Fore.LIGHTBLACK_EX
    }
    
    def __init__(self, game: Minesweeper):
        """
        Inicializa la interfaz CLI para un juego de Buscaminas.
        
        Args:
            game: Instancia del juego de Buscaminas
        """
        self.game = game
        colorama.init()
        
        # Registrar manejadores de eventos
        self.game.register_event_handler(GameEvent.GAME_STARTED, self._on_game_started)
        self.game.register_event_handler(GameEvent.GAME_WON, self._on_game_won)
        self.game.register_event_handler(GameEvent.GAME_LOST, self._on_game_lost)
    
    def display_board(self) -> None:
        """Muestra el tablero actual en la consola."""
        board_state = self.game.get_board_state()
        rows, cols = board_state.shape
        
        # Imprimir cabecera con números de columna
        print("\n   ", end="")
        for j in range(cols):
            print(f"{j:2}", end=" ")
        print("\n   " + "---" * cols)
        
        # Imprimir filas del tablero
        for i in range(rows):
            print(f"{i:2}|", end=" ")
            for j in range(cols):
                self._print_cell(board_state[i, j])
            print()
        
        # Imprimir estadísticas
        stats = self.game.get_game_statistics()
        print(f"\nMinas restantes: {stats['remaining_mines']}")
        print(f"Movimientos: {stats['moves']}")
    
    def _print_cell(self, cell_value: int) -> None:
        """
        Imprime una celda con formato y color adecuados.
        
        Args:
            cell_value: Valor de la celda a imprimir
        """
        if cell_value == self.game.board.HIDDEN:
            print(Back.WHITE + Fore.BLACK + self.HIDDEN_CELL + Style.RESET_ALL, end=" ")
        elif cell_value == self.game.board.MARKED:
            print(Back.YELLOW + Fore.RED + self.MARKED_CELL + Style.RESET_ALL, end=" ")
        elif cell_value == -1:  # Mina
            print(Back.RED + Fore.BLACK + self.MINE_CELL + Style.RESET_ALL, end=" ")
        elif cell_value == 0:  # Celda vacía
            print(self.EMPTY_CELL, end=" ")
        else:  # Número
            color = self.NUMBER_COLORS.get(cell_value, Fore.WHITE)
            print(color + str(cell_value) + Style.RESET_ALL, end=" ")
    
    def play_game(self) -> None:
        """Inicia un juego interactivo en la consola."""
        print("\n=== BUSCAMINAS ===")
        print("Comandos:")
        print("  o fila columna  - Abrir celda")
        print("  m fila columna  - Marcar/desmarcar celda")
        print("  q               - Salir del juego")
        
        self.display_board()
        
        while self.game.status == GameStatus.ONGOING:
            try:
                command = input("\nComando: ").strip().lower()
                
                if command == 'q':
                    print("¡Juego terminado!")
                    break
                
                parts = command.split()
                
                if len(parts) == 3 and parts[0] in ['o', 'm']:
                    action = parts[0]
                    try:
                        row = int(parts[1])
                        col = int(parts[2])
                    except ValueError:
                        print("Coordenadas inválidas. Usa números para fila y columna.")
                        continue
                    
                    if action == 'o':
                        self.game.open_cell(row, col)
                    else:  # action == 'm'
                        self.game.mark_cell(row, col)
                    
                    self.display_board()
                else:
                    print("Comando inválido. Usa 'o fila columna', 'm fila columna' o 'q'.")
            
            except KeyboardInterrupt:
                print("\n¡Juego interrumpido!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def _on_game_started(self, **kwargs) -> None:
        """Manejador para el evento de inicio de juego."""
        print("\n¡El juego ha comenzado!")
    
    def _on_game_won(self, **kwargs) -> None:
        """Manejador para el evento de victoria."""
        moves = kwargs.get('moves', 0)
        print(f"\n¡VICTORIA! Has completado el juego en {moves} movimientos.")
    
    def _on_game_lost(self, **kwargs) -> None:
        """Manejador para el evento de derrota."""
        row, col = kwargs.get('row', -1), kwargs.get('col', -1)
        print(f"\n¡BOOM! Has encontrado una mina en ({row}, {col}).")
        print("Juego terminado.")
        
    @staticmethod
    def play_demo_game(difficulty: str = "beginner") -> None:
        """
        Inicia un juego de demostración con la dificultad especificada.
        
        Args:
            difficulty: Nivel de dificultad ("beginner", "intermediate", "expert")
        """
        if difficulty.lower() == "beginner":
            game = Minesweeper.create_beginner_game()
        elif difficulty.lower() == "intermediate":
            game = Minesweeper.create_intermediate_game()
        elif difficulty.lower() == "expert":
            game = Minesweeper.create_expert_game()
        else:
            print(f"Dificultad '{difficulty}' no reconocida. Usando nivel principiante.")
            game = Minesweeper.create_beginner_game()
        
        cli = CLI(game)
        cli.play_game() 