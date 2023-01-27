import time
import numpy as np
from lib import *

INPUT = "puzzle.txt"


def read_file(file_path):
    with open(file_path) as p:
        return p.read()


# convert the board to an integer matrix
def parse_puzzle(puzzle):
    puzzle = puzzle.splitlines()
    puzzle = np.array(
        [
            [
                int(element) if element != SLOT else PLACEHOLDER
                for element in row.replace(" ", "").split(SEPARATOR)
            ]
            for row in puzzle
        ],
        dtype=np.int8,
    )
    height, width = puzzle.shape
    return puzzle, (height, width)


def search(
    puzzle, dimensions, algo="GBFS"
) -> tuple[list[Node], list[str], Node, list[np.ndarray], list[np.ndarray]]:
    """Initialise search parameters"""
    root = Node(state=puzzle, parent=None, action=None, is_sol=1)
    frontier = FronierOptions[algo]()  # GBFS
    frontier.add(root)
    explored = []
    solution = []
    path = []
    global START_TIME, iteration_limit
    START_TIME = time.time()
    iteration_limit = 5000
    height, width = dimensions

    print()
    """main search loop"""
    while not frontier.is_empty() and len(explored) <= iteration_limit:
        # realtime feedback to determine whether it's hung up or not
        print(
            f"\033[Ffrontier length: {len(frontier)}"
            f"\nexplored length: {len(explored)}",
            end="",
        )
        # remove a node from the frontier
        if not (current := frontier.remove()):
            break
        # add its state to the explored
        explored.append(current.state)

        # if the current state is the goal, then generate
        # the solution steps list and exit out to print it
        if is_goal(current.state):
            leaf = current
            while current.parent is not None:
                current.is_sol = 1
                # prepend current.action to the solution list
                # solution = [current.action, *solution]
                path = [current, *path]
                # then move up the path one step
                current = current.parent
            path = [current, *path]
            break

        ## expanding the node
        # for each possible move from the current state
        for possible_move in children(current.state, dimensions):
            new_guess = apply_move(possible_move, current.state)
            # if the state resulting from this move is neither explored nor in the frontier
            in_explored = any((new_guess == state).all() for state in explored)
            if not frontier.contains_state(new_guess) and not in_explored:
                # then put it in a new node and add it to the frontier
                child = Node(
                    state=new_guess,
                    parent=current,
                    action=possible_move[0],
                    heuristic=distance(new_guess, width),
                )
                frontier.add(child)

    if path:
        solution = [node.action for node in path if node.parent is not None]
        # states = [node.state for node in path]
        return path, solution, root, explored
    else:
        return None


if __name__ == "__main__":
    _, solution, root, explored = search(*parse_puzzle(read_file(INPUT)))
    print("\n")
    if len(explored) >= iteration_limit:
        print("attempt timed out")
    elif not solution:
        print("no solution")
    else:
        print(
            f"search time: {round(time.time() - START_TIME,5)} seconds"
            f"\n# of solution steps = {len(solution)}"
            f"\nsolution: {solution}"
        )
        graph = lv.objviz(root)
        graph.view()
