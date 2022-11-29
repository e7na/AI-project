class Node:

    def __init__(self, state, parent=None, action=None, heuristic=0, cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.heuristic = heuristic
        self.cost = cost


# for the DFS
class StackFrontier:

    def __init__(self):
        self.ft = []

    def is_empty(self):
        return len(self.ft) == 0

    def __len__(self):
        return len(self.ft)

    def contains_state(self, state):
        return any(n.state == state for n in self.ft)

    def add(self, s):
        self.ft.append(s)

    def remove(self):
        if not self.is_empty():
            t = self.ft[-1]
            self.ft = self.ft[:-1]
            return t


# for the BFS or dijkstra
class QueueFrontier(StackFrontier):

    def remove(self):
        if not self.is_empty():
            t = self.ft[0]
            self.ft = self.ft[1:]
            return t


def get_heuristic(n):
    return n.heuristic


# for the GBFS or A*
class GBFSFrontier(StackFrontier):

    def remove(self):
        self.ft.sort(key=get_heuristic)
        if not self.is_empty():
            t = self.ft[0]
            self.ft = self.ft[1:]
            return t
