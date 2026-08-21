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
    # Six non-extreme signals appear once under each income profile.
    regular_red_counts = get_red_counts()

    # Four extreme-signal realizations: two for each income profile.
    # The balancing rule guarantees at least one 120 and one 280
    # across the four extreme slots within the treatment.
    obvious_red_counts = get_obvious_red_counts()

    profiles = get_income_profile()

    # x1 corresponds to the first profile (y1 = 5),
    # x2 to the second profile (y1 = 15).
    x1_counts = regular_red_counts + obvious_red_counts[:2]
    x2_counts = regular_red_counts + obvious_red_counts[2:]

    schedule = (
        [(r, profiles[0]) for r in x1_counts]
        + [(r, profiles[1]) for r in x2_counts]
    )

    images = synthesize_filenames(
        x1_counts,
        x2_counts,
        treatment,
    )

    combined = list(zip(schedule, images))
    random.shuffle(combined)

    schedule, images = zip(*combined)

    player.participant.vars[f"{treatment}_schedule"] = list(schedule)
    player.participant.vars[f"{treatment}_images"] = list(images)


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
        "belief": player.belief_input_raw,
        "treatment": len(player.participant.treatment),
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

        pi2 = 2
        p2_2 = pi2 * p1
        c2_2 = calc_c2(y1, y2, p1, p2_2, c, R)
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


def synthesize_filenames(red_counts_x1, red_counts_x2, treatment):
    def generate_block(red_counts, x):
        seen = {120: 0, 280: 0}
        names = []

        for r in red_counts:
            if r in seen:
                seen[r] += 1
                suffix = "a" if seen[r] == 1 else "b"
                names.append(
                    f"dots_{treatment}_{r}_{x}_{suffix}.png"
                )
            else:
                names.append(
                    f"dots_{treatment}_{r}_{x}.png"
                )

        return names

    return (
        generate_block(red_counts_x1, "x1")
        + generate_block(red_counts_x2, "x2")
    )


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
def run_binary_lottery(chosen, prize: float = 20):
    """
    Binary scoring lottery.
    Returns the prize if the player wins, else 0.
    """
    h_hat = float(chosen.get("h_hat") or 0.0)
    h_true = 1 if float(chosen.get("h_true") or 0.0) > 0.5 else 0

    threshold = max(0.0, 1.0 - abs(h_hat - h_true) ** 2)
    u = random.random()

    if u <= threshold:
        return prize, round(threshold, 2)
    else:
        return 0, round(threshold, 2)


def run_lottery_training(h_hat, prize: float = 2):
    """
    Binary scoring lottery.
    Returns the prize if the player wins, else 0.
    """
    h_hat = float(h_hat or 0.0)
    h_true = 1 #TODO Dynamisch machen

    threshold = max(0.0, 1.0 - abs(h_hat - h_true) ** 2)
    u = random.random()

    if u <= threshold:
        return prize, round(threshold, 2)
    else:
        return 0, round(threshold, 2)



# ---- helpers per spec ----
def calc_c1_max(p) -> float:
    return floor(p.y1 + p.y2 / 2 - 0.5)  # TODO: Price HIGH


def c2_given(p, C) -> float:
    return calc_c2(p.y1, p.y2, C.P1, p.p2, p.c1, C.R)


def calc_c2(y1, y2, p1, p2, c1, R):
    s = y1 - p1 * c1
    return y2 + (R * s) / p2


def u_given(p) -> float:
    return float(p.c1) * p.c2


# Constants ------------------------------------------------------------------------------------------------------------
def get_red_counts():
    return [190, 195, 199, 201, 205, 210]


def get_obvious_red_counts():
    # Draw the first three extreme signals independently with replacement.
    draws = [random.choice([120, 280]) for _ in range(3)]

    # If the first three are identical, force the fourth to be the opposite
    # extreme; otherwise draw the fourth independently.
    if draws[0] == draws[1] == draws[2]:
        draws.append(280 if draws[0] == 120 else 120)
    else:
        draws.append(random.choice([120, 280]))

    return draws


def get_income_profile():
    return [5, 15]


def get_round_count():
    # Six non-extreme + two extreme signals per income profile.
    return (len(get_red_counts()) + 2) * len(get_income_profile())

def smart_append(array, var):
    if not var in array:
        array.append(var)
def sround(var):
    return int(var) if round(var) == var else var
if __name__ == '__main__':
    print(run_lottery_training(0.5)[0])
