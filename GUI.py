# Slide Puzzle
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import pygame, sys, random
from pygame.locals import *
from main import main as maze
import numpy as np

# Create the constants (go ahead and experiment with different values)
BOARDWIDTH = 3 # number of columns in the board
BOARDHEIGHT = 3 # number of rows in the board
TILESIZE = 80
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FPS = 30
BLANK = None

#                 R    G    B
BLACK =         (  0,   0,   0)
WHITE =         (255, 255, 255)
BRIGHTBLUE =    (  0,  50, 255)
DARKTURQUOISE = (  3,  54,  73)
GREEN =         (  0, 204,   0)
HOT_PINK = (255, 105, 180)
COL = (85, 0, 42)

BGCOLOR = HOT_PINK
TILECOLOR = COL
TEXTCOLOR = WHITE
BORDERCOLOR = BLACK
BASICFONTSIZE = 20

BUTTONCOLOR = WHITE
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = WHITE

XMARGIN = (WINDOWWIDTH - (TILESIZE * BOARDWIDTH + (BOARDWIDTH - 1))) // 2
YMARGIN = (WINDOWHEIGHT - (TILESIZE * BOARDHEIGHT + (BOARDHEIGHT - 1))) // 2

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

def main(solution, state):
    global FPSCLOCK, DISPLAYSURF, BASICFONT, AUTO_SURF, AUTO_RECT, ALG_SURF, ALG_RECT, SOLVE_SURF, SOLVE_RECT, NEXT_SURF, NEXT_RECT, BACK_SURF, BACK_RECT, RAND_SURF, RAND_RECT

    solution_index = 0
    auto = False # false for manual (enables the back and next buttons)
    solved = True
    current_index, ALG_CHOICES = 0, ['GBFS', 'BFS', 'DFS']
    steps_remaining = 0

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Slide Puzzle Solver')
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)

    # Store the option buttons and their rectangles in OPTIONS.
    AUTO_SURF, AUTO_RECT = makeText('Reset',    TEXTCOLOR, BGCOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 120)
    RAND_SURF, RAND_RECT = makeText('Randomize',    TEXTCOLOR, BGCOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 90)
    ALG_SURF,   ALG_RECT   = makeText(ALG_CHOICES[current_index], TEXTCOLOR, BGCOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 60)
    SOLVE_SURF, SOLVE_RECT = makeText('Solve',    TEXTCOLOR, BGCOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 30)
    NEXT_SURF, NEXT_RECT = makeText('Next',    TEXTCOLOR, BGCOLOR, 130, WINDOWHEIGHT - 30)
    BACK_SURF, BACK_RECT = makeText('Back',    TEXTCOLOR, BGCOLOR, 30, WINDOWHEIGHT - 30)

    mainBoard = generateNewPuzzle(state)
    # returns a list with the solution state
    SOLVEDBOARD = getStartingBoard() # a solved board is the same as the board in a start state.

    while True: # main game loop
        # updating the title of these buttons
        ALG_SURF, ALG_RECT = makeText(ALG_CHOICES[current_index], TEXTCOLOR, BGCOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 60)
        AUTO_SURF, AUTO_RECT = makeText(f'Auto:{auto}',    TEXTCOLOR, BGCOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 120)
        if solution is None:
            steps_remaining_msg = 'ERROR:exceeded the 2kk iterations limit!!!'
            drawBoard(mainBoard, steps_remaining_msg)
        else:
            # this ckeck is to not update the msg if it's less than 0 which means i have another msg i wanna display feel free to delete it anyway
            if steps_remaining >= 0:
                steps_remaining = len(solution) - solution_index
            if steps_remaining == 0:
                steps_remaining_msg = 'GG!'
            elif steps_remaining > 0:
                steps_remaining_msg = f'Steps: {steps_remaining}'
            drawBoard(mainBoard, steps_remaining_msg)
            if solution_index < len(solution) and auto:
                slideAnimation(mainBoard, solution[solution_index], steps_remaining_msg, 8)
                makeMove(mainBoard, solution[solution_index])
                solution_index += 1
        
        checkForQuit()

        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                spotx, spoty = getSpotClicked(mainBoard, event.pos[0], event.pos[1])

                if (spotx, spoty) == (None, None):

                    if NEXT_RECT.collidepoint(event.pos) and not auto and solution_index < len(solution) and solved:             
                        slideAnimation(mainBoard, solution[solution_index], steps_remaining_msg, 8)
                        makeMove(mainBoard, solution[solution_index])
                        solution_index += 1
                    elif BACK_RECT.collidepoint(event.pos) and not auto and 0 < solution_index <= len(solution):             
                        slideAnimation(mainBoard, opposite(solution[solution_index-1]), steps_remaining_msg, 8)
                        makeMove(mainBoard, opposite(solution[solution_index-1]))
                        solution_index -= 1
                    elif RAND_RECT.collidepoint(event.pos):             
                        mainBoard = generateNewPuzzle(4)
                        solved = False
                        steps_remaining_msg = 'press Solve to begin the visualization ;)'
                        steps_remaining = -1
                    elif SOLVE_RECT.collidepoint(event.pos) and mainBoard != SOLVEDBOARD:
                        solution = maze(mainBoard, alg=ALG_CHOICES[current_index])
                        print(solution)
                        solution_index = 0
                        solved = True
                    elif ALG_RECT.collidepoint(event.pos):
                        current_index = (current_index + 1)%3
                        print(f'current: {ALG_CHOICES[current_index]}')
                        solved = False
                    elif AUTO_RECT.collidepoint(event.pos):
                        auto = not auto

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit()


def checkForQuit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back


def opposite(move):
    switch={
        UP: DOWN,
        DOWN: UP,
        LEFT: RIGHT,
        RIGHT: LEFT
    }
    return switch.get(move)


def getStartingBoard():
    # Return a board data structure with tiles in the solved state.
    # For example, if BOARDWIDTH and BOARDHEIGHT are both 3, this function
    # returns [[1, 4, 7], [2, 5, 8], [3, 6, BLANK]]
    counter = 1
    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(counter)
            counter += BOARDWIDTH
        board.append(column)
        counter -= BOARDWIDTH * (BOARDHEIGHT - 1) + BOARDWIDTH - 1

    board[BOARDWIDTH-1][BOARDHEIGHT-1] = BLANK
    return board


def getBlankPosition(board):
    # Return the x and y of board coordinates of the blank space.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == BLANK:
                return (x, y)


def makeMove(board, move):
    # This function does not check if the move is valid.
    blankx, blanky = getBlankPosition(board)

    if move == UP:
        board[blankx][blanky], board[blankx][blanky + 1] = board[blankx][blanky + 1], board[blankx][blanky]
    elif move == DOWN:
        board[blankx][blanky], board[blankx][blanky - 1] = board[blankx][blanky - 1], board[blankx][blanky]
    elif move == LEFT:
        board[blankx][blanky], board[blankx + 1][blanky] = board[blankx + 1][blanky], board[blankx][blanky]
    elif move == RIGHT:
        board[blankx][blanky], board[blankx - 1][blanky] = board[blankx - 1][blanky], board[blankx][blanky]


def isValidMove(board, move):
    blankx, blanky = getBlankPosition(board)
    return (move == UP and blanky != len(board[0]) - 1) or \
           (move == DOWN and blanky != 0) or \
           (move == LEFT and blankx != len(board) - 1) or \
           (move == RIGHT and blankx != 0)


def getRandomMove(board, lastMove=None):
    # start with a full list of all four moves
    validMoves = [UP, DOWN, LEFT, RIGHT]

    # remove moves from the list as they are disqualified
    if lastMove == UP or not isValidMove(board, DOWN):
        validMoves.remove(DOWN)
    if lastMove == DOWN or not isValidMove(board, UP):
        validMoves.remove(UP)
    if lastMove == LEFT or not isValidMove(board, RIGHT):
        validMoves.remove(RIGHT)
    if lastMove == RIGHT or not isValidMove(board, LEFT):
        validMoves.remove(LEFT)

    # return a random move from the list of remaining moves
    return random.choice(validMoves)


def getLeftTopOfTile(tileX, tileY):
    left = XMARGIN + (tileX * TILESIZE) + (tileX - 1)
    top = YMARGIN + (tileY * TILESIZE) + (tileY - 1)
    return (left, top)


def getSpotClicked(board, x, y):
    # from the x & y pixel coordinates, get the x & y board coordinates
    for tileX in range(len(board)):
        for tileY in range(len(board[0])):
            left, top = getLeftTopOfTile(tileX, tileY)
            tileRect = pygame.Rect(left, top, TILESIZE, TILESIZE)
            if tileRect.collidepoint(x, y):
                return (tileX, tileY)
    return (None, None)


def drawTile(tilex, tiley, number, adjx=0, adjy=0):
    # draw a tile at board coordinates tilex and tiley, optionally a few
    # pixels over (determined by adjx and adjy)
    left, top = getLeftTopOfTile(tilex, tiley)
    pygame.draw.rect(DISPLAYSURF, TILECOLOR, (left + adjx, top + adjy, TILESIZE, TILESIZE))
    textSurf = BASICFONT.render(str(number), True, TEXTCOLOR)
    textRect = textSurf.get_rect()
    textRect.center = left + int(TILESIZE / 2) + adjx, top + int(TILESIZE / 2) + adjy
    DISPLAYSURF.blit(textSurf, textRect)


def makeText(text, color, bgcolor, top, left):
    # create the Surface and Rect objects for some text.
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)


def drawBoard(board, message):
    DISPLAYSURF.fill(BGCOLOR)
    if message:
        textSurf, textRect = makeText(message, MESSAGECOLOR, BGCOLOR, 5, 5)
        DISPLAYSURF.blit(textSurf, textRect)

    for tilex in range(len(board)):
        for tiley in range(len(board[0])):
            if board[tilex][tiley]:
                drawTile(tilex, tiley, board[tilex][tiley])

    left, top = getLeftTopOfTile(0, 0)
    width = BOARDWIDTH * TILESIZE
    height = BOARDHEIGHT * TILESIZE
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (left - 5, top - 5, width + 11, height + 11), 4)

    DISPLAYSURF.blit(AUTO_SURF, AUTO_RECT)
    DISPLAYSURF.blit(RAND_SURF, RAND_RECT)
    DISPLAYSURF.blit(ALG_SURF, ALG_RECT)
    DISPLAYSURF.blit(SOLVE_SURF, SOLVE_RECT)
    DISPLAYSURF.blit(NEXT_SURF, NEXT_RECT)
    DISPLAYSURF.blit(BACK_SURF, BACK_RECT)


def slideAnimation(board, direction, message, animationSpeed):
    # Note: This function does not check if the move is valid.

    blankx, blanky = getBlankPosition(board)
    if direction == UP:
        movex = blankx
        movey = blanky + 1
    elif direction == DOWN:
        movex = blankx
        movey = blanky - 1
    elif direction == LEFT:
        movex = blankx + 1
        movey = blanky
    elif direction == RIGHT:
        movex = blankx - 1
        movey = blanky

    # prepare the base surface
    drawBoard(board, message)
    baseSurf = DISPLAYSURF.copy()
    # draw a blank space over the moving tile on the baseSurf Surface.
    moveLeft, moveTop = getLeftTopOfTile(movex, movey)
    pygame.draw.rect(baseSurf, BGCOLOR, (moveLeft, moveTop, TILESIZE, TILESIZE))

    for i in range(0, TILESIZE, animationSpeed):
        # animate the tile sliding over
        checkForQuit()
        DISPLAYSURF.blit(baseSurf, (0, 0))
        if direction == UP:
            drawTile(movex, movey, board[movex][movey], 0, -i)
        if direction == DOWN:
            drawTile(movex, movey, board[movex][movey], 0, i)
        if direction == LEFT:
            drawTile(movex, movey, board[movex][movey], -i, 0)
        if direction == RIGHT:
            drawTile(movex, movey, board[movex][movey], i, 0)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def generateNewPuzzle(numSlides):   
    # num slide can be  of 2:
    # 1- a state so u just need to draw it
    if type(numSlides) == list: # bgad??????
        board = numSlides
        drawBoard(board, '')
        pygame.display.update()
        return board
    # an integer that u want to generate a random state with the steps is that number
    else:
        board = getStartingBoard()
        drawBoard(board, '')
        pygame.display.update()
        pygame.time.wait(500) # pause 500 milliseconds for effect
        lastMove = None
        for i in range(numSlides):
            move = getRandomMove(board, lastMove)
            slideAnimation(board, move, 'Generating new puzzle...', animationSpeed=TILESIZE // 3)
            makeMove(board, move)
            lastMove = move
        return board

# if u wanna customize the puzzle from a txt file HERE instead of giving a state 
if __name__ == '__main__':    
    # state = [[1, BLANK, 4], [2, 5, 7], [3, 6, 8]]

    with open("./puzzle.txt") as p:
        prob = p.read().splitlines()
        state = np.array([
                [int(element) if element != " " else BLANK for element in row]
                for row in prob
            ], dtype=object).transpose().tolist()
    so = maze(puzzle=state,alg='GBFS')
    main(so,state)