"""
Módulo principal del juego de Buscaminas.
"""

from enum import Enum
from typing import Tuple, List, Callable, Optional, Dict, Any
import numpy as np

from src.game.board import Board


class GameStatus(Enum):
    """Enumeración de los posibles estados del juego."""
    ONGOING = 0
    VICTORY = 1
    DEFEAT = 2


class GameAction(Enum):
    """Enumeración de las posibles acciones en el juego."""
    OPEN = 0
    MARK = 1


class GameEvent(Enum):
    """Enumeración de los posibles eventos durante el juego."""
    CELL_OPENED = 0
    CELL_MARKED = 1
    CELL_UNMARKED = 2
    GAME_STARTED = 3
    GAME_WON = 4
    GAME_LOST = 5


class Minesweeper:
    """
    Clase principal que gestiona la lógica del juego de Buscaminas.
    
    Esta clase utiliza la clase Board para la representación del tablero
    y añade la lógica del juego, sistema de eventos y gestión del estado.
    """
    
    # Configuraciones predefinidas
    BEGINNER = {"rows": 8, "columns": 8, "mines": 10}
    INTERMEDIATE = {"rows": 16, "columns": 16, "mines": 40}
    EXPERT = {"rows": 16, "columns": 30, "mines": 99}
    
    def __init__(self, rows: int, columns: int, num_mines: int):
        """
        Inicializa un nuevo juego de Buscaminas.
        
        Args:
            rows: Número de filas del tablero
            columns: Número de columnas del tablero
            num_mines: Número de minas a colocar
        """
        self.board = Board(rows, columns, num_mines)
        self.status = GameStatus.ONGOING
        self.first_move = True
        self.moves_count = 0
        
        # Sistema de eventos (patrón Observer)
        self.event_handlers: Dict[GameEvent, List[Callable]] = {event: [] for event in GameEvent}
    
    def register_event_handler(self, event: GameEvent, handler: Callable) -> None:
        """
        Registra un manejador para un evento específico.
        
        Args:
            event: Tipo de evento a manejar
            handler: Función que se llamará cuando ocurra el evento
        """
        self.event_handlers[event].append(handler)
    
    def _trigger_event(self, event: GameEvent, **kwargs) -> None:
        """
        Dispara un evento notificando a todos los manejadores registrados.
        
        Args:
            event: Tipo de evento que ha ocurrido
            **kwargs: Datos adicionales del evento
        """
        for handler in self.event_handlers[event]:
            handler(event=event, **kwargs)
    
    def open_cell(self, row: int, col: int) -> GameStatus:
        """
        Abre una celda en el tablero.
        
        Args:
            row: Fila de la celda
            col: Columna de la celda
            
        Returns:
            Estado actual del juego tras la acción
        """
        # Validar coordenadas
        if not (0 <= row < self.board.rows and 0 <= col < self.board.columns):
            return self.status
        
        # Verificar si el juego ya ha terminado
        if self.status != GameStatus.ONGOING:
            return self.status
        
        # Verificar si la celda ya es visible o está marcada
        if self.board.is_visible(row, col) or self.board.is_marked(row, col):
            return self.status
        
        # Notificar inicio del juego en el primer movimiento
        if self.first_move:
            self._trigger_event(GameEvent.GAME_STARTED)
            self.first_move = False
        
        # Incrementar contador de movimientos
        self.moves_count += 1
        
        # Verificar si es una mina
        if self.board.is_mine(row, col):
            self.status = GameStatus.DEFEAT
            self._show_all_mines()
            self._trigger_event(GameEvent.GAME_LOST, row=row, col=col)
            return self.status
        
        # Hacer visible la celda
        self.board.set_visible(row, col)
        self._trigger_event(GameEvent.CELL_OPENED, row=row, col=col, value=self.board.get_cell_value(row, col))
        
        # Si el valor es 0, abrir celdas adyacentes (algoritmo de flood fill)
        if self.board.get_cell_value(row, col) == 0:
            self._flood_fill(row, col)
        
        # Verificar victoria
        if self.board.are_all_safe_cells_visible():
            self.status = GameStatus.VICTORY
            self._trigger_event(GameEvent.GAME_WON, moves=self.moves_count)
        
        return self.status
    
    def mark_cell(self, row: int, col: int) -> None:
        """
        Marca o desmarca una celda como posible mina.
        
        Args:
            row: Fila de la celda
            col: Columna de la celda
        """
        # Validar coordenadas
        if not (0 <= row < self.board.rows and 0 <= col < self.board.columns):
            return
        
        # Verificar si el juego ya ha terminado
        if self.status != GameStatus.ONGOING:
            return
        
        # Verificar si la celda ya es visible
        if self.board.is_visible(row, col):
            return
        
        # Notificar inicio del juego en el primer movimiento
        if self.first_move:
            self._trigger_event(GameEvent.GAME_STARTED)
            self.first_move = False
        
        # Incrementar contador de movimientos
        self.moves_count += 1
        
        # Alternar estado de marcado
        was_marked = self.board.is_marked(row, col)
        self.board.toggle_mark(row, col)
        
        # Notificar evento correspondiente
        if was_marked:
            self._trigger_event(GameEvent.CELL_UNMARKED, row=row, col=col)
        else:
            self._trigger_event(GameEvent.CELL_MARKED, row=row, col=col)
    
    def _flood_fill(self, row: int, col: int) -> None:
        """
        Algoritmo de flood fill para abrir celdas adyacentes a un 0.
        
        Args:
            row: Fila de la celda inicial
            col: Columna de la celda inicial
        """
        # Obtener celdas adyacentes
        for ni, nj in self.board.get_adjacent_cells(row, col):
            # Si la celda adyacente no es visible y no está marcada
            if not self.board.is_visible(ni, nj) and not self.board.is_marked(ni, nj):
                # Hacer visible la celda
                self.board.set_visible(ni, nj)
                self._trigger_event(GameEvent.CELL_OPENED, row=ni, col=nj, value=self.board.get_cell_value(ni, nj))
                
                # Si es un 0, continuar el flood fill
                if self.board.get_cell_value(ni, nj) == 0:
                    self._flood_fill(ni, nj)
    
    def _show_all_mines(self) -> None:
        """Hace visibles todas las minas del tablero."""
        for i in range(self.board.rows):
            for j in range(self.board.columns):
                if self.board.is_mine(i, j):
                    self.board.set_visible(i, j)
    
    def get_board_state(self) -> np.ndarray:
        """
        Obtiene la representación actual del tablero.
        
        Returns:
            Matriz de NumPy con el estado actual del tablero
        """
        return self.board.get_state_representation()
    
    def get_visible_board(self) -> np.ndarray:
        """
        Obtiene una representación del tablero visible para el jugador.
        
        Returns:
            Matriz de NumPy con el tablero visible
        """
        return self.board.get_state_representation()
    
    def get_game_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del juego actual.
        
        Returns:
            Diccionario con estadísticas del juego
        """
        return {
            "status": self.status,
            "moves": self.moves_count,
            "rows": self.board.rows,
            "columns": self.board.columns,
            "mines": self.board.num_mines,
            "remaining_mines": self.board.get_remaining_mines()
        }
    
    @classmethod
    def create_beginner_game(cls) -> 'Minesweeper':
        """
        Crea un juego de nivel principiante.
        
        Returns:
            Instancia de Minesweeper con configuración de principiante
        """
        return cls(**cls.BEGINNER)
    
    @classmethod
    def create_intermediate_game(cls) -> 'Minesweeper':
        """
        Crea un juego de nivel intermedio.
        
        Returns:
            Instancia de Minesweeper con configuración intermedia
        """
        return cls(**cls.INTERMEDIATE)
    
    @classmethod
    def create_expert_game(cls) -> 'Minesweeper':
        """
        Crea un juego de nivel experto.
        
        Returns:
            Instancia de Minesweeper con configuración experta
        """
        return cls(**cls.EXPERT) 