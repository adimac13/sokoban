def find_deadlocks(new_box_pos, other_boxes_pos, obstacles_pos, goals_pos, size):
    """
    Returns 1 if deadlock, 0 if not found.
    """

    # Box on final position
    if new_box_pos in goals_pos:
        return 0

    # Box in the corner
    if (new_box_pos[0] == 0 or new_box_pos[0] == size - 1) and (new_box_pos[1] == 0 or new_box_pos[1] == size - 1):
        return 1

    # Box on the edge
    goal_on_edge = False
    box_on_edge = False

    if new_box_pos[0] == 0:
        box_on_edge = True
        for goal in goals_pos:
            if goal[0] == 0:
                goal_on_edge = True
                break
    elif new_box_pos[0] == size - 1:
        box_on_edge = True
        for goal in goals_pos:
            if goal[0] == size - 1:
                goal_on_edge = True
                break
    elif new_box_pos[1] == 0:
        box_on_edge = True
        for goal in goals_pos:
            if goal[1] == 0:
                goal_on_edge = True
                break
    elif new_box_pos[1] == size - 1:
        box_on_edge = True
        for goal in goals_pos:
            if goal[1] == size - 1:
                goal_on_edge = True
                break

    if not goal_on_edge and box_on_edge:
        return 1


    # Positions to check around the box
    p = new_box_pos
    around_pos = [(p[0] - 1, p[1]), (p[0] + 1, p[1]), (p[0], p[1] - 1), (p[0], p[1] + 1)]

    # Box locked by the obstacles
    i = set(around_pos) & set(obstacles_pos)
    if len(i) > 2:
        # If there are more than two obstacles, the box can't be moved later
        return 1
    elif len(i) == 2:
        # If the obstacles touch at corners, the box can't be moved later
        i = list(i)
        first = i[0]
        second = i[1]
        if first[0] != second [0] and first[1] != second[1]:
            return 1
    elif len(i) == 1:
        obs = list(i)[0]
        if new_box_pos[1] == obs[1]:
            pos_to_check = [(obs[0], obs[1] - 1), (obs[0], obs[1] + 1)]
            detected_obs = set(pos_to_check) & (set(other_boxes_pos) | set(obstacles_pos))
            if len(detected_obs) > 0:
                for new_obs in detected_obs:
                    new_pos_to_check = (new_box_pos[0], new_obs[1])
                    if new_pos_to_check in (set(other_boxes_pos) | set(obstacles_pos)): return 1
        else:
            pos_to_check = [(obs[0] - 1, obs[1]), (obs[0] + 1, obs[1])]
            detected_obs = set(pos_to_check) & (set(other_boxes_pos) | set(obstacles_pos))
            if len(detected_obs) > 0:
                for new_obs in detected_obs:
                    new_pos_to_check = (new_obs[0], new_box_pos[1])
                    if new_pos_to_check in (set(other_boxes_pos) | set(obstacles_pos)): return 1


    # Box locked by other boxes
    i = set(around_pos) & set(other_boxes_pos)
    i = list(i)

    if len(i) > 1: # If there is more than one box around the moved box
        if len(i) == 2:
            # There are 2 boxes around the moved box
            first = i[0]
            second = i[1]
            if first[0] == second[0] or first[1] == second[1]:
                return 0
            pos_to_check = [(first[0], second[1]), (first[1], second[0])]
            if len((set(other_boxes_pos) | set(obstacles_pos)) & set(pos_to_check)):
                return 1
        else:
            # There are 3 boxes around the moved box
            first = i[0]
            second = i[1]
            third = i[2]

            if first[1]!=second[1] and first[1]!=third[1] and second[1]!=third[1]:
                # The situation is like
                # ---B---       --BPB--
                # --BPB--  or   ---B---

                # Potential boxes on the corner
                if first[0] == second[0]:
                    boxes_to_check = [(third[0], first[1]), (third[0], second[1])]
                elif first[0] == third[0]:
                    boxes_to_check = [(second[0], first[1]), (second[0], third[1])]
                else: # second[0] == third[0]
                    boxes_to_check = [(first[0], second[1]), (first[0], third[1])]
            else:
                # The situation is like
                # ---B---
                # --BP---
                # ---B---

                if first[1] == second[1]:
                    boxes_to_check = [(first[0], third[1]), (second[0], third[1])]
                elif first[1] == third[1]:
                    boxes_to_check = [(first[0], second[1]), (third[0], second[1])]
                else: # second[0] == third [0]
                    boxes_to_check = [(second[0], first[1]), (third[0], first[1])]

            if len(set(boxes_to_check) & (set(other_boxes_pos) | set(obstacles_pos))):
                return 1

    return 0

def evaluate_board(boxes_pos, obstacles_pos, goals_pos, size):
    """
    Returns 1 if any deadlock found, else 0
    """
    for box in boxes_pos:
        other_boxes = [b for b in boxes_pos if b!=box]
        if find_deadlocks(box, other_boxes, obstacles_pos, goals_pos, size):
            return 1
    return 0

def heuristic_evaluation(player_pos, boxes_pos, goals_pos, all_permutations):
    min_dist = float('inf')
    goals_pos = list(goals_pos)
    for j, perm in enumerate(all_permutations):
        dist = 0
        for i,box in enumerate(boxes_pos):
            goal = goals_pos[perm[i]]
            dist += abs(box[0] - goal[0]) + abs(box[1] - goal[1])

        min_dist = min(dist, min_dist)

    if not min_dist: return min_dist

    min_dist_player = float('inf')
    for box in boxes_pos:
        min_dist_player = min(min_dist_player, (abs(player_pos[0] - box[0]) + abs(player_pos[1] - box[1])))

    return min_dist + min_dist_player / 10

if __name__ == "__main__":
    pass