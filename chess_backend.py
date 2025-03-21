import chess
import chess.engine
from threading import Lock
from config import STOCKFISH_PATH

class ChessEngine:
    def __init__(self):
        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        self.engine.configure({"Skill Level": 5})
        self.lock = Lock()  # Add thread lock
        
    def get_ai_move(self):
        with self.lock:  # Prevent concurrent access
            result = self.engine.play(self.board, chess.engine.Limit(time=0.5))
            return result.move
        
    def make_move(self, move):
        with self.lock:  # Thread-safe move handling
            try:
                self.board.push(move)
                return True
            except Exception as e:
                print(f"Move error: {e}")
                return False
    
   
    def get_legal_moves(self, square=None):
        if square:
            return [move for move in self.board.legal_moves if move.from_square == square]
        return list(self.board.legal_moves)
    
    def is_game_over(self):
        return self.board.is_game_over()
    
    
    def get_board_state(self):
        return self.board.fen()
    
    def reset(self):
        self.board.reset()
    
    def close(self):
        self.engine.quit()
    def get_chess_engine(slef):
        return self.engine
    

if __name__ == "__main__":
    # Example usage
    engine = ChessEngine()
    print(engine.get_legal_moves())
    engine.close()