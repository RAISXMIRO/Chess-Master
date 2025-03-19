import customtkinter
import chess
import chess.engine
from PIL import Image

# Constants
WIDTH = HEIGHT = 512
IMAGES = {}
selected_piece = None

# Main function
def main():
    global window, board_frame, board_chess

    # Function to handle piece clicks
    def on_piece_click(row, column):
        global selected_piece

    # Convert row, column to a chess square
        square = chess.square(column, 7 - row)
        piece = board_chess.piece_at(square)

    # Check if a piece exists and belongs to the user (white)
        if piece and piece.color == chess.WHITE:
            selected_piece = square  # Store the selected piece's position
            show_legal_moves(square)
    
    def show_legal_moves(square):
        for move in board_chess.legal_moves:
            if move.from_square == square:
                target_row = 7 - chess.square_rank(move.to_square)
                target_col = chess.square_file(move.to_square)
                square_button(target_row, target_col)
                
                
    def square_button(row, column):
        color_of_button = "#A9CBA7" if (row + column) % 2 == 0 else "#4B6A4F"
        moving_button = customtkinter.CTkButton(board_frame , text="●" , width=5 , height=5 , fg_color=color_of_button , bg_color=color_of_button , text_color="white")
        moving_button.grid(row = row , column = column)
    

                
                
                

    # Function to update the board GUI
    def update_board():
        for widget in board_frame.winfo_children():
            widget.destroy()
        Draw_Board()
        place_images()

    # Function to draw the chessboard
    def Draw_Board():
        for row in range(8):
            for column in range(8):
                color = "#A9CBA7" if (row + column) % 2 == 0 else "#4B6A4F"
                square = customtkinter.CTkLabel(board_frame, text="", fg_color=color, width=WIDTH // 8, height=HEIGHT // 8)
                square.grid(row=row, column=column)
                if column == 0:
                    num_label = customtkinter.CTkLabel(square, text=f"{8 - row}", text_color='black', font=("Arial", 10))
                    num_label.place(relx=0.05, rely=0.05)
                if row == 7:
                    letter_label = customtkinter.CTkLabel(square, text=f"{chr(97 + column)}", text_color='black', font=("Arial", 10))
                    letter_label.place(relx=0.8, rely=0.69)

    # Function to load piece images
    def load_images():
        black_pieces = ['p', 'n', 'r', 'k', 'q', 'b']
        white_pieces = ['P', 'N', 'R', 'K', 'Q', 'B']

        for piece in black_pieces:
            IMAGES[piece] = customtkinter.CTkImage(light_image=Image.open(f"Black_Pieces/{piece}.png").resize((60, 60)))
        
        for piece in white_pieces:
            IMAGES[piece] = customtkinter.CTkImage(light_image=Image.open(f"White_Pieces/{piece}.png").resize((60, 60)))

    # Function to place piece images on the board
    def place_images():
        for row in range(8):
            for column in range(8):
                square = chess.square(column, 7 - row)  # Convert row/column to chess square
                piece = board_chess.piece_at(square)
                background_color = "#A9CBA7" if (row + column) % 2 == 0 else "#4B6A4F"
                if piece is not None:
                    button = customtkinter.CTkButton(
                        board_frame,
                        image=IMAGES[piece.symbol()],
                        width=WIDTH // 8 - 20,
                        height=HEIGHT // 8 - 20,
                        fg_color=background_color,
                        border_width=0,
                        bg_color=background_color,
                        text='',
                        cursor='hand2',
                        command=lambda r=row, c=column: on_piece_click(r, c)
                    )
                    button.grid(row=row, column=column)

    # Initialize the main window
    window = customtkinter.CTk()
    window.title("Chess Game")
    window.geometry("512x512")

    # Create a frame for the chessboard
    board_frame = customtkinter.CTkFrame(window)
    board_frame.pack()

    # Initialize the chessboard
    board_chess = chess.Board()

    # Draw the board, load images, and place pieces
    Draw_Board()
    load_images()
    place_images()

    # Start the main loop
    window.mainloop()



main()
