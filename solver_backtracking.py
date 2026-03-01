def backtrack(index, assignment):
    # Base case: all hidden cells assigned
    if index == len(hidden_list):
        if is_valid(assignment):
            for i, val in enumerate(assignment):
                if val == 1:
                    always_safe.discard(hidden_list[i])
                else:
                    always_mine.discard(hidden_list[i])
        return

    # Try Safe (0) and Mine (1)
    for choice in [0, 1]:
        assignment[index] = choice

        if is_valid(assignment):   # Constraint checking
            backtrack(index + 1, assignment)

        assignment[index] = -1   # Undo (Backtrack)