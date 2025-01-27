import random
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf

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

        while mines_placed < self.num_mines:
            row = random.randint(0, self.rows - 1)
            column = random.randint(0, self.columns - 1)

            if board[row][column] == 0:
                board[row][column] = -1
                mines_placed += 1

                for i in range(max(0, row-1), min(self.rows, row+2)):
                    for j in range(max(0,column-1), min(self.columns, column+2)):
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
    flattened_board = [cell for row in game.board for cell in row]

    state = np.array(flattened_board).reshape(1, -1)
    
    prediction = model.predict(state, verbose=0)
    action = "open" if np.argmax(prediction) == 0 else "mark"
    
    available_cells = [(i, j) for i in range(game.rows) 
                      for j in range(game.columns) 
                      if not game.visible[i][j]]
    
    if available_cells:
        row, col = random.choice(available_cells)
        return row, col, action
    
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

# Usage example:
if __name__ == "__main__":
    model = tf.keras.models.load_model("minesweeper_ai_model.h5")
    play_ai_game(model)