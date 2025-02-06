import random
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
tf.config.run_functions_eagerly(True)
import matplotlib.pyplot as plt

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
        mines_placed = 0
        max_attempts = 100  # Prevenir bucle infinito
        attempts = 0

        # Crear lista de todas las posiciones posibles
        all_positions = [(i, j) for i in range(self.rows) for j in range(self.columns)]
        
        # Colocar minas usando random.sample
        mine_positions = random.sample(all_positions, self.num_mines)
        
        for row, col in mine_positions:
            board[row][col] = -1
            # Incrementar números alrededor de la mina
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

def generate_game_data(rows, columns, num_mines, num_samples):
    game_data = []
    
    for sample in range(num_samples):
        game = Minesweeper(rows, columns, num_mines)
        move_count = 0
        
        while not game.lose and not game.check_victory() and move_count < 100:
            row = random.randint(0, rows - 1)
            col = random.randint(0, columns - 1)
            
            if not game.visible[row][col]:
                action = random.choice(["open", "mark"])
                
                if action == "open":
                    result = game.open_cell(row, col)
                else:
                    game.mark_mine(row, col)
                    result = "mark"
                
                flattened_board = [cell for row in game.board for cell in row]
                flattened_visible = [cell for row in game.visible for cell in row]
                flattened_marked = [cell for row in game.marked for cell in row]
                game_data.append(flattened_board + flattened_visible + flattened_marked + [result])
                
                move_count += 1
    
    column_names = (
        [f'cell_{i}' for i in range(rows * columns)] +
        [f'visible_{i}' for i in range(rows * columns)] +
        [f'marked_{i}' for i in range(rows * columns)] +
        ['action']
    )
    
    return pd.DataFrame(game_data, columns=column_names)

def get_ai_move(game, model):
    try:
        flattened_board = [cell for row in game.board for cell in row]
        state = np.array(flattened_board).reshape(1, -1)
        
        # Predicción sin timeout
        prediction = model.predict(state, verbose=0)
        action = "open" if np.argmax(prediction) == 0 else "mark"
        
        available_cells = [(i, j) for i in range(game.rows) 
                          for j in range(game.columns) 
                          if not game.visible[i][j]]
        
        if available_cells:
            row, col = random.choice(available_cells)
            return row, col, action
        
        return None
    except Exception as e:
        print(f"Error en predicción: {e}")
        return None

def play_ai_game(model, rows=5, columns=5, num_mines=5):
    game = Minesweeper(rows, columns, num_mines)
    moves = 0
    
    while not game.lose and not game.check_victory() and moves < 100:
        print(f"\nMove {moves + 1}")
        game.display_board()
        
        move = get_ai_move(game, model)
        if move is None:
            print("No more moves available")
            break
            
        row, col, action = move
        print(f"AI decides to {action} at position ({row}, {col})")
        
        if action == "open":
            result = game.open_cell(row, col)
            if result == "mine":
                print("Game Over - Mine hit!")
                game.display_board()
                return False
            elif result == "Victory":
                print("Victory!")
                game.display_board()
                return True
        else:
            game.mark_mine(row, col)
        
        moves += 1
    
    game.display_board()
    return game.check_victory()

def play_multiple_games(model, num_games=100, rows=5, columns=5, num_mines=5, max_moves_per_game=50):
    victories = 0
    total_moves = 0
    games_data = []
    
    for game_num in range(num_games):
        print(f"\nGame {game_num + 1}")
        moves = 0
        try:
            game = Minesweeper(rows, columns, num_mines)
            
            while not game.lose and not game.check_victory() and moves < max_moves_per_game:
                game.display_board()
                
                move = get_ai_move(game, model)
                if move is None:
                    print("No more moves available or prediction error")
                    break
                    
                row, col, action = move
                print(f"AI decides to {action} at position ({row}, {col})")
                
                if action == "open":
                    result = game.open_cell(row, col)
                    if result == "mine":
                        print("Game Over - Mine hit!")
                        game.display_board()
                        break
                    elif result == "Victory":
                        print("Victory!")
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
            
        except KeyboardInterrupt:
            print("\nJuego interrumpido por el usuario")
            break
        except Exception as e:
            print(f"Error en el juego {game_num + 1}: {e}")
            continue
    
    # Estadísticas finales
    games_played = len(games_data)
    if games_played > 0:
        print("\n=== Final Statistics ===")
        print(f"Games played: {games_played}")
        print(f"Victories: {victories}")
        print(f"Win rate: {(victories/games_played)*100:.2f}%")
        print(f"Average moves per game: {total_moves/games_played:.2f}")
    
        # Guardar estadísticas en CSV
        stats_df = pd.DataFrame(games_data)
        stats_df.to_csv('game_statistics.csv', index=False)
        print("\nEstadísticas guardadas en 'game_statistics.csv'")
    
    return pd.DataFrame(games_data)

def generate_training_data_from_ai_games(model, num_games=100, rows=5, columns=5, num_mines=5):
    training_data = []
    
    for game_num in range(num_games):
        print(f"\nGenerando datos del juego {game_num + 1}")
        game = Minesweeper(rows, columns, num_mines)
        moves = 0
        
        while not game.lose and not game.check_victory() and moves < 100:
            # Obtener estado actual
            state = []
            for i in range(game.rows):
                for j in range(game.columns):
                    if game.visible[i][j]:
                        state.append(game.board[i][j])
                    else:
                        state.append(-2 if game.marked[i][j] else -1)
            
            # Obtener movimiento de la IA
            move = get_ai_move(game, model)
            if move is None:
                break
                
            row, col, action = move
            
            # Solo guardar movimientos exitosos
            if action == "open":
                result = game.open_cell(row, col)
                if result != "mine":  # Solo guardamos movimientos que no resultaron en mina
                    training_data.append(state + [row, col, "open"])
            else:
                if game.board[row][col] == -1:  # Solo guardamos marcados correctos
                    game.mark_mine(row, col)
                    training_data.append(state + [row, col, "mark"])
            
            moves += 1
            
            if moves % 10 == 0:
                print(f"Movimientos procesados: {moves}")
    
    # Guardar los datos en CSV
    df = pd.DataFrame(training_data)
    # Asignar nombres de columnas similares a tus datos originales
    column_names = ([f'cell_{i}' for i in range(rows * columns)] + 
                   ['row', 'column', 'action'])
    df.columns = column_names
    
    # Guardar en CSV
    output_file = f"minesweeper_ai_training_data_{len(training_data)}.csv"
    df.to_csv(output_file, index=False)
    print(f"\nDatos guardados en {output_file}")
    
    return df

# Función para reentrenar el modelo
def retrain_model(model, new_data_df):
    # Habilitar ejecución eager
    tf.config.run_functions_eagerly(True)
    
    # Preparar los datos nuevos
    X_new = new_data_df.iloc[:, :-3].values  # Todas las columnas excepto row, column y action
    y_new = new_data_df['action'].values
    
    # Convertir etiquetas
    label_encoder = LabelEncoder()
    y_new = label_encoder.fit_transform(y_new)
    
    # Recrear el modelo con el mismo diseño
    new_model = tf.keras.Sequential([
        tf.keras.layers.Dense(128, activation='relu', input_shape=(X_new.shape[1],)),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(2, activation='softmax')  # Suponiendo clasificación binaria
    ])
    
    # Compilar el nuevo modelo
    new_model.compile(
        optimizer='adam', 
        loss='sparse_categorical_crossentropy', 
        metrics=['accuracy']
    )
    
    # Reentrenar el modelo
    print("\nReentrenando modelo...")
    history = new_model.fit(X_new, y_new, epochs=10, batch_size=32, validation_split=0.2)
    
    return new_model, history

# Uso:
if __name__ == "__main__":
    try:
        model = tf.keras.models.load_model("minesweeper_ai_model.h5")
        stats_df = play_multiple_games(model, num_games=50, max_moves_per_game=50)
        # Generar nuevos datos de entrenamiento
        new_training_data = generate_training_data_from_ai_games(model, num_games=50)
        
        # Reentrenar el modelo
        model, history = retrain_model(model, new_training_data)
        
        # Guardar el modelo reentrenado
        model.save("minesweeper_ai_model_retrained.h5")  # Cambiar new_model por model
        print("\nModelo reentrenado guardado como 'minesweeper_ai_model_retrained.h5'")
        
        # Visualizar el progreso del entrenamiento
        plt.figure(figsize=(10, 5))
        plt.plot(history.history['accuracy'], label='accuracy')
        plt.plot(history.history['val_accuracy'], label='val_accuracy')
        plt.title('Model Accuracy During Retraining')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()
        plt.show()

        # Visualizar estadísticas si hay datos
        if not stats_df.empty:
            plt.figure(figsize=(10, 5))
            plt.bar(stats_df['game_number'], stats_df['moves'], 
                    color=np.where(stats_df['result'] == 'Victory', 'green', 'red'))
            plt.title('Moves per Game (Green = Victory, Red = Loss)')
            plt.xlabel('Game Number')
            plt.ylabel('Number of Moves')
            plt.show()

    except KeyboardInterrupt:
        print("\nPrograma terminado por el usuario")

    except Exception as e:
        print(f"Error general: {e}")