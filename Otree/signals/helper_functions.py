import itertools
import random
from enum import Enum
from math import floor


class Price(Enum):
    LOW = 0.5
    HIGH = 2


# --- template helpers -----------------------------------------------------------------------------------------------
def create_pairs(red_counts):
    pairs = list(itertools.product(get_income_profile(), red_counts))
    pairs = [(y, y1) for (y1, y) in pairs]
    return pairs

def create_schedule(player, treatment):
    if "num_obvious_blue" not in player.participant.vars:
        player.participant.vars["num_obvious_blue"] = 0
    if "num_obvious_red" not in player.participant.vars:
        player.participant.vars["num_obvious_red"] = 0

    # Generate two random obvious red counts. Check, if participant saw the same redcount twice and will see it a third
    # time this round. Set the last image to be the other one
    # NOTE: Will be shuffled
    obvious_red_counts = get_obvious_red_counts()
    if player.participant.vars["num_obvious_blue"] >= 2 and obvious_red_counts[0] == 120:
        obvious_red_counts[1] = 280
    if player.participant.vars["num_obvious_red"] >= 2 and obvious_red_counts[0] == 280:
        obvious_red_counts[1] = 120

    player.participant.vars["num_obvious_blue"] += obvious_red_counts.count(120)
    player.participant.vars["num_obvious_red"] += obvious_red_counts.count(280)

    # Pair all red counts with the income profiles
    red_counts = get_red_counts() + obvious_red_counts
    pairs = create_pairs(red_counts)
    image_files_master = synthesize_filenames(red_counts, treatment)

    schedule = pairs[:]
    images = image_files_master[:]

    #
    combined = list(zip(schedule, images))
    random.shuffle(combined)

    schedule, images = zip(*combined)
    schedule = list(schedule)
    images = list(images)

    player.participant.vars[f"{treatment}_schedule"] = schedule
    player.participant.vars[f"{treatment}_images"] = images


def create_session(subsession, C, treatment):
    # For each participant, randomize order and assign per-round parameters
    for p in subsession.get_players():
        # Shuffle pairs in the first round randomly, different for every player
        if subsession.round_number == 1:
            create_schedule(p, treatment)

        r, y1 = p.participant.vars[f"{treatment}_schedule"][subsession.round_number - 1]
        image_file = p.participant.vars[f"{treatment}_images"][subsession.round_number - 1]

        p.y1 = y1
        p.red_count = int(r)
        p.h_true = p.red_count / 400.0
        p.pi = 2 if p.red_count > 200 else 0.5
        p.y2 = 15 if y1 == 5 else 5
        p.p2 = p.pi * C.P1
        p.image_file = image_file
        p.c1_max = calc_c1_max(p)


def build_vars_for_template_choice(player, C):
    return {
            "y1": player.y1,
            "y2": player.y2,
            "p1": C.P1,
            "R": C.R,
            "c1_max": player.c1_max,
            "table_rows": build_payoff_table(
                player.y1, player.y2, C.P1, C.R, player.c1_max
            ),
        }


def build_payoff_table(y1, y2, p1, R, c1_max):
    """
    Build a payoff table like Table 1 in the spec:
    rows for c1 = 1..20, columns for π = 0.5 and 1.5.
    Returns a list of dicts {c1, u05, u15, infeasible05, infeasible15}.
    """
    rows = []
    for k in range(1, floor(c1_max) + 1):
        c = float(k)

        # π = 0.5
        pi05 = 0.5
        p2_05 = pi05 * p1
        # s05 = y1 - p1 * c
        # c2_05 = (y2 + R * s05) / p2_05
        c2_05 = calc_c2(y1, y2, p1, p2_05, c, R)
        u05 = round(c * c2_05, 2) if c2_05 >= 1 else None

        # π = 2
        pi2 = 2
        p2_2 = pi2 * p1
        # s2 = y1 - p1 * c
        # c2_2 = (y2 + R * s2) / p2_2
        c2_2= calc_c2(y1, y2, p1, p2_2, c, R)
        u2 = round(c * c2_2, 2) if c2_2 >= 1 else None

        rows.append(
            dict(
                c1=k,
                u05=u05,
                infeasible05=(c2_05 < 1),
                u15=u2,
                infeasible15=(c2_2 < 1),
            )
        )
    return rows


def synthesize_filenames(red_count, treatment):
    def generate_block(x):
        seen = {120: False, 280: False}
        names = []

        for r in red_count:
            if r in seen:
                suffix = "a" if not seen[r] else "b"
                seen[r] = True
                names.append(f"dots_{treatment}_{r}_{x}_{suffix}.png")
            else:
                names.append(f"dots_{treatment}_{r}_{x}.png")

        return names

    block1 = generate_block("x1")
    block2 = generate_block("x2")

    return block1 + block2



# helper_functions.py
def record_main_round(player, app_label: str):
    """
    Push the current round's key data into participant.vars['main_rounds'].
    Call this at the end of the treatment round (e.g., last page's before_next_page).
    """
    current_round_entry = dict(
        treatment=app_label,
        round=player.round_number,
        # decision/consumption side
        c1=getattr(player, "c1", None),
        c2=getattr(player, "c2", None),
        u=getattr(player, "u", None),
        # belief side
        h_true=getattr(player, "h_true", None),  # r/400
        h_hat=getattr(player, "h_hat", None),  # normalized belief ∈[0,1]
        belief_input_raw=getattr(player, "belief_input_raw", None),
        # metadata that may help
        y1=getattr(player, "y1", None),
        pi=getattr(player, "pi", None),
        red_count=getattr(player, "red_count", None),
    )
    arr = player.participant.vars.setdefault("main_rounds", [])
    arr.append(current_round_entry)


# ---- Calculation helpers --------------------------------------------------------------------------------------------
def run_binary_lottery(chosen, prize: float = 100):
    """
    Binary scoring lottery.
    Returns the prize if the player wins, else 0.
    """
    h_hat = float(chosen.get("h_hat") or 0.0)
    h_true = 1 if float(chosen.get("h_true") or 0.0) > 0.5 else 0

    threshold = max(0.0, 1.0 - abs(h_hat - h_true)**2)
    u = random.random()

    if u <= threshold:
        return prize, threshold
    else:
        return 0, threshold


# ---- helpers per spec ----
def calc_c1_max(p) -> float:
    return floor(p.y1 + p.y2 / 2 - 0.5) # TODO: Price HIGH


def c2_given(p, C) -> float:
    return calc_c2(p.y1, p.y2, C.P1, p.p2, p.c1, C.R)

def calc_c2(y1, y2, p1, p2, c1, R):
    s = y1 - p1*c1
    return y2 + (R*s)/p2

def u_given(p) -> float:
    return float(p.c1) * p.c2


# Constants ------------------------------------------------------------------------------------------------------------
def get_red_counts():
    return [185, 195, 205, 215]

def get_obvious_red_counts():
    obvious_red_counts = [120, 120, 280, 280]
    random.shuffle(obvious_red_counts)
    return obvious_red_counts[:2]

def get_income_profile():
    return [5, 15]

def get_round_count():
    return 1#len(get_red_counts() * len(get_income_profile()))

if __name__ == '__main__':
    print(synthesize_filenames(get_red_counts() + get_obvious_red_counts(), "T0"))