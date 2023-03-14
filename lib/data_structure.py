class Node:
    def __init__(
        self,
        state,
        parent=None,
        children=None,
        action=None,
        heuristic: int = -1,
        is_sol=None,
    ):
        self.state = state
        self.parent = parent
        self.action = action
        self.heuristic = heuristic
        self.children = children
        self.is_sol = is_sol
        if self.parent is not None:
            self.parent.add_child(self)

    def add_child(self, child):
        if self.children is None:
            self.children = []
        if child is not None:
            self.children.append(child)


# for the DFS
class QueueFrontier:
    def __init__(self):
        self.frontier: list[Node] = []

    def __len__(self):
        return len(self.frontier)

    def is_empty(self):
        return len(self) == 0

    def contains_state(self, state):
        return any((n.state == state).all() for n in self.frontier)

    def add(self, state):
        # add to the top of the stack, which is the end of the array
        self.frontier.append(state)

    def remove(self) -> Node | None:  # FIFO
        if not self.is_empty:
            return self.frontier.pop(0)


class PriorityQueue(QueueFrontier):
    def add(self, state: Node):
        super().add(state)
        self._heapify_up((len(self) - 1))

    def remove(self):
        if len(self) == 0:
            return
        heap = self.frontier

        if len(self) == 1:
            return heap.pop()

        minimum = heap[0]
        heap[0] = heap.pop()
        self._heapify_down(0)
        return minimum

    def _swap(self, x, y):
        heap = self.frontier
        heap[x], heap[y] = heap[y], heap[x]

    def _heapify_up(self, idx: int):
        parent = (idx - 1) // 2

        heap = self.frontier
        current = idx
        if current and heap[current].heuristic < heap[parent].heuristic:
            self._swap(current, parent)
            self._heapify_up(parent)

    def _heapify_down(self, idx: int):
        heap = self.frontier
        minimum = idx
        left = 2 * idx + 1
        right = 2 * idx + 2
        if left < len(heap) and heap[left].heuristic < heap[minimum].heuristic:
            minimum = left

        if right < len(heap) and heap[right].heuristic < heap[minimum].heuristic:
            minimum = right

        if minimum != idx:
            self._swap(minimum, idx)
            self._heapify_down(minimum)


# for the BFS or dijkstra
class StackFrontier(QueueFrontier):
    def remove(self):  # LIFO
        if not self.is_empty():
            # pop off the top of the stack; the array's last element
            top = self.frontier[-1]
            # and slice it off the array
            self.frontier = self.frontier[:-1]
            # then return it
            return top
