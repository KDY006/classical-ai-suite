"""Bot mau nhom ngoai chuan 2 (Dict Adapter): ham doc lap get_action(obs)."""

from __future__ import annotations

from collections import deque

BOT_NAME = "Bot ngoài: Săn căn cứ (Dict)"
BOT_CLI_NAME = "Bot ngoai: San can cu (Dict)"

_DIRS = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1),
}
_MOVE_TO_DIR = {
    "MOVE_UP": "UP",
    "MOVE_DOWN": "DOWN",
    "MOVE_LEFT": "LEFT",
    "MOVE_RIGHT": "RIGHT",
}


def _line_has_steel(
    r1: int,
    c1: int,
    r2: int,
    c2: int,
    steel: set[tuple[int, int]],
) -> bool:
    """Kiem tra xem giua hai o cung hang/cot co bi tuong thep chan hay khong."""
    if r1 == r2:
        step = 1 if c2 > c1 else -1
        return any((r1, c) in steel for c in range(c1 + step, c2, step))
    if c1 == c2:
        step = 1 if r2 > r1 else -1
        return any((r, c1) in steel for r in range(r1 + step, r2, step))
    return True


def _next_step_bfs(
    rows: int,
    cols: int,
    start: tuple[int, int],
    target: tuple[int, int],
    blocked: set[tuple[int, int]],
) -> str | None:
    """Tim huong di ngan nhat ne tuong thep tu start den target."""
    if start == target:
        return None
    visited = {start}
    queue: deque[tuple[tuple[int, int], str]] = deque()
    for action, direction in _MOVE_TO_DIR.items():
        dr, dc = _DIRS[direction]
        nr, nc = start[0] + dr, start[1] + dc
        if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in blocked:
            if (nr, nc) == target:
                return action
            visited.add((nr, nc))
            queue.append(((nr, nc), action))

    while queue:
        (r, c), first_action = queue.popleft()
        for dr, dc in _DIRS.values():
            nr, nc = r + dr, c + dc
            pos = (nr, nc)
            if 0 <= nr < rows and 0 <= nc < cols and pos not in blocked and pos not in visited:
                if pos == target:
                    return first_action
                visited.add(pos)
                queue.append((pos, first_action))
    return None


def get_action(obs: dict) -> str:
    """Chon hanh dong dua tren tu dien quan sat doc lap (khong import engine)."""
    me = obs["current_player"]
    opp = 2 if me == 1 else 1
    my_tank = obs["tanks"][me]
    opp_tank = obs["tanks"][opp]
    opp_base = obs["bases"][opp]
    legal = obs["legal_actions"]

    r, c, facing = my_tank["row"], my_tank["col"], my_tank["facing"]
    br, bc = opp_base["row"], opp_base["col"]
    tr, tc = opp_tank["row"], opp_tank["col"]
    steel = {(w["row"], w["col"]) for w in obs["steel_walls"]}
    bricks = {(w["row"], w["col"]) for w in obs["brick_walls"]}

    # 1. Ban ngay neu dang ngam thang xe tang hoac can cu dich khong bi tuong thep chan
    if "FIRE" in legal:
        for target_r, target_c in ((tr, tc), (br, bc)):
            if r == target_r and not _line_has_steel(r, c, target_r, target_c, steel):
                if (target_c > c and facing == "RIGHT") or (target_c < c and facing == "LEFT"):
                    return "FIRE"
            if c == target_c and not _line_has_steel(r, c, target_r, target_c, steel):
                if (target_r > r and facing == "DOWN") or (target_r < r and facing == "UP"):
                    return "FIRE"

    # 2. Neu o truoc mat la tuong gach tren duong toi can cu dich thi ban pha tuong
    dr, dc = _DIRS[facing]
    if "FIRE" in legal and (r + dr, c + dc) in bricks:
        return "FIRE"

    # 3. Di chuyen vong qua tuong thep huong ve can cu dich bang BFS
    bfs_move = _next_step_bfs(obs["rows"], obs["cols"], (r, c), (br, bc), steel)
    if bfs_move in legal:
        return bfs_move

    if "FIRE" in legal and (r + dr, c + dc) not in steel:
        return "FIRE"
    return legal[0] if legal else "STAY"
