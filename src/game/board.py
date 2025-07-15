"""
Módulo de representación del tablero de Buscaminas.
"""
import numpy as np
import random
from typing import List, Tuple, Set, Optional


class Board:
    """
    Clase que representa el tablero de Buscaminas.
    
    Esta clase se encarga de gestionar la matriz del tablero, colocación de minas,
    cálculo de números y operaciones relacionadas con la representación del estado.
    """
    
    # Constantes para la representación del tablero
    HIDDEN = -1
    MINE = -2
    MARKED = -3
    
    def __init__(self, rows: int, columns: int, num_mines: int):
        """
        Inicializa un nuevo tablero de Buscaminas.
        
        Args:
            rows: Número de filas del tablero
            columns: Número de columnas del tablero
            num_mines: Número de minas a colocar
        """
        self.rows = rows
        self.columns = columns
        self.num_mines = min(num_mines, rows * columns - 1)  # Evitar tablero lleno de minas
        
        # Matrices principales
        self._mine_grid = np.zeros((rows, columns), dtype=int)  # -1 para minas, >=0 para número
        self._visible_grid = np.zeros((rows, columns), dtype=bool)  # True si es visible
        self._marked_grid = np.zeros((rows, columns), dtype=bool)  # True si está marcada
        
        # Colocar minas y calcular números
        self._place_mines()
        self._calculate_adjacent_mines()
        
    def _place_mines(self) -> None:
        """Coloca las minas aleatoriamente en el tablero."""
        # Crear lista de todas las posiciones posibles
        all_positions = [(i, j) for i in range(self.rows) for j in range(self.columns)]
        
        # Seleccionar posiciones para las minas
        mine_positions = random.sample(all_positions, self.num_mines)
        
        # Colocar las minas
        for row, col in mine_positions:
            self._mine_grid[row, col] = -1  # -1 representa una mina
    
    def _calculate_adjacent_mines(self) -> None:
        """Calcula el número de minas adyacentes para cada celda."""
        # Iterar sobre cada celda
        for i in range(self.rows):
            for j in range(self.columns):
                # Saltar si la celda contiene una mina
                if self._mine_grid[i, j] == -1:
                    continue
                
                # Contar minas adyacentes
                count = 0
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        ni, nj = i + di, j + dj
                        if 0 <= ni < self.rows and 0 <= nj < self.columns:
                            if self._mine_grid[ni, nj] == -1:
                                count += 1
                
                self._mine_grid[i, j] = count
    
    def get_cell_value(self, row: int, col: int) -> int:
        """
        Obtiene el valor de una celda del tablero.
        
        Args:
            row: Fila de la celda
            col: Columna de la celda
            
        Returns:
            Valor de la celda (-1 para mina, >=0 para número)
        """
        return self._mine_grid[row, col]
    
    def is_mine(self, row: int, col: int) -> bool:
        """
        Verifica si una celda contiene una mina.
        
        Args:
            row: Fila de la celda
            col: Columna de la celda
            
        Returns:
            True si la celda contiene una mina, False en caso contrario
        """
        return self._mine_grid[row, col] == -1
    
    def is_visible(self, row: int, col: int) -> bool:
        """
        Verifica si una celda es visible para el jugador.
        
        Args:
            row: Fila de la celda
            col: Columna de la celda
            
        Returns:
            True si la celda es visible, False en caso contrario
        """
        return self._visible_grid[row, col]
    
    def is_marked(self, row: int, col: int) -> bool:
        """
        Verifica si una celda está marcada como posible mina.
        
        Args:
            row: Fila de la celda
            col: Columna de la celda
            
        Returns:
            True si la celda está marcada, False en caso contrario
        """
        return self._marked_grid[row, col]
    
    def set_visible(self, row: int, col: int) -> None:
        """
        Establece una celda como visible.
        
        Args:
            row: Fila de la celda
            col: Columna de la celda
        """
        self._visible_grid[row, col] = True
    
    def toggle_mark(self, row: int, col: int) -> None:
        """
        Alterna el estado de marcado de una celda.
        
        Args:
            row: Fila de la celda
            col: Columna de la celda
        """
        self._marked_grid[row, col] = not self._marked_grid[row, col]
    
    def get_adjacent_cells(self, row: int, col: int) -> List[Tuple[int, int]]:
        """
        Obtiene las coordenadas de las celdas adyacentes a una posición.
        
        Args:
            row: Fila de la celda
            col: Columna de la celda
            
        Returns:
            Lista de tuplas (fila, columna) de las celdas adyacentes
        """
        adjacent = []
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                ni, nj = row + di, col + dj
                if 0 <= ni < self.rows and 0 <= nj < self.columns:
                    adjacent.append((ni, nj))
        return adjacent
    
    def get_state_representation(self) -> np.ndarray:
        """
        Obtiene una representación del estado actual del tablero para la IA.
        
        Returns:
            Array de NumPy con la representación del estado
        """
        state = np.zeros((self.rows, self.columns), dtype=int)
        
        for i in range(self.rows):
            for j in range(self.columns):
                if self._visible_grid[i, j]:
                    state[i, j] = self._mine_grid[i, j]
                elif self._marked_grid[i, j]:
                    state[i, j] = self.MARKED
                else:
                    state[i, j] = self.HIDDEN
        
        return state
    
    def get_remaining_mines(self) -> int:
        """
        Obtiene el número de minas que faltan por marcar.
        
        Returns:
            Número de minas restantes (puede ser negativo si se han marcado demasiadas celdas)
        """
        return self.num_mines - np.sum(self._marked_grid)
    
    def are_all_safe_cells_visible(self) -> bool:
        """
        Verifica si todas las celdas seguras (sin minas) son visibles.
        
        Returns:
            True si todas las celdas seguras son visibles, False en caso contrario
        """
        for i in range(self.rows):
            for j in range(self.columns):
                if self._mine_grid[i, j] != -1 and not self._visible_grid[i, j]:
                    return False
        return True 