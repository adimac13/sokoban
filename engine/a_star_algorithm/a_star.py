from queue import PriorityQueue
from itertools import permutations
from .state import State
from .node import Node
from evaluation import find_deadlocks, heuristic_evaluation


def find_shortest_path(player_pos, boxes_pos, goals_pos, obstacles_pos, size):
    pq = PriorityQueue()
    visited = set()
    boxes_pos = tuple(boxes_pos)
    goals_pos = tuple(goals_pos)
    state = State(player_pos, boxes_pos, goals_pos)

    # Crucial element for faster heuristic evaluation
    all_permutations = list(permutations(range(len(boxes_pos))))

    pq.put(Node(None, state, 0, None, heuristic_evaluation(boxes_pos, goals_pos, all_permutations)))

    success = False
    success_node = None
    success_move = None


    while not pq.empty():
        node = pq.get()
        if node.state in visited:
            continue
        visited.add(node.state)
        moves = ['w','a','s','d']
        success = False
        for move in moves:
            new_positions = player_move(move, node.state, obstacles_pos, size)
            if new_positions is None: continue

            new_pos_player = new_positions[0]
            new_box_pos = new_positions[1]

            heuristic_eval = heuristic_evaluation(new_box_pos, goals_pos, all_permutations)

            if not heuristic_eval:
                success = True
                success_node = node
                success_move = move
                break

            new_state = State(new_pos_player, new_box_pos, goals_pos)

            if new_state in visited:
                continue

            pq.put(Node(move, new_state, node.num_of_moves + 1, node, node.num_of_moves + heuristic_eval))

        if success:
            break

    if success:
        final_cmd = []
        print("Route found")
        success_node.get_full_route(final_cmd)
        return final_cmd
    else:
        print("Could not find route")
        return None



def player_move(key, last_state, obstacles_pos, size):
    player_pos = last_state.player_pos
    boxes_pos = list(last_state.boxes_pos)
    goals_pos = last_state.goals_pos

    if key == 'w':
        vec = [-1, 0]  # going up
    elif key == 's':
        vec = [1, 0]  # going down
    elif key == 'a':
        vec = [0, -1]  # going left
    elif key == 'd':
        vec = [0, 1]  # going right

    old_pos_player = player_pos
    old_pos_boxes = boxes_pos.copy()

    new_pos_player = (player_pos[0] + vec[0], player_pos[1] + vec[1])

    # If obstacle or outside the area
    if new_pos_player in obstacles_pos or new_pos_player[0] < 0 or new_pos_player[0] >= size \
            or new_pos_player[1] < 0 or new_pos_player[1] >= size:
        return None

    for i, box in enumerate(boxes_pos):
        if new_pos_player == box:
            new_pos_box = (box[0] + vec[0], box[1] + vec[1])

            if new_pos_box in obstacles_pos or new_pos_box in boxes_pos or new_pos_box[0] < 0 or new_pos_box[
                0] >= size \
                    or new_pos_box[1] < 0 or new_pos_box[1] >= size:
                return None

            boxes_pos[i] = new_pos_box

            # Evaluation
            other_boxes_pos = [box for j, box in enumerate(boxes_pos) if j != i]
            evaluation = find_deadlocks(new_pos_box, other_boxes_pos, obstacles_pos, goals_pos, size)
            if evaluation: return None

            break

    return [new_pos_player, set(boxes_pos)]






if __name__ == "__main__":
    pass