def find_deadlocks(new_box_pos, other_boxes_pos, obstacles_pos, goals_pos, size):
    """
    Returns 1 if deadlock, 0 if not found.
    """

    # Box on final position
    if new_box_pos in goals_pos:
        return 0

    # Box in the corner or edge
    if new_box_pos[0] == 0 or new_box_pos[0] == size - 1 or new_box_pos[1] == 0 or new_box_pos[1] == size - 1:
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
            if len(set(other_boxes_pos) & set(pos_to_check)):
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

            if len(set(boxes_to_check) & set(other_boxes_pos)):
                return 1

    """
    TODO
    add detecting such situation:
    --OO--
    --BB--
    """

    return 0