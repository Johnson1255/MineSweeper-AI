import random

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
        return "Continue"
    
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