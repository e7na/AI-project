from lib.data_structure import *
import numpy as np

# initializing the puzzle properties
SLOT = "__"
SEPARATOR = "|"
PLACEHOLDER = -1

FronierOptions = {  
    "A*"  : GBFSFrontier,
    "GBFS": GBFSFrontier,
    "BFS" : QueueFrontier,
    "DFS" : StackFrontier,
}

# check if the current state is the goal state
def is_goal(state):
    # return (np.roll(np.sort(state.copy()), -1) == state).any()
    flat = state.flatten()
    goal = np.array([*range(1, len(flat)), PLACEHOLDER])
    return (flat == goal).all()
    # return (state == np.array([[1, 2, 3], [4, 5, 6], [7, 8, SLOT]])).all()


# the search cost function
def distance(state, width):
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
        if block != PLACEHOLDER:
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
        (col_number, row_number)
        for (row_number, col_number), block in np.ndenumerate(state)
        if block == PLACEHOLDER
    ][0]
    return slot_coords


# return a list of all possible neighbour nodes
def children(state, dimensions):
    height, width = dimensions
    possible_moves = []
    if slot_coords := find_slot(state):  # the slot is the empty block
        slot_x, slot_y = slot_coords
        if slot_x > 0:  # if the slot is on the 2nd or 3rd column
            # this means that a block can be moved to the right
            possible_moves.append(["right", slot_coords])
        if slot_x < width - 1:  # if the slot is on the 1st or 2nd column
            # this means that a block can be moved to the left
            possible_moves.append(["left", slot_coords])
        if slot_y > 0:  # if the slot is on the 2nd or 3rd row
            # this means that a block can be moved down
            possible_moves.append(["down", slot_coords])
        if slot_y < height - 1:  # if the slot is on the 1st or 2nd row
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


def swap_right(state, slot_coords):
    slot_x, slot_y = slot_coords
    # swap the slot with the block on its left in the row
    state[slot_y, slot_x], state[slot_y, slot_x - 1] = (
        state[slot_y, slot_x - 1],
        state[slot_y, slot_x],
    )
    return state


def swap_left(state, slot_coords):
    slot_x, slot_y = slot_coords
    # swap the slot with the block on its right in the row
    state[slot_y, slot_x], state[slot_y, slot_x + 1] = (
        state[slot_y, slot_x + 1],
        state[slot_y, slot_x],
    )
    return state


def swap_up(state, slot_coords):
    slot_x, slot_y = slot_coords
    # swap the slot with the block below it in the same column
    state[slot_y, slot_x], state[slot_y + 1, slot_x] = (
        state[slot_y + 1, slot_x],
        state[slot_y, slot_x],
    )
    return state


def swap_down(state, slot_coords):
    slot_x, slot_y = slot_coords
    # swap the slot with the block above it in the same column
    state[slot_y, slot_x], state[slot_y - 1, slot_x] = (
        state[slot_y - 1, slot_x],
        state[slot_y, slot_x],
    )
    return state
