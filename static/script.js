class GomokuGame {
    constructor() {
        this.boardSize = 10;
        this.board = Array(this.boardSize).fill().map(() => Array(this.boardSize).fill(0));
        this.currentPlayer = 1; // 1 for black (human), 2 for white (AI or human)
        this.gameMode = null; // 'ai' or 'human'
        this.gameActive = false;
        
        // DOM elements
        this.boardElement = document.getElementById('board');
        this.statusElement = document.getElementById('status');
        this.vsHumanBtn = document.getElementById('vs-human');
        this.vsAIBtn = document.getElementById('vs-ai');
        this.resetBtn = document.getElementById('reset');
        
        // Event listeners
        this.vsHumanBtn.addEventListener('click', () => this.startGame('human'));
        this.vsAIBtn.addEventListener('click', () => this.startGame('ai'));
        this.resetBtn.addEventListener('click', () => this.resetGame());
        
        // Initialize board UI
        this.createBoard();
    }
    
    createBoard() {
        this.boardElement.innerHTML = '';
        for (let i = 0; i < this.boardSize; i++) {
            for (let j = 0; j < this.boardSize; j++) {
                const cell = document.createElement('div');
                cell.className = 'cell';
                cell.dataset.row = i;
                cell.dataset.col = j;
                cell.addEventListener('click', (e) => this.handleCellClick(e));
                this.boardElement.appendChild(cell);
            }
        }
    }
    
    startGame(mode) {
        this.gameMode = mode;
        this.gameActive = true;
        this.currentPlayer = 1;
        this.board = Array(this.boardSize).fill().map(() => Array(this.boardSize).fill(0));
        this.createBoard();
        this.vsHumanBtn.style.display = 'none';
        this.vsAIBtn.style.display = 'none';
        this.resetBtn.style.display = 'inline-block';
        this.updateStatus();
    }
    
    resetGame() {
        this.gameActive = false;
        this.vsHumanBtn.style.display = 'inline-block';
        this.vsAIBtn.style.display = 'inline-block';
        this.resetBtn.style.display = 'none';
        this.statusElement.textContent = 'Select game mode to start';
        this.createBoard();
    }
    
    updateStatus() {
        if (!this.gameActive) return;
        const playerText = this.currentPlayer === 1 ? 'Black' : 'White';
        this.statusElement.textContent = `Current player: ${playerText}`;
    }
    
    async handleCellClick(event) {
        if (!this.gameActive) return;
        
        const row = parseInt(event.target.dataset.row);
        const col = parseInt(event.target.dataset.col);
        
        if (this.board[row][col] !== 0) return;
        
        // Make human move
        if (this.makeMove(row, col)) {
            if (this.checkWinner(row, col)) {
                this.endGame(`${this.currentPlayer === 1 ? 'Black' : 'White'} wins!`);
                return;
            }
            
            if (this.isDraw()) {
                this.endGame("It's a draw!");
                return;
            }
            
            // Switch players
            this.currentPlayer = this.currentPlayer === 1 ? 2 : 1;
            this.updateStatus();
            
            // If playing against AI and it's AI's turn
            if (this.gameMode === 'ai' && this.currentPlayer === 2) {
                this.makeAIMove();
            }
        }
    }
    
    async makeAIMove() {
        try {
            const response = await fetch('/make_move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    board: this.board,
                    player: 'ai'
                })
            });
            
            const data = await response.json();
            if (data.error) {
                console.error(data.error);
                return;
            }
            
            const { row, col } = data;
            if (this.makeMove(row, col)) {
                if (this.checkWinner(row, col)) {
                    this.endGame('AI wins!');
                    return;
                }
                
                if (this.isDraw()) {
                    this.endGame("It's a draw!");
                    return;
                }
                
                this.currentPlayer = 1;
                this.updateStatus();
            }
        } catch (error) {
            console.error('Error making AI move:', error);
        }
    }
    
    makeMove(row, col) {
        if (this.board[row][col] === 0) {
            this.board[row][col] = this.currentPlayer;
            const stone = document.createElement('div');
            stone.className = `stone ${this.currentPlayer === 1 ? 'black' : 'white'}`;
            const cell = this.boardElement.children[row * this.boardSize + col];
            cell.appendChild(stone);
            return true;
        }
        return false;
    }
    
    checkWinner(row, col) {
        const directions = [
            [[0, 1], [0, -1]],  // horizontal
            [[1, 0], [-1, 0]],  // vertical
            [[1, 1], [-1, -1]], // diagonal
            [[1, -1], [-1, 1]]  // anti-diagonal
        ];
        
        const player = this.board[row][col];
        
        for (const [dir1, dir2] of directions) {
            let count = 1;
            
            // Check in first direction
            let r = row + dir1[0];
            let c = col + dir1[1];
            while (r >= 0 && r < this.boardSize && c >= 0 && c < this.boardSize && this.board[r][c] === player) {
                count++;
                r += dir1[0];
                c += dir1[1];
            }
            
            // Check in opposite direction
            r = row + dir2[0];
            c = col + dir2[1];
            while (r >= 0 && r < this.boardSize && c >= 0 && c < this.boardSize && this.board[r][c] === player) {
                count++;
                r += dir2[0];
                c += dir2[1];
            }
            
            if (count >= 5) return true;
        }
        
        return false;
    }
    
    isDraw() {
        return this.board.every(row => row.every(cell => cell !== 0));
    }
    
    endGame(message) {
        this.gameActive = false;
        this.statusElement.textContent = message;
    }
}

// Initialize the game when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new GomokuGame();
});