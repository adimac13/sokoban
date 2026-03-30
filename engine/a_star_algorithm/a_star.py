import heapq
from .node import Node
from ..evaluation import find_deadlocks, heuristic_evaluation


def find_shortest_path(player_pos, boxes_pos, goals_pos, obstacles_pos, size):
    pq = []
    heapq.heapify(pq)
    visited = set()
    boxes_pos = tuple(boxes_pos)
    goals_pos = tuple(goals_pos)
    state = (player_pos, boxes_pos, goals_pos)

    heapq.heappush(pq, Node(None, state, 0, None, heuristic_evaluation(player_pos, boxes_pos, goals_pos)))

    success = False

    while pq:
        node = heapq.heappop(pq)
        if node.state in visited:
            continue
        visited.add(node.state)
        moves = ['w','a','s','d']
        for move in moves:
            new_positions = player_move(move, node.state, obstacles_pos, size)
            if new_positions is None: continue

            new_pos_player = new_positions[0]
            new_box_pos = new_positions[1]

            heuristic_eval = heuristic_evaluation(new_pos_player, new_box_pos, goals_pos)

            if not heuristic_eval:
                success = True
                success_node = node
                success_move = move
                break

            new_state = (new_pos_player, new_box_pos, goals_pos)

            if new_state in visited:
                continue

            heapq.heappush(pq, Node(move, new_state, node.num_of_moves + 1, node, node.num_of_moves + heuristic_eval))

        if success:
            break

    if success:
        final_cmd = []
        success_node.get_full_route(final_cmd)
        final_cmd.append(success_move)
        return final_cmd
    else:
        return None



def player_move(key, last_state, obstacles_pos, size):
    player_pos = last_state[0]
    boxes_pos = list(last_state[1])
    goals_pos = last_state[2]

    if key == 'w':
        vec = [-1, 0]  # going up
    elif key == 's':
        vec = [1, 0]  # going down
    elif key == 'a':
        vec = [0, -1]  # going left
    elif key == 'd':
        vec = [0, 1]  # going right

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

    return [new_pos_player, tuple(boxes_pos)]

if __name__ == "__main__":
    pass