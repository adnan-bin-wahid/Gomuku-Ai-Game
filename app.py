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
        print("Received board:", board)  # Debug log

        if not board:
            return jsonify({'error': 'No board state provided'}), 400

        row, col = ai.get_best_move(board)
        print("AI move:", row, col)  # Debug log
        return jsonify({'row': row, 'col': col})
    except Exception as e:
        print("Error in AI move:", e)  # Debug log
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)