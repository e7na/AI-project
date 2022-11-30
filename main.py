import time
from data_structure import *

# initializing the puzzle properties
width, height = 3, 3
input = "puzzle.txt"
with open(input) as p:
    puzzle = p.read().splitlines()

# for the goal check
def is_goal(state):
    return state == ["123", "456", "78 "]


# locating the empty slot
def find_slot(state):
    for row_number, row in enumerate(state):
        col_number = row.find(" ")  # col_number = -1 if " " not found
        if col_number >= 0:  # if " " exists on the current row
            # return its coordinates
            return [row_number, col_number]


def swapr(ar, r, c):
    x = list(ar[r])
    x[c - 1], x[c] = x[c], x[c - 1]
    x = "".join(x)
    ar[r] = "".join(x)
    return ar


def swapl(ar, r, c):
    x = list(ar[r])
    x[c], x[c + 1] = x[c + 1], x[c]
    ar[r] = "".join(x)
    return ar


def swapup(ar, r, c):
    x = list(ar[r])
    y = list(ar[r + 1])
    y[c], x[c] = x[c], y[c]
    ar[r], ar[r + 1] = "".join(x), "".join(y)
    return ar


def swapdw(ar, r, c):
    x = list(ar[r])
    y = list(ar[r - 1])
    y[c], x[c] = x[c], y[c]
    ar[r], ar[r - 1] = "".join(x), "".join(y)
    return ar


def move(possible_move, state):
    f = 0
    b = []
    for row in state:
        b.append(row)
        f += 1
    action = possible_move[0]
    r, c = possible_move[1][0], possible_move[1][1]
    if action == "up":
        b = swapup(b, r, c)
    elif action == "dw":
        b = swapdw(b, r, c)
    elif action == "r":
        b = swapr(b, r, c)
    elif action == "l":
        b = swapl(b, r, c)
    return b


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
    # for each block on each row in the current state
    for current_y, row in enumerate(state):
        for current_x, block in enumerate(row):
            if not block == " ":
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


# returning a list with possible neighbours
def children(state):
    slot_coords = find_slot(state)  # slot = empty block
    x, y = slot_coords[1], slot_coords[0]
    possible_moves = []
    if x > 0:  # if the slot is on the 2nd or 3rd column
        # this means that a block can be moved to the right
        possible_moves.append(["r", slot_coords])
    if x < 2:  # if the slot is on the 1st or 2nd column
        # this means that a block can be moved to the left
        possible_moves.append(["l", slot_coords])
    if y > 0:  # if the slot is on the 2nd or 3rd row
        # this means that a block can be moved down
        possible_moves.append(["dw", slot_coords])
    if y < 2:  # if the slot is on the 1st or 2nd row
        # this means that a block can be moved up
        possible_moves.append(["up", slot_coords])
    return possible_moves


"""Initialise search parameters"""
root = Node(state=puzzle, parent=None, action=None)
# frontier = StackFrontier()
# frontier = QueueFrontier()
frontier = GBFSFrontier()
frontier.add(root)
explored = []
solution = []
start = time.time()
iteration_limit = 500
iteration_count = 0

"""main search loop"""
while not frontier.is_empty() and iteration_count <= iteration_limit:
    iteration_count += 1

    # remove a node from the frontier
    current = frontier.remove()
    # add its state to the explored
    explored.append(current.state)

    # if the current state is the goal, then generate
    # the solution steps list and exit out to print it
    if is_goal(current.state):
        while current.parent is not None:
            # prepend current.action to the solution list
            solution = [current.action, *solution]
            # then move up the path one step
            current = current.parent
        break

    ## expanding the node
    # for each possible move from the current state
    for possible_move in children(current.state):
        new_guess = move(possible_move, current.state)
        # if the state resulting from this move is neither explored nor in the frontier
        if not frontier.contains_state(new_guess) and new_guess not in explored:
            # then put it in a new node and add it to the frontier
            child = Node(
                state=new_guess,
                parent=current,
                action=possible_move[0],
                heuristic=distance(new_guess),
            )
            frontier.add(child)


if iteration_count >= iteration_limit:
    print("attempt timed out")
elif not solution:
    print("no solution")
else:
    print(f"taken time: {round(time.time() - start,5)} seconds")
    print(f"# of explored nodes: {len(explored)}")
    print(f"Frontier length = {len(frontier)}")
    print(f"# of solution steps = {len(solution)}")
    print(f"solution: {solution}")
    print(f"iterations: {iteration_count}")
