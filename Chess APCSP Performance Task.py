import pygame
import chess

pygame.init()
width = 640
length = 640
square = width // 8
screen = pygame.display.set_mode((width, length))
white = (255, 255, 255)
black = (0, 0 ,0)
board = chess.Board()
font = pygame.font.SysFont("arial", 32)
def draw_board():
    for row in range(8):
        for col in range(8):
            color = white if (row + col) % 2 == 0 else black
            pygame.draw.rect(screen, color, (col * square, row * square, square, square))
def render_pieces():
    #chess.SQUARES: list of all sqaure names.
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece:
            row = 7 - sq // 8
            col = sq % 8
            # font.render render(text, antialias(boolean, asking to smooth out edges), color, background=None) -> Surface
            text = font.render(piece.symbol(), True, (255,0,0))
            screen.blit(text, (col * square + 12, row * square + 8))

def get_piece_from_sqaure(x, y):
    row = y // square
    col = x // square
    sq =chess.square(col, 7 - row)
    piece = board.piece_at(sq)
    print(piece)


    


    





#dict pieces_images = {
   # "P" =
   # "p" = 
  #  "R" =
   # "r" =
   # "B" = 
   # "b" =
    #"N" = 
    #"n" =
   # "Q" =
   # "q" =
   # "K" = 
   # "k" =
#}


running = True
while running:
    screen.fill((0, 0, 0))
    draw_board()
    render_pieces()
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            get_piece_from_sqaure(x, y)

pygame.quit()

