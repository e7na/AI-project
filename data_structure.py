class Node:
    def __init__(self, state, parent=None, action=None, heuristic=0, cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.heuristic = heuristic
        self.cost = cost


# for the DFS
class QueueFrontier:
    def __init__(self):
        self.frontier = []

    def __len__(self):
        return len(self.frontier)

    def is_empty(self):
        return self.__len__() == 0

    def contains_state(self, state):
        return any(n.state == state for n in self.frontier)

    def add(self, state):
        # add to the top of the stack, which is the end of the array
        self.frontier.append(state)

    def remove(self):  # FIFO
        if not self.is_empty():
            # take out the queue's head; the array's first element
            head = self.frontier[0]
            # and slice it off the array
            self.frontier = self.frontier[1:]
            # then return it
            return head


# for the GBFS or A*
class GBFSFrontier(QueueFrontier):
    def remove(self):  # greedy
        # sort the frontier by path cost
        self.frontier.sort(key=lambda node: node.heuristic)
        # then take out the cheapest, first element and return it
        return super().remove()


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
