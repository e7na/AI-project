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


def move(possible_moves, state):
    f = 0
    b = []
    for row in state:
        b.append(row)
        f += 1
    action = possible_moves[0]
    r, c = possible_moves[1][0], possible_moves[1][1]
    if action == "up":
        b = swapup(b, r, c)
    elif action == "dw":
        b = swapdw(b, r, c)
    elif action == "r":
        b = swapr(b, r, c)
    elif action == "l":
        b = swapl(b, r, c)
    return b


# the calculation for the heuristic function
def distance(state):
    result = 0
    for row_number, row in enumerate(state):
        for col_number, block in enumerate(row):
            if not block == " ":
                # each block's value is its number-1
                # because rows and cols index at 0
                value = int(block) - 1
                ## horizontal distance
                x = abs((value % width) - col_number)
                ## vertical distance
                # // is integer division
                # it floors the result
                y = abs((value // width) - row_number)
                result += x + y
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


# now this is the process beginning
node = Node(state=puzzle, parent=None, action=None)
# frontier = StackFrontier()
# frontier = QueueFrontier()
frontier = GBFSFrontier()
frontier.add(node)
explored = []
solution = []
explored_nodes = 0
start = time.time()
iterations_limit = 500
iteration = 0

while True:
    iteration += 1
    # check if the frontier isn't empty
    if frontier.is_empty() or iteration >= iterations_limit:
        print("NO SOLUTION")
        break
    # remove from the frontier
    node = frontier.remove()

    # add to the explored
    explored.append(node.state)
    explored_nodes += 1

    # checking for the goal(will terminate if it's the goal)
    if is_goal(node.state):
        print(f"taken time: {round(time.time() - start,5)} seconds")
        print(f"# of explored nodes: {explored_nodes}")
        while node.parent is not None:
            solution.append(node.action)
            node = node.parent
        solution.reverse()
        print(f"Frontier length = {frontier.__len__()}")
        print(f"# of solution steps = {len(solution)}")
        print(f"solution: {solution}")
        print(f"iterations: {iteration}")
        break

    # expanding the node
    for trans in children(node.state):
        test = move(trans, node.state)
        if not frontier.contains_state(test) and test not in explored:
            child = Node(
                state=test, parent=node, action=trans[0], heuristic=distance(test)
            )
            frontier.add(child)
