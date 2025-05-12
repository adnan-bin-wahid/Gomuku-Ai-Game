class GomokuGame {
    constructor() {
        this.boardSize = 10;
        this.board = Array(this.boardSize).fill().map(() => Array(this.boardSize).fill(0));
        this.currentPlayer = 1;
        this.gameMode = null;
        this.gameActive = false;
        this.player1Name = '';
        this.player2Name = '';
        this.moveCount = 0;
        this.gameStartTime = null;
        this.gameTimer = null;
        
        // Initialize the board UI
        this.initializeBoard();
        
        // Get modal elements
        this.winnerModal = document.getElementById('winnerModal');
        this.playerNamesModal = document.getElementById('playerNamesModal');
        this.initialControls = document.getElementById('initialControls');
        this.winnerMessage = document.getElementById('winnerMessage');
        
        // Initialize UI elements
        this.playerNameSpan = document.getElementById('playerName');
        this.totalMovesSpan = document.getElementById('totalMoves');
        this.gameTimeSpan = document.getElementById('gameTime');
        this.status = document.getElementById('status');
        
        // Add audio effects
        this.moveSound = new Audio('/static/sounds/move.mp3');
        this.winSound = new Audio('/static/sounds/win.mp3');
        
        // Add event listeners
        document.getElementById('vs-human').addEventListener('click', () => this.showPlayerNamesModal());
        document.getElementById('vs-ai').addEventListener('click', () => {
            this.player1Name = 'You';
            this.player2Name = 'AI';
            this.startGame('ai');
        });
        document.getElementById('playAgain').addEventListener('click', () => this.resetGame());
        document.getElementById('startGameBtn').addEventListener('click', () => this.handleStartGame());
        
        // Bind event listeners
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Add keyboard support
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.resetGame();
            }
        });

        // Add input validation
        const nameInputs = document.querySelectorAll('.player-input input');
        nameInputs.forEach(input => {
            input.addEventListener('input', (e) => {
                e.target.value = e.target.value.replace(/[^a-zA-Z0-9\s]/g, '');
            });
        });
    }

    showPlayerNamesModal() {
        this.playerNamesModal.style.display = 'flex';
        document.getElementById('player1Name').value = '';
        document.getElementById('player2Name').value = '';
    }

    handleStartGame() {
        const player1Input = document.getElementById('player1Name');
        const player2Input = document.getElementById('player2Name');
        
        this.player1Name = player1Input.value.trim() || 'Player 1';
        this.player2Name = player2Input.value.trim() || 'Player 2';
        
        this.playerNamesModal.style.display = 'none';
        this.startGame('human');
    }

    initializeBoard() {
        const boardElement = document.getElementById('board');
        boardElement.innerHTML = '';
        
        for (let i = 0; i < this.boardSize; i++) {
            for (let j = 0; j < this.boardSize; j++) {
                const cell = document.createElement('div');
                cell.className = 'cell';
                cell.dataset.row = i;
                cell.dataset.col = j;
                cell.addEventListener('click', (e) => this.handleCellClick(e));
                boardElement.appendChild(cell);
            }
        }
    }

    startGame(mode) {
        this.gameMode = mode;
        this.gameActive = true;
        this.currentPlayer = 1;
        this.moveCount = 0;
        this.resetBoard();
        
        // Start game timer
        this.gameStartTime = Date.now();
        this.startGameTimer();
        
        this.updateStatus();
        this.addGameStartAnimation();
    }

    startGameTimer() {
        if (this.gameTimer) clearInterval(this.gameTimer);
        
        this.gameTimer = setInterval(() => {
            if (this.gameActive) {
                const elapsed = Math.floor((Date.now() - this.gameStartTime) / 1000);
                const minutes = Math.floor(elapsed / 60);
                const seconds = elapsed % 60;
                this.gameTimeSpan.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
            }
        }, 1000);
    }

    addGameStartAnimation() {
        const board = document.querySelector('.board');
        board.style.animation = 'none';
        board.offsetHeight; // Trigger reflow
        board.style.animation = 'boardAppear 0.5s ease-out';
    }

    resetGame() {
        this.winnerModal.style.display = 'none';
        this.gameActive = false;
        this.gameMode = null;
        this.resetBoard();
        this.status.innerHTML = 'Select game mode to start';
        
        // Remove winning highlights
        const cells = document.getElementsByClassName('cell');
        Array.from(cells).forEach(cell => {
            cell.classList.remove('winning');
        });
    }

    resetBoard() {
        this.board = Array(this.boardSize).fill().map(() => Array(this.boardSize).fill(0));
        const cells = document.getElementsByClassName('cell');
        Array.from(cells).forEach(cell => {
            cell.innerHTML = '';
        });
    }

    makeMove(row, col, switchPlayer = true) {
        // Allow move if cell is empty, regardless of gameActive
        if (this.board[row][col] === 0) {
            this.moveSound.currentTime = 0;
            this.moveSound.play();
            this.board[row][col] = this.currentPlayer;
            this.moveCount++;
            const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
            const stone = document.createElement('div');
            stone.className = `stone ${this.currentPlayer === 1 ? 'black' : 'white'}`;
            cell.appendChild(stone);
            if (this.checkWinner(row, col)) {
                this.endGame(this.currentPlayer);
                return true;
            }
            if (switchPlayer) {
                this.currentPlayer = this.currentPlayer === 1 ? 2 : 1;
                this.updateStatus();
            }
            return true;
        }
        return false;
    }
    
    async handleCellClick(event) {
        if (!this.gameActive) return;
        const row = parseInt(event.target.dataset.row);
        const col = parseInt(event.target.dataset.col);
        if (this.board[row][col] !== 0) return;
        // Human move, don't switch player yet
        if (this.makeMove(row, col, false)) {
            if (this.checkWinner(row, col)) {
                this.endGame(this.currentPlayer);
                return;
            }
            if (this.gameMode === 'ai' && this.gameActive) {
                this.gameActive = false;
                this.updateStatus('AI is thinking...');
                try {
                    const response = await fetch('/make_move', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ board: this.board })
                    });
                    if (!response.ok) throw new Error('Failed to get AI move');
                    const data = await response.json();
                    setTimeout(() => {
                        const { row: aiRow, col: aiCol } = data;
                        this.currentPlayer = 2; // Set to AI
                        if (this.makeMove(aiRow, aiCol, false)) {
                            if (this.checkWinner(aiRow, aiCol)) {
                                this.endGame(this.currentPlayer);
                                return;
                            }
                        }
                        this.currentPlayer = 1; // Back to human
                        this.gameActive = true;
                        this.updateStatus();
                    }, 500);
                } catch (error) {
                    console.error('Error:', error);
                    this.gameActive = true;
                    this.updateStatus('Error occurred during AI move');
                }
            } else {
                // Human vs human: switch player
                this.currentPlayer = this.currentPlayer === 1 ? 2 : 1;
                this.updateStatus();
            }
        }
    }

    checkWinner(row, col) {
        const directions = [
            [0, 1],   // horizontal
            [1, 0],   // vertical
            [1, 1],   // diagonal
            [1, -1],  // anti-diagonal
        ];
        
        const player = this.board[row][col];
        
        for (const [dx, dy] of directions) {
            let count = 1;
            const winningCells = [[row, col]];
            
            // Check in both directions
            for (const factor of [-1, 1]) {
                let r = row + dx * factor;
                let c = col + dy * factor;
                
                while (
                    r >= 0 && r < this.boardSize &&
                    c >= 0 && c < this.boardSize &&
                    this.board[r][c] === player
                ) {
                    count++;
                    winningCells.push([r, c]);
                    r += dx * factor;
                    c += dy * factor;
                }
            }
            
            if (count >= 5) {
                this.highlightWinningCells(winningCells);
                return true;
            }
        }
        
        return false;
    }

    highlightWinningCells(cells) {
        cells.forEach(([row, col]) => {
            const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
            cell.classList.add('winning');
        });
    }

    endGame(winner) {
        this.gameActive = false;
        clearInterval(this.gameTimer);
        
        // Play win sound
        this.winSound.play();
        
        let message;
        if (this.gameMode === 'ai') {
            message = winner === 1 ? 'You win!' : 'AI wins!';
        } else {
            const winnerName = winner === 1 ? this.player1Name : this.player2Name;
            message = `${winnerName} wins!`;
        }
        
        // Update stats
        this.totalMovesSpan.textContent = this.moveCount;
        
        // Show winner modal with animation
        this.winnerMessage.textContent = message;
        this.winnerModal.style.display = 'flex';
        this.createConfetti();
    }

    createConfetti() {
        const confettiCount = 100;
        const confettiContainer = document.querySelector('.confetti');
        confettiContainer.innerHTML = '';
        
        for (let i = 0; i < confettiCount; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti-piece';
            confetti.style.setProperty('--rotation', Math.random() * 360 + 'deg');
            confetti.style.setProperty('--delay', Math.random() * 3 + 's');
            confetti.style.left = Math.random() * 100 + '%';
            confetti.style.backgroundColor = `hsl(${Math.random() * 360}, 70%, 50%)`;
            confettiContainer.appendChild(confetti);
        }
    }

    updateStatus(message) {
        if (message) {
            this.status.innerHTML = message;
        } else {
            const currentPlayerName = this.currentPlayer === 1 ? this.player1Name : this.player2Name;
            const color = this.currentPlayer === 1 ? 'Black' : 'White';
            this.status.innerHTML = `
                <div class="current-player">
                    <span class="player-label">Current Turn:</span>
                    <span id="playerName">${currentPlayerName} (${color})</span>
                </div>
            `;
        }
    }
}

// Initialize the game when the page loads
window.addEventListener('load', () => {
    new GomokuGame();
});