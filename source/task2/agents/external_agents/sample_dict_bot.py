"""Example external student group bot using Protocol 2: pure dict get_action(obs_dict).

Other student groups do not need to import internal GameState classes; they can
simply inspect ``obs_dict`` and return one of the 6 valid action strings.
"""

from __future__ import annotations

BOT_NAME = "Bot ngoài: Săn căn cứ (Dict)"


def get_action(obs: dict) -> str:
    me = obs["current_player"]
    opp = 2 if me == 1 else 1
    my_tank = obs["tanks"][me]
    opp_base = obs["bases"][opp]
    legal = obs["legal_actions"]

    r, c, facing = my_tank["row"], my_tank["col"], my_tank["facing"]
    br, bc = opp_base["row"], opp_base["col"]

    # Fire immediately when aligned with enemy base
    if "FIRE" in legal:
        if r == br and ((bc > c and facing == "RIGHT") or (bc < c and facing == "LEFT")):
            return "FIRE"
        if c == bc and ((br > r and facing == "DOWN") or (br < r and facing == "UP")):
            return "FIRE"

    # Otherwise close Manhattan distance toward enemy base
    preferred = []
    if br < r:
        preferred.append("MOVE_UP")
    elif br > r:
        preferred.append("MOVE_DOWN")
    if bc < c:
        preferred.append("MOVE_LEFT")
    elif bc > c:
        preferred.append("MOVE_RIGHT")

    for act in preferred:
        if act in legal:
            return act
    if "FIRE" in legal:
        return "FIRE"
    return legal[0] if legal else "STAY"
