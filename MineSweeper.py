import random

class Minesweeper:
    def __init__(self):
        self.rows = rows
        self.columns = columns
        self.num_mines = num_mines
        self.board = self._create_board()
        self.visible = [[False for _ in range(columns)] for _ in range(rows)]
        self.marked = [[False for _ in range(columns)] for _ in range(rows)]

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
                    for j in range(man(0,column-1), min(self.columns, column+2)):
                        if board[i][j] != -1:
                            board[i][j] += 1
        return board

    def open_cell(self, row, column):
        if self.board[row][column] == -1:
            return "mine"

        self.visible[row][column] = True
        if self.board[row][column] == 0:

            #Open adjacent cells
            for i in range(max(0, row-1), min(self.rows, row+2)):
                for j in range(max(0, column-1), min(self.columns, column+2)):
                    if not self.visible[i][j]:
                        self.open_cell(i, j)
        return "Continue"
    
    def mark_mine(self, row, column):
        self.marked[row][column] = not self.marked[row][column]

    def display_board(self):
        for i in range(self.rows):
            row = ""
            for j in range(self.columns):
                if self.visible[i][j]:
                    row += str(self.board[i][j]) + " "
                elif self.marked[i][j]:
                    row += "M "
                else:
                    row += ". "
            print(row)
        print()