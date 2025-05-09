import numpy as np
from typing import Tuple, List, Optional

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

    def get_best_move(self, board: List[List[int]]) -> Tuple[int, int]:
        """Find the best move using minimax with alpha-beta pruning."""
        board = np.array(board)
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        # Get all valid moves
        valid_moves = self.get_valid_moves(board)
        
        # Sort moves by their evaluation to improve alpha-beta pruning
        moves_with_scores = []
        for move in valid_moves:
            board[move[0]][move[1]] = 2  # AI's move
            score = self.evaluate_board(board)
            board[move[0]][move[1]] = 0  # Undo move
            moves_with_scores.append((score, move))
        
        # Sort moves by score in descending order
        moves_with_scores.sort(reverse=True)
        valid_moves = [move for _, move in moves_with_scores]

        for move in valid_moves:
            board[move[0]][move[1]] = 2  # AI's move
            score = self.minimax(board, self.max_depth, False, alpha, beta)
            board[move[0]][move[1]] = 0  # Undo move
            
            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, best_score)
            if alpha >= beta:
                break
        
        return best_move if best_move is not None else valid_moves[0]

    def minimax(self, board: np.ndarray, depth: int, is_maximizing: bool, alpha: float, beta: float) -> float:
        """Minimax algorithm with alpha-beta pruning."""
        # Early stopping conditions
        if depth == 0:
            return self.evaluate_board(board)
        
        if self.is_winner(board, 1) or self.is_winner(board, 2):
            return self.evaluate_board(board)
        
        valid_moves = self.get_valid_moves(board)
        if not valid_moves:  # Draw
            return 0
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in valid_moves:
                board[move[0]][move[1]] = 2
                eval = self.minimax(board, depth - 1, False, alpha, beta)
                board[move[0]][move[1]] = 0
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in valid_moves:
                board[move[0]][move[1]] = 1
                eval = self.minimax(board, depth - 1, True, alpha, beta)
                board[move[0]][move[1]] = 0
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def evaluate_board(self, board: np.ndarray) -> float:
        """Evaluate the current board state."""
        if self.is_winner(board, 2):  # AI wins
            return 10000
        if self.is_winner(board, 1):  # Human wins
            return -10000
        
        score = 0
        # Evaluate each position
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i][j] != 0:
                    score += self.evaluate_position(board, i, j)
        
        return score

    def evaluate_position(self, board: np.ndarray, row: int, col: int) -> float:
        """Evaluate a position based on its potential."""
        player = board[row][col]
        score = 0
        
        for dir_x, dir_y in self.directions:
            count = 1
            blocks = 0
            empty = 0
            
            # Look in both directions
            for factor in [-1, 1]:
                r = row + dir_x * factor
                c = col + dir_y * factor
                while (0 <= r < self.board_size and 
                       0 <= c < self.board_size and 
                       count < 5):
                    if board[r][c] == player:
                        count += 1
                    elif board[r][c] == 0:
                        empty += 1
                        break
                    else:
                        blocks += 1
                        break
                    r += dir_x * factor
                    c += dir_y * factor
            
            # Score based on the number of stones in a row and blocks
            multiplier = 1 if player == 2 else -1
            if count >= 4:
                score += 100 * multiplier
            elif count == 3 and blocks == 0:
                score += 50 * multiplier
            elif count == 2 and blocks == 0:
                score += 10 * multiplier
            elif count == 1 and blocks == 0:
                score += 1 * multiplier
        
        return score

    def get_valid_moves(self, board: np.ndarray) -> List[Tuple[int, int]]:
        """Get all valid moves, prioritizing moves near existing stones."""
        moves = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i][j] == 0 and self.has_neighbor(board, i, j):
                    moves.append((i, j))
        
        return moves if moves else [(i, j) for i in range(self.board_size) 
                                  for j in range(self.board_size) 
                                  if board[i][j] == 0]

    def has_neighbor(self, board: np.ndarray, row: int, col: int, distance: int = 2) -> bool:
        """Check if a position has any stones within a certain distance."""
        for i in range(max(0, row - distance), min(self.board_size, row + distance + 1)):
            for j in range(max(0, col - distance), min(self.board_size, col + distance + 1)):
                if board[i][j] != 0:
                    return True
        return False

    def is_winner(self, board: np.ndarray, player: int) -> bool:
        """Check if the given player has won."""
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i][j] == player:
                    # Check all directions
                    for dir_x, dir_y in self.directions:
                        count = 1
                        # Look forward
                        r, c = i + dir_x, j + dir_y
                        while (0 <= r < self.board_size and 
                               0 <= c < self.board_size and 
                               board[r][c] == player):
                            count += 1
                            r += dir_x
                            c += dir_y
                        
                        if count >= 5:
                            return True
        
        return False