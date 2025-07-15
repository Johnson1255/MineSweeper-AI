"""
Módulo para visualización del tablero de Buscaminas.
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Optional, Tuple, List
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle

from src.game.minesweeper import Minesweeper, GameEvent


class BoardVisualizer:
    """
    Clase para visualizar el tablero de Buscaminas.
    
    Esta clase proporciona métodos para visualizar el estado del tablero
    utilizando Matplotlib.
    """
    
    # Colores para las celdas
    CELL_COLORS = {
        'hidden': '#AAAAAA',
        'marked': '#FFAA00',
        'mine': '#FF0000',
        'empty': '#FFFFFF',
        1: '#0000FF',
        2: '#008000',
        3: '#FF0000',
        4: '#000080',
        5: '#800000',
        6: '#008080',
        7: '#000000',
        8: '#808080'
    }
    
    def __init__(self, game: Minesweeper, figsize: Tuple[int, int] = (8, 8)):
        """
        Inicializa el visualizador de tablero.
        
        Args:
            game: Instancia del juego de Buscaminas
            figsize: Tamaño de la figura (ancho, alto)
        """
        self.game = game
        self.figsize = figsize
        self.fig = None
        self.ax = None
        self.cells = []
        
        # Registrar manejadores de eventos
        self.game.register_event_handler(GameEvent.CELL_OPENED, self._on_cell_opened)
        self.game.register_event_handler(GameEvent.CELL_MARKED, self._on_cell_marked)
        self.game.register_event_handler(GameEvent.CELL_UNMARKED, self._on_cell_unmarked)
        self.game.register_event_handler(GameEvent.GAME_LOST, self._on_game_lost)
    
    def create_board_figure(self) -> Tuple[plt.Figure, plt.Axes]:
        """
        Crea una figura para visualizar el tablero.
        
        Returns:
            Tupla con la figura y los ejes
        """
        self.fig, self.ax = plt.subplots(figsize=self.figsize)
        self.ax.set_aspect('equal')
        self.ax.set_xlim(-0.05, self.game.board.columns + 0.05)
        self.ax.set_ylim(-0.05, self.game.board.rows + 0.05)
        self.ax.invert_yaxis()  # Para que (0,0) esté arriba a la izquierda
        
        # Configurar ejes
        self.ax.set_xticks(range(self.game.board.columns))
        self.ax.set_yticks(range(self.game.board.rows))
        self.ax.set_xticklabels(range(self.game.board.columns))
        self.ax.set_yticklabels(range(self.game.board.rows))
        self.ax.grid(True, linestyle='-', alpha=0.7)
        
        # Título
        self.ax.set_title(f"Buscaminas ({self.game.board.rows}x{self.game.board.columns}, {self.game.board.num_mines} minas)")
        
        return self.fig, self.ax
    
    def draw_board(self) -> None:
        """Dibuja el estado actual del tablero."""
        if self.fig is None or self.ax is None:
            self.create_board_figure()
        
        # Limpiar celdas anteriores
        for cell in self.cells:
            cell.remove()
        self.cells = []
        
        # Obtener estado del tablero
        board_state = self.game.get_board_state()
        
        # Dibujar celdas
        for i in range(self.game.board.rows):
            for j in range(self.game.board.columns):
                value = board_state[i, j]
                self._draw_cell(i, j, value)
        
        # Actualizar figura
        self.fig.canvas.draw()
    
    def _draw_cell(self, row: int, col: int, value: int) -> None:
        """
        Dibuja una celda individual.
        
        Args:
            row: Fila de la celda
            col: Columna de la celda
            value: Valor de la celda
        """
        # Determinar color y texto
        if value == self.game.board.HIDDEN:
            color = self.CELL_COLORS['hidden']
            text = ''
        elif value == self.game.board.MARKED:
            color = self.CELL_COLORS['marked']
            text = '⚑'
        elif value == -1:  # Mina
            color = self.CELL_COLORS['mine']
            text = '✹'
        elif value == 0:  # Vacío
            color = self.CELL_COLORS['empty']
            text = ''
        else:  # Número
            color = self.CELL_COLORS['empty']
            text = str(value)
            text_color = self.CELL_COLORS.get(value, '#000000')
        
        # Dibujar rectángulo
        rect = Rectangle((col, row), 1, 1, facecolor=color, edgecolor='black', alpha=0.8)
        self.ax.add_patch(rect)
        self.cells.append(rect)
        
        # Añadir texto si es necesario
        if text:
            if value > 0:  # Número
                text_obj = self.ax.text(col + 0.5, row + 0.5, text, ha='center', va='center', 
                                   color=text_color, fontweight='bold', fontsize=12)
            else:  # Marcado o mina
                text_obj = self.ax.text(col + 0.5, row + 0.5, text, ha='center', va='center', 
                                   color='black', fontsize=12)
            self.cells.append(text_obj)
    
    def _on_cell_opened(self, **kwargs) -> None:
        """Manejador para el evento de celda abierta."""
        if self.fig is not None and plt.fignum_exists(self.fig.number):
            self.draw_board()
    
    def _on_cell_marked(self, **kwargs) -> None:
        """Manejador para el evento de celda marcada."""
        if self.fig is not None and plt.fignum_exists(self.fig.number):
            self.draw_board()
    
    def _on_cell_unmarked(self, **kwargs) -> None:
        """Manejador para el evento de celda desmarcada."""
        if self.fig is not None and plt.fignum_exists(self.fig.number):
            self.draw_board()
    
    def _on_game_lost(self, **kwargs) -> None:
        """Manejador para el evento de juego perdido."""
        if self.fig is not None and plt.fignum_exists(self.fig.number):
            self.draw_board()
            self.ax.set_title("¡BOOM! Juego terminado")
    
    def animate_game(self, actions: List[Tuple[int, int, str]], delay: float = 0.5) -> None:
        """
        Anima una secuencia de acciones en el tablero.
        
        Args:
            actions: Lista de tuplas (fila, columna, acción)
            delay: Tiempo de espera entre acciones (segundos)
        """
        import time
        
        self.create_board_figure()
        self.draw_board()
        
        for row, col, action in actions:
            time.sleep(delay)
            
            if action.lower() == 'open':
                self.game.open_cell(row, col)
            elif action.lower() == 'mark':
                self.game.mark_cell(row, col)
            
            self.draw_board()
            plt.pause(0.01)  # Necesario para actualizar la figura en algunos backends
    
    def show(self) -> None:
        """Muestra la visualización del tablero."""
        if self.fig is None:
            self.create_board_figure()
            self.draw_board()
        
        plt.tight_layout()
        plt.show()
    
    def save(self, filepath: str) -> None:
        """
        Guarda la visualización actual en un archivo.
        
        Args:
            filepath: Ruta donde guardar la imagen
        """
        if self.fig is None:
            self.create_board_figure()
            self.draw_board()
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight') 