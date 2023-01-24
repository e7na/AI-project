class Node:
    def __init__(self, state, parent=None, children=None, action=None, heuristic=0, is_sol=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.heuristic = heuristic
        self.cost = 0
        self.children = children
        self.is_sol = is_sol
        if self.parent is not None:
            self.parent.add_child(self)
            self.cost = parent.cost + 1
        
        
    # def reverse(self, copy=False):
    #     _next = None
    #     if copy:
    #         current = self.copy()
    #         while current is not None:
    #             _prev = current.parent.copy()
    #             current.parent = _next
    #             _next, current =  current, _prev
    #     else:
    #         current = self
    #         while current is not None:
    #             _prev = current.parent
    #             current.parent = _next
    #             _next, current = current, _prev

            
    def add_child(self, child):
        if self.children is None:
            self.children = []
        if child is not None:
            self.children.append(child)

            
# for the BFS
class QueueFrontier:
    def __init__(self):
        self.frontier = []

    def __len__(self):
        return len(self.frontier)

    def is_empty(self):
        return self.__len__() == 0

    def contains_state(self, state):
        return any((n.state == state).all() for n in self.frontier)
    
    def add(self, state):
        # add to the top of the stack, which is the end of the array
        self.frontier.append(state)

    def remove(self):  # FIFO
        if not self.is_empty():
            return self.frontier.pop(0)


# for the GBFS
class GBFSFrontier(QueueFrontier):
    def remove(self):  # greedy
        # sort the frontier by heuristic values of each node (ascending)
        self.frontier.sort(key=lambda node: node.heuristic)
        # then take out the cheapest, first element and return it
        return super().remove()

class A_star(QueueFrontier):
    def remove(self):
        # sort the frontier by the evaluation function of each node (ascending)
        self.frontier.sort(key=lambda node: (node.heuristic+node.cost))
        # then take out the cheapest, first element and return it
        return super().remove()


# for the DFS
class StackFrontier(QueueFrontier):
    def remove(self):  # LIFO
        if not self.is_empty():
            return self.frontier.pop()
