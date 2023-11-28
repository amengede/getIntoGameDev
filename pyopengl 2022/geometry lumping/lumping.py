import pygame

debug = True

pygame.init()

BACKGROUND = (64, 128, 192)
FOREGROUND = (192, 128, 64)
HIGHLIGHT = (255, 192, 128)
OUTLINE = (16, 32, 64)
FONT = pygame.font.SysFont("arial", 24)
PIECE_SIZE = 30

screen = pygame.display.set_mode((1600,800))

def draw_array(screen, x, y, array):
    # pygame.draw.rect(surface, color, rect)
    # rect = (left, top, width, height)
    rows = len(array)
    cols = len(array[0])
    pygame.draw.rect(screen, FOREGROUND, (x, y, cols * PIECE_SIZE, rows * PIECE_SIZE))
    pygame.draw.rect(screen, OUTLINE, (x, y, cols * PIECE_SIZE, rows * PIECE_SIZE), width=2)

    for col in range(cols):
        for row in range(rows):
            if array[row][col] != 0:
                pygame.draw.rect(screen, HIGHLIGHT, (x + PIECE_SIZE * col, y + PIECE_SIZE * row, PIECE_SIZE, PIECE_SIZE))
                # render(text, antialias, color, background=None) -> surface
                # surface.blit(source, dest, area=None, special_flags=0)
                screen.blit(FONT.render(str(array[row][col]), True, OUTLINE),(x + PIECE_SIZE * col + 5, y + PIECE_SIZE * row))
                pygame.draw.rect(screen, OUTLINE, (x + PIECE_SIZE * col, y + PIECE_SIZE * row, PIECE_SIZE, PIECE_SIZE), width=2)

    for col in range(cols):
        # pygame.draw.line(surface, color, start_pos, end_pos, width=1)
        pygame.draw.line(screen, OUTLINE, (x + PIECE_SIZE * col, y), (x + PIECE_SIZE * col, y + rows * PIECE_SIZE), width=2)
    
    for row in range(rows):
        pygame.draw.line(screen, OUTLINE, (x, y + PIECE_SIZE * row), (x + PIECE_SIZE * cols, y + row * PIECE_SIZE), width=2)

def get_lumped_geometry_from(array):

    rows = len(array)
    cols = len(array[0])

    result = [[0 for col in range(cols)] for row in range(rows)]

    for row in range(rows):
        for col in range(cols):

            if array[row][col] != 0:
                result[row][col] = 15

                #north
                if row == 0 or array[row - 1][col] != 0:
                    result[row][col] -= 1
                
                #east
                if col == (cols - 1) or array[row][col + 1] != 0:
                    result[row][col] -= 2
                
                #south
                if row == (rows - 1) or array[row + 1][col] != 0:
                    result[row][col] -= 4
                
                #west
                if col == 0 or array[row][col - 1] != 0:
                    result[row][col] -= 8
            

    return result

walls = [
  [8,8,8,8,8,8,8,8,8,8,8,4,4,6,4,4,6,4,6,4,4,4,6,4],
  [8,0,0,0,0,0,0,0,0,0,8,4,0,0,0,0,0,0,0,0,0,0,0,4],
  [8,0,3,3,0,0,0,0,0,8,8,4,0,0,0,0,0,0,0,0,0,0,0,6],
  [8,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,6],
  [8,0,3,3,0,0,0,0,0,8,8,4,0,0,0,0,0,0,0,0,0,0,0,4],
  [8,0,0,0,0,0,0,0,0,0,8,4,0,0,0,0,0,6,6,6,0,6,4,6],
  [8,8,8,8,0,8,8,8,8,8,8,4,4,4,4,4,4,6,0,0,0,0,0,6],
  [7,7,7,7,0,7,7,7,7,0,8,0,8,0,8,0,8,4,0,4,0,6,0,6],
  [7,7,0,0,0,0,0,0,7,8,0,8,0,8,0,8,8,6,0,0,0,0,0,6],
  [7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,6,0,0,0,0,0,4],
  [7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,6,0,6,0,6,0,6],
  [7,7,0,0,0,0,0,0,7,8,0,8,0,8,0,8,8,6,4,6,0,6,6,6],
  [7,7,7,7,0,7,7,7,7,8,8,4,0,6,8,4,8,3,3,3,0,3,3,3],
  [2,2,2,2,0,2,2,2,2,4,6,4,0,0,6,0,6,3,0,0,0,0,0,3],
  [2,2,0,0,0,0,0,2,2,4,0,0,0,0,0,0,4,3,0,0,0,0,0,3],
  [2,0,0,0,0,0,0,0,2,4,0,0,0,0,0,0,4,3,0,0,0,0,0,3],
  [1,0,0,0,0,0,0,0,1,4,4,4,4,4,6,0,6,3,3,0,0,0,3,3],
  [2,0,0,0,0,0,0,0,2,2,2,1,2,2,2,6,6,0,0,5,0,5,0,5],
  [2,2,0,0,0,0,0,2,2,2,0,0,0,2,2,0,5,0,5,0,0,0,5,5],
  [2,0,0,0,0,0,0,0,2,0,0,0,0,0,2,5,0,5,0,5,0,5,0,5],
  [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5],
  [2,0,0,0,0,0,0,0,2,0,0,0,0,0,2,5,0,5,0,5,0,5,0,5],
  [2,2,0,0,0,0,0,2,2,2,0,0,0,2,2,0,5,0,5,0,0,0,5,5],
  [2,2,2,2,1,2,2,2,2,2,2,1,2,2,2,5,5,5,5,5,5,5,5,5]
]

lumped = get_lumped_geometry_from(walls)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill(BACKGROUND)
    
    draw_array(screen, 10, 10, walls)

    draw_array(screen, 810, 10, lumped)

    pygame.display.update()