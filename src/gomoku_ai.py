import numpy as np
from typing import List, Tuple
import time

class GomokuAI:
    def __init__(self, max_depth: int = 3, time_limit: int = 5):
        self.max_depth = max_depth
        self.time_limit = time_limit  # seconds
        self.start_time = 0
        self.board_size = 10

    def get_best_move(self, board: List[List[int]]) -> Tuple[int, int]:
        self.start_time = time.time()
        best_score = float('-inf')
        best_move = None
        board = np.array(board)
        
        # Get all valid moves (empty cells)
        valid_moves = self.get_valid_moves(board)
        
        # Prioritize center moves in early game
        if len(valid_moves) > 80:  # Board is mostly empty
            center = self.board_size // 2
            if (center, center) in valid_moves:
                return (center, center)

        alpha = float('-inf')
        beta = float('inf')
        
        for move in valid_moves:
            if time.time() - self.start_time > self.time_limit:
                break
                
            board[move[0]][move[1]] = 2  # AI's move
            score = self.minimax(board, self.max_depth, False, alpha, beta)
            board[move[0]][move[1]] = 0  # Undo move
            
            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, score)
        
        return best_move if best_move else valid_moves[0]

    def minimax(self, board: np.ndarray, depth: int, is_maximizing: bool, alpha: float, beta: float) -> float:
        if time.time() - self.start_time > self.time_limit:
            return self.evaluate_board(board)
            
        if depth == 0:
            return self.evaluate_board(board)
            
        if self.check_winner(board, 2):  # AI wins
            return 10000
        if self.check_winner(board, 1):  # Human wins
            return -10000
            
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

    def get_valid_moves(self, board: np.ndarray) -> List[Tuple[int, int]]:
        valid_moves = []
        # Focus on moves near existing pieces
        padded_board = np.pad(board, 1, mode='constant')
        for i in range(1, self.board_size + 1):
            for j in range(1, self.board_size + 1):
                if padded_board[i][j] == 0:  # Empty cell
                    # Check if there's any piece in neighboring cells
                    neighborhood = padded_board[i-1:i+2, j-1:j+2]
                    if board[i-1][j-1] == 0 and np.any(neighborhood != 0):
                        valid_moves.append((i-1, j-1))
        
        # If no moves near existing pieces, return all empty cells
        if not valid_moves:
            return [(i, j) for i in range(self.board_size) 
                   for j in range(self.board_size) if board[i][j] == 0]
        return valid_moves

    def evaluate_board(self, board: np.ndarray) -> float:
        score = 0
        # Check horizontal, vertical and diagonal lines
        for i in range(self.board_size):
            for j in range(self.board_size):
                # Horizontal
                if j <= self.board_size - 5:
                    score += self.evaluate_line(board[i, j:j+5])
                # Vertical
                if i <= self.board_size - 5:
                    score += self.evaluate_line(board[i:i+5, j])
                # Diagonal
                if i <= self.board_size - 5 and j <= self.board_size - 5:
                    score += self.evaluate_line(np.diagonal(board[i:i+5, j:j+5]))
                    score += self.evaluate_line(np.diagonal(np.fliplr(board[i:i+5, j:j+5])))
        return score

    def evaluate_line(self, line: np.ndarray) -> float:
        if len(line) < 5:
            return 0
            
        ai_count = np.sum(line == 2)
        human_count = np.sum(line == 1)
        empty_count = np.sum(line == 0)
        
        if human_count == 0 and ai_count > 0:
            return pow(10, ai_count)
        if ai_count == 0 and human_count > 0:
            return -pow(10, human_count)
        return 0

    def check_winner(self, board: np.ndarray, player: int) -> bool:
        # Check horizontal
        for i in range(self.board_size):
            for j in range(self.board_size - 4):
                if np.all(board[i, j:j+5] == player):
                    return True
        
        # Check vertical
        for i in range(self.board_size - 4):
            for j in range(self.board_size):
                if np.all(board[i:i+5, j] == player):
                    return True
        
        # Check diagonal (top-left to bottom-right)
        for i in range(self.board_size - 4):
            for j in range(self.board_size - 4):
                if np.all(np.diagonal(board[i:i+5, j:j+5]) == player):
                    return True
        
        # Check diagonal (top-right to bottom-left)
        for i in range(self.board_size - 4):
            for j in range(4, self.board_size):
                if np.all(np.diagonal(np.fliplr(board[i:i+5, j-4:j+1])) == player):
                    return True
        
        return False