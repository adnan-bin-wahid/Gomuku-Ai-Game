from flask import Flask, render_template, jsonify, request
from src.gomoku_ai import GomokuAI

app = Flask(__name__)
ai = GomokuAI()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/make_move', methods=['POST'])
def make_move():
    data = request.json
    board = data.get('board')
    player = data.get('player')
    
    if player == 'ai':
        move = ai.get_best_move(board)
        return jsonify({'row': move[0], 'col': move[1]})
    return jsonify({'error': 'Invalid player'})

if __name__ == '__main__':
    app.run(debug=True)