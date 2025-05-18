import numpy as np
from typing import Tuple, List, Optional
import time

class GomokuAI:
    def __init__(self, max_depth: int = 3):
        self.max_depth = max_depth
        self.board_size = 10
        self.directions = [
            (0, 1),   # horizontal
            (1, 0),   # vertical
            (1, 1),   # diagonal
            (1, -1),  # anti-diagonal
        ]
        self.pattern_scores = {
            '11111': 1000000,  # Win
            '011110': 100000,  # Open four
            '011112': 10000,   # Four with one block
            '211110': 10000,
            '01110': 1000,     # Open three
            '010110': 1000,
            '011100': 1000,
            '001110': 1000,
            '0110': 100,       # Open two
            '01010': 100,
            '00110': 100,
            '01100': 100,
        }
        self.transposition_table = {}
        self.time_limit = 1.5  # seconds per move

    def get_best_move(self, board: List[List[int]]) -> Tuple[int, int]:
        board = np.array(board)
        self.transposition_table.clear()
        start_time = time.time()
        best_move = None
        best_score = float('-inf')
        valid_moves = self.get_valid_moves(board)
        # 1. Check for immediate win or block
        for move in valid_moves:
            board[move[0]][move[1]] = 2
            if self.is_winner(board, 2):
                board[move[0]][move[1]] = 0
                return move
            board[move[0]][move[1]] = 1
            if self.is_winner(board, 1):
                board[move[0]][move[1]] = 0
                return move
            board[move[0]][move[1]] = 0
        # 2. Check for open four or double threat block
        for move in valid_moves:
            board[move[0]][move[1]] = 1
            if self._has_open_four(board, 1) or self._has_double_threat(board, 1):
                board[move[0]][move[1]] = 0
                return move
            board[move[0]][move[1]] = 0
        # 3. Move ordering: sort by advanced evaluation
        moves_with_scores = []
        for move in valid_moves:
            board[move[0]][move[1]] = 2
            score = self.evaluate_board(board)
            board[move[0]][move[1]] = 0
            moves_with_scores.append((score, move))
        moves_with_scores.sort(reverse=True)
        max_moves = self._dynamic_move_limit(board)
        search_moves = [move for _, move in moves_with_scores[:max_moves]]
        for depth in range(2, self.max_depth+1):
            for move in search_moves:
                if time.time() - start_time > self.time_limit:
                    break
                board[move[0]][move[1]] = 2
                score = self.minimax(board, depth-1, False, float('-inf'), float('inf'), start_time)
                board[move[0]][move[1]] = 0
                if score > best_score or best_move is None:
                    best_score = score
                    best_move = move
            if time.time() - start_time > self.time_limit:
                break
        return best_move if best_move else search_moves[0]

    def minimax(self, board, depth, is_max, alpha, beta, start_time):
        if time.time() - start_time > self.time_limit:
            return self.evaluate_board(board)
        board_hash = hash(board.tobytes())
        if (board_hash, depth, is_max) in self.transposition_table:
            return self.transposition_table[(board_hash, depth, is_max)]
        if self.is_winner(board, 2):
            return 1000000 + depth
        if self.is_winner(board, 1):
            return -1000000 - depth
        if depth == 0:
            return self.evaluate_board(board)
        valid_moves = self.get_valid_moves(board)
        moves_with_scores = []
        for move in valid_moves:
            board[move[0]][move[1]] = 2 if is_max else 1
            score = self.quick_pattern_score(board, move[0], move[1], 2 if is_max else 1)
            board[move[0]][move[1]] = 0
            moves_with_scores.append((score, move))
        moves_with_scores.sort(reverse=True)
        max_moves = self._dynamic_move_limit(board)
        search_moves = [move for _, move in moves_with_scores[:max_moves]]
        if is_max:
            value = float('-inf')
            for move in search_moves:
                board[move[0]][move[1]] = 2
                value = max(value, self.minimax(board, depth-1, False, alpha, beta, start_time))
                board[move[0]][move[1]] = 0
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
        else:
            value = float('inf')
            for move in search_moves:
                board[move[0]][move[1]] = 1
                value = min(value, self.minimax(board, depth-1, True, alpha, beta, start_time))
                board[move[0]][move[1]] = 0
                beta = min(beta, value)
                if beta <= alpha:
                    break
        self.transposition_table[(board_hash, depth, is_max)] = value
        return value

    def _has_open_four(self, board, player):
        # Detect open four (011110) for the given player
        patterns = [f'0{player}{player}{player}{player}0']
        for i in range(self.board_size):
            row = ''.join(str(int(x)) for x in board[i, :])
            col = ''.join(str(int(x)) for x in board[:, i])
            for pat in patterns:
                if pat in row or pat in col:
                    return True
        for offset in range(-self.board_size+1, self.board_size):
            diag = ''.join(str(int(x)) for x in np.diagonal(board, offset=offset))
            adiag = ''.join(str(int(x)) for x in np.diagonal(np.fliplr(board), offset=offset))
            for pat in patterns:
                if pat in diag or pat in adiag:
                    return True
        return False

    def _has_double_threat(self, board, player):
        # Detect double open three (two open threes in one move)
        open_three = f'0{player}{player}{player}0'
        count = 0
        for i in range(self.board_size):
            row = ''.join(str(int(x)) for x in board[i, :])
            col = ''.join(str(int(x)) for x in board[:, i])
            count += row.count(open_three)
            count += col.count(open_three)
        for offset in range(-self.board_size+1, self.board_size):
            diag = ''.join(str(int(x)) for x in np.diagonal(board, offset=offset))
            adiag = ''.join(str(int(x)) for x in np.diagonal(np.fliplr(board), offset=offset))
            count += diag.count(open_three)
            count += adiag.count(open_three)
        return count >= 2

    def evaluate_board(self, board):
        # Stronger pattern-based evaluation for both players
        score = 0
        patterns = [
            ('11111', 1000000),
            ('011110', 100000),
            ('011112', 50000),
            ('211110', 50000),
            ('01110', 10000),
            ('010110', 10000),
            ('011100', 10000),
            ('001110', 10000),
            ('0110', 1000),
            ('01010', 1000),
            ('00110', 1000),
            ('01100', 1000),
        ]
        for player in [2, 1]:
            mult = 1 if player == 2 else -1.2  # Defensive bias
            for i in range(self.board_size):
                row = ''.join(str(int(x)) for x in board[i, :])
                col = ''.join(str(int(x)) for x in board[:, i])
                for pat, val in patterns:
                    score += mult * row.count(pat) * val
                    score += mult * col.count(pat) * val
            for offset in range(-self.board_size+1, self.board_size):
                diag = ''.join(str(int(x)) for x in np.diagonal(board, offset=offset))
                adiag = ''.join(str(int(x)) for x in np.diagonal(np.fliplr(board), offset=offset))
                for pat, val in patterns:
                    score += mult * diag.count(pat) * val
                    score += mult * adiag.count(pat) * val
        return score

    def quick_pattern_score(self, board, row, col, player):
        # Fast local pattern check for move ordering
        score = 0
        for dx, dy in self.directions:
            line = []
            for d in range(-4, 5):
                r, c = row + dx*d, col + dy*d
                if 0 <= r < self.board_size and 0 <= c < self.board_size:
                    line.append(board[r][c])
                else:
                    line.append(3-player)  # treat out-of-bounds as opponent
            s = ''.join(str(int(x)) for x in line)
            s = s.replace(str(3-player), '2')
            s = s.replace(str(player), '1')
            for pat, val in self.pattern_scores.items():
                if pat in s:
                    score += val
        return score

    def get_valid_moves(self, board: np.ndarray) -> List[Tuple[int, int]]:
        # Only consider empty cells near existing stones
        moves = set()
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i][j] != 0:
                    for dx in range(-2, 3):
                        for dy in range(-2, 3):
                            ni, nj = i+dx, j+dy
                            if 0 <= ni < self.board_size and 0 <= nj < self.board_size:
                                if board[ni][nj] == 0:
                                    moves.add((ni, nj))
        if not moves:
            return [(self.board_size//2, self.board_size//2)]
        return list(moves)

    def is_winner(self, board: np.ndarray, player: int) -> bool:
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i][j] == player:
                    for dx, dy in self.directions:
                        count = 1
                        for d in range(1, 5):
                            ni, nj = i+dx*d, j+dy*d
                            if 0 <= ni < self.board_size and 0 <= nj < self.board_size and board[ni][nj] == player:
                                count += 1
                            else:
                                break
                        if count >= 5:
                            return True
        return False

    def _dynamic_move_limit(self, board):
        # Fewer moves as board fills up or depth increases
        empty = np.count_nonzero(board == 0)
        if self.max_depth >= 7:
            return 4 if empty < 60 else 6
        elif self.max_depth >= 5:
            return 6 if empty < 60 else 8
        else:
            return 10 if empty < 60 else 12