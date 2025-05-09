# Gomoku Game

A web-based implementation of Gomoku (Five in a Row) with an AI opponent using minimax algorithm and alpha-beta pruning.

## Features

- Play against AI or another human player
- 10x10 game board
- Interactive web interface
- AI opponent using:
  - Minimax algorithm with alpha-beta pruning
  - Smart evaluation function
  - Early stopping mechanism
  - Neighbor-based move prioritization
- Real-time game status updates
- Player name customization
- Winning move highlighting
- Responsive design

## Technologies Used

- Backend:
  - Python 3
  - Flask (Web Framework)
  - NumPy (Numerical Computing)
- Frontend:
  - HTML5
  - CSS3
  - JavaScript (Vanilla)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Gomuku-Ai-Game
   ```

2. Set up a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Game

1. Start the Flask server:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

## How to Play

1. Choose game mode:
   - "Play vs Human" - Play against another person
   - "Play vs AI" - Play against the computer

2. If playing against another human:
   - Enter names for both players when prompted
   - Black stones play first
   - Players take turns placing stones

3. Game Rules:
   - Players take turns placing stones on intersections
   - Black plays first
   - First player to get 5 stones in a row (horizontally, vertically, or diagonally) wins
   - Game ends in a draw if the board is filled without a winner

## AI Implementation

The AI opponent uses several advanced techniques:

1. **Minimax Algorithm**: Explores possible future game states to make optimal moves

2. **Alpha-Beta Pruning**: Optimizes the search by eliminating branches that won't affect the final decision

3. **Evaluation Function**: Considers:
   - Number of stones in a row
   - Blocking opportunities
   - Position control
   - Pattern recognition

4. **Move Prioritization**: 
   - Focuses on moves near existing stones
   - Evaluates threatening patterns first
   - Considers both offensive and defensive plays

## Project Structure

- `app.py`: Flask application and route handlers
- `src/gomoku_ai.py`: AI implementation with minimax and game logic
- `static/`:
  - `script.js`: Frontend game logic and UI interactions
  - `style.css`: Game styling and animations
- `templates/`:
  - `index.html`: Main game interface

## Contributing

Feel free to submit issues and enhancement requests!

## License

[MIT License](LICENSE)

## Acknowledgments

- Inspired by the traditional Japanese game of Gomoku
- AI implementation based on game theory principles
- Web interface designed for optimal user experience
