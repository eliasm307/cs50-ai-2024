from typing import Optional


class Node():
    def __init__(self, person_id: str, parent: 'Optional[Node]' = None, from_move_id: Optional[str] = None):
        self.person_id = person_id
        self.parent = parent
        self.from_movie_id = from_move_id


class StackFrontier():
    def __init__(self):
        self.frontier: list[Node] = []

    def add(self, node: Node):
        self.frontier.append(node)

    def contains_state(self, person_id: str) -> bool:
        return any(node.person_id == person_id for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node


class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node
