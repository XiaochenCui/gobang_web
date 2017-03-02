"""Include game class."""

import numpy as np

BLACK = 1
WHITE = 2


class Game(object):
    """Game class."""

    def __init__(self):
        """Initialize parameters and start game."""
        self._board = None
        self._current_player = None
        self._started = False
        self._finished = False
        self._winner = 0

        self.start_game()

    def start_game(self):
        """Start a game and update initial parameters."""
        self._reset_board()

        self._current_player = BLACK
        self._started = True
        self._finished = False
        self._winner = None

    def _reset_board(self):
        """Reset chessboard."""
        self._board = np.zeros((10, 10), dtype=np.int16)

    def make_move(self, row: int, col: int):
        """
        Set value of board(row, col) to current player.

        Args:
            row:
            col:
        """
        if not self.is_empty(row, col):
            raise ValueError('Invalid move({0}, {1})'.format(row, col))

        row, col = row - 1, col - 1
        player = self.current_player
        self._board[row][col] = player

        # update winner.
        self._winner = self.get_winner(row, col)

        # update current player.
        if self._current_player == BLACK:
            self._current_player = WHITE
        else:
            self._current_player = BLACK

    def is_empty(self, row: int, col: int) -> bool:
        """
        Test and verify if the board(row, col) is empty.

        Args:
            row: 
            col: 

        Returns:
            True for empty, False otherwise.
        """
        if not self.board:
            return False

        if not self.in_board(row, col):
            return False

        if self._board[row][col]:
            return False

        return True

    def in_board(self, row: int, col: int):
        """
        Test and verify if the location(row, col) in board.

        Args:
            row: 
            col: 

        Returns:
            True for location(row, col) in board, False otherwise.
        """
        if not self.board:
            return False

        total_row, total_col = self._board.shape
        if row in range(total_row) and col in range(total_col):
            return True

        return False

    @property
    def total_row(self):
        """Get row numbers of board."""
        if self.board:
            return len(self.board)
        else:
            return 0

    @property
    def total_col(self):
        """Get col numbers of board."""
        if self.board:
            return len(self.board[0])
        else:
            return 0

    @property
    def board(self):
        """
        Get current board in list type.

        Returns:
            :obj:`list`, None otherwise
        """
        if self._board is None:
            return None
        return self._board.tolist()

    @property
    def current_player(self):
        """Get current player."""
        return self._current_player

    @property
    def finished(self):
        """True for game finished, False otherwise."""
        return self._finished

    @property
    def winner(self):
        """Get winner."""
        return self._winner

    def print_board(self):
        """Print current board."""
        s = ''
        for row in self.board:
            s += '+---' * self.total_col
            s += '\n'
            for col in row:
                s += '| {i} '.format(i=col)
            s += '\n'
        print(s)

    def get_winner(self, row: int, col: int) -> object:
        """
        Verify whether win from 8 directions around current location(row, col).

        Returns:
            object: Player for winner, None otherwise.
        """
        player = int(self._board[row][col])

        # 设置四个寻找方向
        directions = ((1, 0), (0, 1), (1, -1), (1, 1))

        situations = [1 for i in range(4)]

        for i in range(len(directions)):
            # 正向寻找
            move_row, move_col = directions[i]

            temp_row, temp_col = row, col

            for j in range(4):
                temp_row += move_row
                temp_col += move_col

                if self.board[temp_row][temp_col] != player:
                    break

                situations[i] += 1

            # 反向寻找
            move_row, move_col = -move_row, -move_col

            temp_row, temp_col = row, col

            for j in range(4):
                temp_row += move_row
                temp_col += move_col

                if self.board[temp_row][temp_col] != player:
                    break

                situations[i] += 1

            if situations[i] == 5:
                self._finished = True
                return player

        return


# Sample test.
if __name__ == '__main__':
    g = Game()
    for i in range(1, 6):
        g.make_move(i, 2)
        g.make_move(i, 3)
        g.print_board()
        print(g.winner)
