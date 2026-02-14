from collections import defaultdict, deque


def get_frontier_cells(board):
    """Return hidden, unflagged cells adjacent to at least one revealed numbered cell.

    Time complexity: O(R*C*8), where R and C are board dimensions.
    """
    frontier = set()
    for r in range(board.rows):
        for c in range(board.cols):
            cell = board.grid[r][c]
            if cell.is_revealed or cell.is_flagged:
                continue
            for neighbor in cell.neighbors:
                if neighbor.is_revealed and neighbor.number > 0:
                    frontier.add(cell)
                    break
    return frontier


def get_connected_frontier_regions(board):
    """Divide frontier cells into independent connected regions.

    Two frontier cells are connected if they are both constrained by at least one
    common revealed numbered cell. This aligns component boundaries with local
    constraints and supports divide-and-conquer solving.

    Returns:
        list[set[Cell]]: Independent frontier regions.

    Time complexity:
        Let F be frontier size and E the induced constraint edges. O(F + E).
    """
    frontier = get_frontier_cells(board)
    if not frontier:
        return []

    adjacency = {cell: set() for cell in frontier}
    numbered_nodes = board.get_revealed_numbered_nodes()

    # Build an induced graph where hidden frontier cells share an edge when they
    # participate in the same numbered constraint.
    for node in numbered_nodes:
        local_hidden = [n for n in board.get_hidden_neighbors(node) if n in frontier]
        for i in range(len(local_hidden)):
            for j in range(i + 1, len(local_hidden)):
                a = local_hidden[i]
                b = local_hidden[j]
                adjacency[a].add(b)
                adjacency[b].add(a)

    visited = set()
    regions = []

    for start in frontier:
        if start in visited:
            continue

        region = set()
        queue = deque([start])
        visited.add(start)

        while queue:
            curr = queue.popleft()
            region.add(curr)
            for nxt in adjacency[curr]:
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)

        regions.append(region)

    return regions


def map_frontier_constraints(board):
    """Map each frontier cell to nearby revealed numbered constraint cells.

    Useful for heuristic strength estimates and DP region-state signatures.
    """
    constraints = defaultdict(list)
    for node in board.get_revealed_numbered_nodes():
        hidden = board.get_hidden_neighbors(node)
        for h in hidden:
            constraints[h].append(node)
    return constraints
