from flask import Flask, render_template, request, jsonify
from src.gomoku_ai import GomokuAI

app = Flask(__name__)
ai = GomokuAI(max_depth=3)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/make_move', methods=['POST'])
def make_move():
    try:
        data = request.get_json()
        board = data.get('board')
        
        if not board:
            return jsonify({'error': 'No board state provided'}), 400
        
        # Get AI's move
        row, col = ai.get_best_move(board)
        return jsonify({'row': row, 'col': col})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)