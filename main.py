from __future__ import absolute_import
import time
import numpy as np
import pygame
import sys
import OpenGL.GL as gl
from imgui.integrations.pygame import PygameRenderer
import imgui
from data_structure import *
from state_ops import *
from yamete import *

# initializing the puzzle properties
# width, height = 3, 3
SLOT = -1
input = "puzzle.txt"
with open(input) as p:
    puzzle = p.read().splitlines()
    # convert the board to an integer matrix
    puzzle = np.array(
        [
            [int(element) if element != " " else SLOT for element in row.split(",")]
            for row in puzzle
        ],
        dtype=np.int8,
    )
    width, height = puzzle.shape


# check if the current state is the goal state
def is_goal(state):
    # return (np.roll(np.sort(state.copy()), -1) == state).any()
    return ([*range(len(state)-1), SLOT] == state).any()
    # return (state == np.array([[1, 2, 3], [4, 5, 6], [7, 8, SLOT]])).all()


# the search cost function
def distance(state):
    """
    the heuristic function is the sum of distances of each block from
    its goal position, the more shuffled the board is, the higher the
    heuristic.
    |1|2|3| to determine the goal position of a block, we first divide
    |4|5|6| its value by the board's width to determine how many rows
    |7|8| | percede the block, this is the block's vertical position.
    The remainder of the division represents how many steps off the new
    row the block is. so to determine the 6 block's goal position,
    we do:
        goal_x = value % width  = 5 % 3  = 2   # 3rd element
        goal_y = value // width = 5 // 3 = 1   # on 2nd row
    where value = (block number) - 1 and x,y index at 0
    """
    result = 0
    # for each block on each row in the given state
    for (current_y, current_x), block in np.ndenumerate(state):
        if block != SLOT:
            value = int(block) - 1
            goal_x = value % width
            goal_y = value // width

            x_distance = abs(
                goal_x - current_x
            )  # horizontal distance is the difference between the
            # block's current x position and its goal x position

            y_distance = abs(
                goal_y - current_y
            )  # vertical distance is the difference between the
            # block's current y position and its goal y position

            ## the heuristic is the sum of all distances for all blocks
            result += x_distance + y_distance
    return result


# locate the empty slot, and return its coordinates
def find_slot(state):
    slot_coords = [
        [col_number, row_number]
        for (row_number, col_number), block in np.ndenumerate(state)
        if block == SLOT
    ][0]
    return slot_coords


# return a list of all possible neighbour nodes
def children(state):
    possible_moves = []
    if slot_coords := find_slot(state):  # the slot is the empty block
        slot_x, slot_y = slot_coords
        if slot_x > 0:  # if the slot is on the 2nd or 3rd column
            # this means that a block can be moved to the right
            possible_moves.append(["right", slot_coords])
        if slot_x < width-1:  # if the slot is on the 1st or 2nd column
            # this means that a block can be moved to the left
            possible_moves.append(["left", slot_coords])
        if slot_y > 0:  # if the slot is on the 2nd or 3rd row
            # this means that a block can be moved down
            possible_moves.append(["down", slot_coords])
        if slot_y < width-1:  # if the slot is on the 1st or 2nd row
            # this means that a block can be moved up
            possible_moves.append(["up", slot_coords])
    return possible_moves


# apply a specific move to a board given its state,
# and return the state resulting from this move
def apply_move(move, state):
    initial_state = (
        state.copy()
    )  # create new object instead of referencing the original
    """
    the move data structure is as follows
    move : list = [
        action : str,
        [ slot_x : int, slot_y : int ]
    ]
    """
    match move:
        case ["up", slot_coords]:
            new_state = swap_up(initial_state, slot_coords)
        case ["down", slot_coords]:
            new_state = swap_down(initial_state, slot_coords)
        case ["left", slot_coords]:
            new_state = swap_left(initial_state, slot_coords)
        case ["right", slot_coords]:
            new_state = swap_right(initial_state, slot_coords)
        case _:
            new_state = initial_state
    return new_state


def display_sol(frames, initial=0):
    idx = initial
    size = 500, 500

    pygame.init()
    pygame.display.set_mode(size, pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)

    imgui.create_context()
    impl = PygameRenderer()

    io = imgui.get_io()
    io.display_size = size

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            impl.process_event(event)
        imgui.new_frame()

        frame = frames[idx]

        with imgui.begin(
            "Board",
            flags=imgui.WINDOW_NO_RESIZE
            | imgui.WINDOW_NO_MOVE
            | imgui.WINDOW_NO_TITLE_BAR,
        ):
            imgui.columns(width)
            for row in frame:
                for block in row:
                    imgui.text(str(block) if block != SLOT else " ")
                    imgui.next_column()
                imgui.separator()
            imgui.columns(1)
            imgui.spacing()
            match [idx, imgui.button("Back"), imgui.same_line(), imgui.button("Next")]:
                case [index, _, _, True] if index < len(frames) - 1:
                    idx += 1
                case [index, True, _, _] if index > 0:
                    idx -= 1

        gl.glClearColor(1, 1, 1, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        imgui.render()
        impl.render(imgui.get_draw_data())

        pygame.display.flip()


"""Initialise search parameters"""
root = Node(state=puzzle, parent=None, action=None, is_sol=1)
# frontier = StackFrontier()  # BFS
# frontier = QueueFrontier()  # DFS
frontier = GBFSFrontier()  # GBFS
frontier.add(root)
explored = []
solution = []
path = []
start = time.time()
iteration_limit = 2000


"""main search loop"""
while not frontier.is_empty() and len(explored) < iteration_limit:
    # remove a node from the frontier
    current = frontier.remove()
    # add its state to the explored
    explored.append(current.state)

    # if the current state is the goal, then generate
    # the solution steps list and exit out to print it
    if is_goal(current.state):
        leaf = current  # parse the solution steps non destructively
        while current.parent is not None:
            current.is_sol = 1
            # prepend current.action to the solution list
            # solution = [current.action, *solution]
            path = [current, *path]
            # then move up the path one step
            current = current.parent
        break

    ## expanding the node
    # for each possible move from the current state
    for possible_move in children(current.state):
        new_guess = apply_move(possible_move, current.state)
        # if the state resulting from this move is neither explored nor in the frontier
        in_explored = any((new_guess == state).all() for state in explored)
        if not frontier.contains_state(new_guess) and not in_explored:
            # then put it in a new node and add it to the frontier
            child = Node(
                state=new_guess,
                parent=current,
                action=possible_move[0],
                heuristic=distance(new_guess),
            )
            frontier.add(child)

if path:
    solution = [node.action for node in path]
    frames = [node.state for node in path]

if len(explored) >= iteration_limit:
    print("attempt timed out")
elif not solution:
    print("no solution")
else:
    print(
        f"taken time: {round(time.time() - start,5)} seconds"
        f"\n# of explored nodes: {len(explored)}"
        f"\nFrontier length = {len(frontier)}"
        f"\n# of solution steps = {len(solution)}"
        f"\nsolution: {solution}"
    )
    graph = lv.treeviz(root)
    graph.view()
    display_sol(frames)
