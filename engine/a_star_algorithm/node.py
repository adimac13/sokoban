class Node:
    def __init__(self, cmd, state, num_of_moves, previous, priority):
        self.cmd = cmd
        self.state = state
        self.num_of_moves = num_of_moves
        self.previous = previous
        self.priority = priority

    def __lt__(self, other):
        if self.priority < other.priority:
            return True
        if self.priority > other.priority:
            return False
        if self.num_of_moves < other.num_of_moves:
            return True
        return False

    def get_full_route(self, final_cmd):
        if self.previous is not None:
            self.previous.get_full_route(final_cmd)
            final_cmd.append(self.cmd)