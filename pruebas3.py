import random
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder

class Minesweeper:
    def __init__(self, rows, columns, num_mines):
        self.rows = rows
        self.columns = columns
        self.num_mines = num_mines
        self.board = self._create_board()
        self.visible = [[False for _ in range(columns)] for _ in range(rows)]
        self.marked = [[False for _ in range(columns)] for _ in range(rows)]
        self.lose = False

    def _create_board(self):
        board = [[0 for _ in range(self.columns)] for _ in range(self.rows)]
        all_positions = [(i, j) for i in range(self.rows) for j in range(self.columns)]
        mine_positions = random.sample(all_positions, self.num_mines)
        
        for row, col in mine_positions:
            board[row][col] = -1
            for i in range(max(0, row-1), min(self.rows, row+2)):
                for j in range(max(0, col-1), min(self.columns, col+2)):
                    if board[i][j] != -1:
                        board[i][j] += 1
        
        return board

    def open_cell(self, row, column):
        if self.lose:
            return "End Game"

        if self.board[row][column] == -1:
            self.lose = True
            self._show_mines()
            return "mine"

        self.visible[row][column] = True
        if self.board[row][column] == 0:
            for i in range(max(0, row-1), min(self.rows, row+2)):
                for j in range(max(0, column-1), min(self.columns, column+2)):
                    if not self.visible[i][j]:
                        self.open_cell(i, j)
        
        return "Victory" if self.check_victory() else "continue"
    
    def mark_mine(self, row, column):
        if not self.lose:
            self.marked[row][column] = not self.marked[row][column]

    def _show_mines(self):
        for i in range(self.rows):
            for j in range(self.columns):
                if self.board[i][j] == -1:
                    self.visible[i][j] = True

    def display_board(self):
        for i in range(self.rows):
            row = ""
            for j in range(self.columns):
                if self.visible[i][j]:
                    if self.board[i][j] == -1:
                        row += "X "
                    else:
                        row += str(self.board[i][j]) + " "
                elif self.marked[i][j]:
                    row += "M "
                else:
                    row += ". "
            print(row)
        print()
    
    def check_victory(self):
        for i in range(self.rows):
            for j in range(self.columns):
                if self.board[i][j] != -1 and not self.visible[i][j]:
                    return False
        return True

def get_ai_move(game, model):
    try:
        flattened_board = [cell for row in game.board for cell in row]
        state = np.array(flattened_board).reshape(1, -1)
        
        # Obtener predicción del modelo
        prediction = model.predict(state, verbose=0)
        action_probabilities = prediction[0]
        
        # Favorecer "open" al inicio del juego
        num_visible = sum(sum(row) for row in game.visible)
        if num_visible < (game.rows * game.columns * 0.2):  # Si menos del 20% está visible
            action_probabilities[0] *= 1.5  # Aumentar probabilidad de "open"
        
        # Limitar el número de marcas basado en el número de minas
        num_marked = sum(sum(row) for row in game.marked)
        if num_marked >= game.num_mines:
            action_probabilities[1] = 0  # No permitir más marcas si ya marcamos suficientes
        
        action = "open" if action_probabilities[0] > action_probabilities[1] else "mark"
        
        # Obtener celdas disponibles con sistema de puntuación
        available_cells = []
        for i in range(game.rows):
            for j in range(game.columns):
                if not game.visible[i][j]:
                    # Puntuación basada en celdas adyacentes descubiertas
                    score = 0
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            ni, nj = i + di, j + dj
                            if (0 <= ni < game.rows and 
                                0 <= nj < game.columns and 
                                game.visible[ni][nj]):
                                score += 1
                    available_cells.append((i, j, score))
        
        if available_cells:
            # Ordenar celdas por puntuación y seleccionar preferentemente las mejores
            available_cells.sort(key=lambda x: x[2], reverse=True)
            if random.random() < 0.7:  # 70% de probabilidad de elegir entre las mejores opciones
                selected = available_cells[0:max(1, len(available_cells)//3)]
            else:
                selected = available_cells
            
            row, col, _ = random.choice(selected)
            return row, col, action
        
        return None
    except Exception as e:
        print(f"Error en predicción: {e}")
        return None

def play_multiple_games(model, num_games=100, rows=5, columns=5, num_mines=5, max_moves_per_game=None):
    if max_moves_per_game is None:
        max_moves_per_game = rows * columns  # Un movimiento por cada celda
        
    victories = 0
    total_moves = 0
    games_data = []
    
    for game_num in range(num_games):
        print(f"\nJuego {game_num + 1}")
        moves = 0
        try:
            game = Minesweeper(rows, columns, num_mines)
            
            while not game.lose and not game.check_victory() and moves < max_moves_per_game:
                game.display_board()
                
                move = get_ai_move(game, model)
                if move is None:
                    print("No hay más movimientos disponibles")
                    break
                    
                row, col, action = move
                print(f"La IA decide {action} en la posición ({row}, {col})")
                
                if action == "open":
                    result = game.open_cell(row, col)
                    if result == "mine":
                        print("¡Juego Terminado - Mina encontrada!")
                        game.display_board()
                        break
                    elif result == "Victory":
                        print("¡Victoria!")
                        game.display_board()
                        victories += 1
                        break
                else:
                    game.mark_mine(row, col)
                
                moves += 1
                
            total_moves += moves
            games_data.append({
                'game_number': game_num + 1,
                'result': 'Victory' if game.check_victory() else 'Loss',
                'moves': moves
            })
            
        except Exception as e:
            print(f"Error en el juego {game_num + 1}: {e}")
            continue
    
    return pd.DataFrame(games_data)

def analyze_and_visualize_results(stats_df):
    if not stats_df.empty:
        # Crear figura con dos subplots
        plt.figure(figsize=(15, 6))
        
        # Gráfico de barras de movimientos por juego
        plt.subplot(1, 2, 1)
        plt.bar(stats_df['game_number'], stats_df['moves'],
               color=np.where(stats_df['result'] == 'Victory', 'green', 'red'))
        plt.title('Movimientos por Juego\n(Verde = Victoria, Rojo = Derrota)')
        plt.xlabel('Número de Juego')
        plt.ylabel('Número de Movimientos')
        
        # Gráfico circular de victorias vs derrotas
        plt.subplot(1, 2, 2)
        victory_count = len(stats_df[stats_df['result'] == 'Victory'])
        loss_count = len(stats_df[stats_df['result'] == 'Loss'])
        plt.pie([victory_count, loss_count],
               labels=['Victorias', 'Derrotas'],
               colors=['green', 'red'],
               autopct='%1.1f%%')
        plt.title('Distribución de Victorias vs Derrotas')
        
        plt.tight_layout()
        plt.show()
        
        # Imprimir estadísticas detalladas
        print("\n=== Estadísticas Detalladas ===")
        print(f"Total de juegos: {len(stats_df)}")
        print(f"Victorias: {victory_count}")
        print(f"Derrotas: {loss_count}")
        print(f"Tasa de victoria: {(victory_count/len(stats_df))*100:.2f}%")
        print(f"Promedio de movimientos por juego: {stats_df['moves'].mean():.2f}")
        print(f"Mediana de movimientos por juego: {stats_df['moves'].median():.2f}")
        print(f"Máximo de movimientos en un juego: {stats_df['moves'].max()}")
        print(f"Mínimo de movimientos en un juego: {stats_df['moves'].min()}")
        
        # Guardar estadísticas en CSV
        output_file = f"model_test_statistics_{len(stats_df)}_games.csv"
        stats_df.to_csv(output_file, index=False)
        print(f"\nEstadísticas guardadas en '{output_file}'")

if __name__ == "__main__":
    try:
        # Configuración
        MODEL_PATH = "minesweeper_ai_model_retrained.h5"  # Ajusta la ruta según necesites
        NUM_GAMES = 200  # Ajusta según necesites
        BOARD_ROWS = 5
        BOARD_COLS = 5
        NUM_MINES = 5
        
        # Cargar modelo
        print(f"Cargando modelo desde {MODEL_PATH}...")
        model = tf.keras.models.load_model(MODEL_PATH)
        
        # Jugar partidas y obtener estadísticas
        print(f"\nJugando {NUM_GAMES} partidas para evaluar el modelo...")
        stats_df = play_multiple_games(
            model,
            num_games=NUM_GAMES,
            rows=BOARD_ROWS,
            columns=BOARD_COLS,
            num_mines=NUM_MINES
        )
        
        # Analizar y visualizar resultados
        analyze_and_visualize_results(stats_df)
        
    except Exception as e:
        print(f"Error general: {e}")