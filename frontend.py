# chess_frontend_qt.py
import sys
import chess
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QPoint, QEasingCurve, pyqtSlot
from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QGraphicsOpacityEffect

from chess_backend import ChessEngine
from config import STOCKFISH_PATH

class EngineThread(QThread):
    ai_move_ready = pyqtSignal(chess.Move)

    def __init__(self, engine):
        super().__init__()
        self.engine = engine

    def run(self):
        ai_move = self.engine.get_ai_move()
        self.ai_move_ready.emit(ai_move)

class ChessBoard(QWidget):
    square_clicked = pyqtSignal(int, int)
    animations_finished = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(512, 512)
        self.square_size = 64
        self.pieces = {}
        self.legal_markers = []
        self.current_selection = None
        self.active_animations = []
        
        # Load graphics
        self.board_bg = QPixmap("chessboard.png").scaled(512, 512)
        self.piece_images = {
            'white': {p: QPixmap(f"White_Pieces/{p}.png") for p in ['P','N','B','R','Q','K']},
            'black': {p: QPixmap(f"Black_Pieces/{p.lower()}.png") for p in ['P','N','B','R','Q','K']}
        }

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.board_bg)

    def square_pos(self, square):
        col = chess.square_file(square)
        row = 7 - chess.square_rank(square)
        return QPoint(col * self.square_size + 4, row * self.square_size + 4)

    def animate_move(self, move, is_capture):
        print(is_capture)
        # Get piece labels
        from_label = self.pieces.get(move.from_square)
        to_label = self.pieces.get(move.to_square) if is_capture else None

        # Animate capture
        if is_capture and to_label:
            opacity = QGraphicsOpacityEffect(to_label)
            to_label.setGraphicsEffect(opacity)
            
            fade_anim = QPropertyAnimation(opacity, b"opacity")
            fade_anim.setDuration(300)
            fade_anim.setStartValue(1.0)
            fade_anim.setEndValue(0.0)
            fade_anim.finished.connect(to_label.deleteLater)
            fade_anim.start()
            self.active_animations.append(fade_anim)

        # Animate movement
        if from_label:
            anim = QPropertyAnimation(from_label, b"pos")
            anim.setDuration(400)
            anim.setStartValue(self.square_pos(move.from_square))
            anim.setEndValue(self.square_pos(move.to_square))
            anim.setEasingCurve(QEasingCurve.Type.OutQuad)
            anim.start()
            self.active_animations.append(anim)

            # Update piece tracking after animation
            anim.finished.connect(lambda: self.update_piece_position(move.from_square, move.to_square))

    

    def update_piece_position(self, from_sq, to_sq):
        if from_sq in self.pieces:
            self.pieces[to_sq] = self.pieces.pop(from_sq)

    def update_pieces(self, board_state):
        current_pieces = set(self.pieces.keys())
        new_pieces = {}
        
        for square in chess.SQUARES:
            piece = board_state.piece_at(square)
            if piece:
                if square in self.pieces:
                    new_pieces[square] = self.pieces[square]
                else:
                    self.create_piece(square, piece)
                new_pieces[square] = self.pieces[square]
        
        # Remove captured pieces
        for square in current_pieces - new_pieces.keys():
            if square in self.pieces:
                self.pieces[square].deleteLater()
                del self.pieces[square]

    def create_piece(self, square, piece):
        color = 'white' if piece.color == chess.WHITE else 'black'
        symbol = piece.symbol().upper()
        label = QLabel(self)
        label.setPixmap(self.piece_images[color][symbol].scaled(56, 56))
        label.move(self.square_pos(square))
        label.show()
        self.pieces[square] = label

    def show_legal_moves(self, moves):
        # Clear old markers
        for m in self.legal_markers:
            m.deleteLater()
        self.legal_markers = []
        
        # Add new markers
        for move in moves:
            label = QLabel(self)
            label.setStyleSheet("background-color: rgba(255, 0, 0, 30%); border-radius: 15px;")
            label.resize(30, 30)
            label.move(self.square_pos(move.to_square) + QPoint(17, 17))
            label.show()
            self.legal_markers.append(label)

    def mousePressEvent(self, event):
        pos = event.pos()
        col = pos.x() // self.square_size
        row = pos.y() // self.square_size
        if 0 <= col < 8 and 0 <= row < 8:
            self.square_clicked.emit(col, 7 - row)

class ChessWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = ChessEngine()
        self.ai_thread = None
        self.init_ui()
        self.update_display()

    def init_ui(self):
        self.setWindowTitle("Chess AI")
        self.setFixedSize(512, 512)
        self.board = ChessBoard(self)
        self.board.square_clicked.connect(self.handle_click)
        self.setCentralWidget(self.board)

    def update_display(self):
        self.board.update_pieces(self.engine.board)

    @pyqtSlot(int, int)
    def handle_click(self, file, rank):
        if self.ai_thread and self.ai_thread.isRunning():
            return

        square = chess.square(file, rank)
        piece = self.engine.board.piece_at(square)

        if self.board.current_selection is None:
            if piece and piece.color == chess.WHITE:
                self.board.current_selection = square
                legal_moves = [move for move in self.engine.board.legal_moves 
                              if move.from_square == square]
                self.board.show_legal_moves(legal_moves)
        else:
            move = chess.Move(self.board.current_selection, square)
            if move in self.engine.board.legal_moves:
                self.make_move(move)
            self.board.current_selection = None
            self.board.show_legal_moves([])

    def make_move(self, move):
        print("make move")
        is_capture = self.engine.board.is_capture(move)
        
        # Animate first
        self.board.animate_move(move, is_capture)
        
        
        self.engine.board.push(move)
    
    # Start AI move if needed
        if not self.engine.board.is_game_over():
            self.start_ai_move()
        # Queue AI move after animations

    def start_ai_move(self):
        self.ai_thread = EngineThread(self.engine)
        self.ai_thread.ai_move_ready.connect(self.handle_ai_move)
        self.ai_thread.start()

    def handle_ai_move(self, move):
        is_capture = self.engine.board.is_capture(move)
        self.board.animate_move(move, is_capture)
        self.engine.board.push(move)
        #self.update_display()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChessWindow()
    window.show()
    app.exec()
    window.engine.close()