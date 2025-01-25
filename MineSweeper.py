import random
import numpy as np
import pandas as pd
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
        mines_placed = 0

        while mines_placed < self.num_mines:
            row = random.randint(0, self.rows - 1)
            column = random.randint(0, self.columns - 1)

            if board[row][column] == 0:
                board[row][column] = -1 #Mine
                mines_placed += 1

                #Increment numbers around the mine
                for i in range(max(0, row-1), min(self.rows, row+2)):
                    for j in range(max(0,column-1), min(self.columns, column+2)):
                        if board[i][j] != -1:
                            board[i][j] += 1
        return board

    def open_cell(self, row, column):
        if self.lose:
            return "End Game" #If u lose u cannot play anymore

        if self.board[row][column] == -1:
            self.lose = True
            self._show_mines()
            return "mine"

        self.visible[row][column] = True
        if self.board[row][column] == 0:

            #Open adjacent cells
            for i in range(max(0, row-1), min(self.rows, row+2)):
                for j in range(max(0, column-1), min(self.columns, column+2)):
                    if not self.visible[i][j]:
                        self.open_cell(i, j)
        
        if self.check_victory():
            return "Victory"
    
    def mark_mine(self, row, column):
        if not self.lose:
            self.marked[row][column] = not self.marked[row][column]

    def _show_mines(self):
        #Show all the mines when u lose with a 'X'
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
    
# Function to simulate the game and generate training data
def generate_game_data(rows, columns, num_mines, num_samples):
    game_data = []
    
    for _ in range(num_samples):
        game = Minesweeper(rows, columns, num_mines)
        
        while not game.lose and not game.check_victory():
            # Select a random cell to open or mark
            row = random.randint(0, rows - 1)
            col = random.randint(0, columns - 1)
            action = random.choice(["open", "mark"])
            
            if action == "open":
                result = game.open_cell(row, col)
            elif action == "mark":
                game.mark_mine(row, col)
                result = "mark"

            if result == "mine" or result == "Victory":
                break  # End the simulation when a mine is hit or the game is won
            
            # Save game features and action
            flattened_board = [cell for row in game.board for cell in row]
            flattened_visible = [cell for row in game.visible for cell in row]
            flattened_marked = [cell for row in game.marked for cell in row]
            features = flattened_board + flattened_visible + flattened_marked
            game_data.append(features + [result])

    # Create DataFrame with generated data
    df = pd.DataFrame(game_data)
    return df

# Generate game data (adjust number of samples as needed)
game_data = generate_game_data(5, 5, 5, 100)  # 5x5 board with 5 mines and 100 samples

# Save data to CSV file
game_data.to_csv("minesweeper_training_data.csv", index=False)

# Load data from CSV
data = pd.read_csv("minesweeper_training_data.csv")

# Preprocessing
X = data.iloc[:, :-1].values  # All columns except last (action)
y = data.iloc[:, -1].values  # Only action column (last)

# Convert labels to numeric values
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(y)

# Now you can use X and y to train your AI model