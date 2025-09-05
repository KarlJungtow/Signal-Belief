import random
import itertools


#---template helpers----------------------------------------------------------------------------------------------------
def create_session(subsession, C, treatment):
    # Build 20 pairs (r, x): each r appears once with x=0.5 and once with x=1.5
    pairs = list(itertools.product(C.RED_COUNTS, C.XS))

    # Precompute a 20-item image list if explicit files not provided
    image_files_master = synthesize_filenames(C.RED_COUNTS, C.IMAGE_FILES)

    # For each participant, randomize order and assign per-round parameters
    for p in subsession.get_players():
        if subsession.round_number == 1:
            schedule = pairs[:]
            random.shuffle(schedule)

            # shuffle image files for each player (distinct images within treatment)
            images = image_files_master[:]
            random.shuffle(images)

            p.participant.vars[f"{treatment}_schedule"] = schedule
            p.participant.vars[f"{treatment}_images"] = images

        r, x = p.participant.vars[f"{treatment}_schedule"][subsession.round_number - 1]
        image_file = p.participant.vars[f"{treatment}_images"][subsession.round_number - 1]

        p.income_factor = float(x)
        p.red_count = int(r)
        p.h_true = p.red_count / 400.0
        p.pi = 1.5 if p.red_count > 200 else 0.5
        p.p2 = p.pi * C.P1
        p.image_file = image_file
        p.c1_max = calc_c1_max(p, C)


def build_vars_for_template_choice(player, C):
    return {
        "y1": C.Y1,
        "p1": C.P1,
        "R": C.R,
        "x": player.income_factor,
        "y2_pi05": 0.5 * player.income_factor * C.Y1,
        "y2_pi15": 1.5 * player.income_factor * C.Y1,
        "c1_max": player.c1_max,
        "table_rows": build_payoff_table(player.income_factor, C.P1, C.Y1, C.R),
    }


def build_payoff_table(x_val: float, p1, y1, R):
    """
    Build a payoff table like Table 1 in the spec:
    rows for c1 = 1..20, columns for π = 0.5 and 1.5.
    Returns a list of dicts {c1, u05, u15, infeasible05, infeasible15}.
    """
    rows = []
    for k in range(1, 21):
        c = float(k)
        # π = 0.5
        pi05 = 0.5
        p2_05 = pi05 * p1
        s05 = y1 - p1 * c
        c2_05 = (pi05 * x_val * y1 + R * s05) / p2_05
        u05 = c * c2_05 if c2_05 >= 1 else None
        # π = 1.5
        pi15 = 1.5
        p2_15 = pi15 * p1
        s15 = y1 - p1 * c
        c2_15 = (pi15 * x_val * y1 + R * s15) / p2_15
        u15 = c * c2_15 if c2_15 >= 1 else None
        rows.append(dict(
            c1=k,
            u05=u05, infeasible05=(c2_05 < 1),
            u15=u15, infeasible15=(c2_15 < 1),
        ))
    return rows


def synthesize_filenames(red_count, file_names=None):
    if file_names is None:
        # two variants per red count
        synthesized = []
        for r in red_count:
            synthesized.append(f"dots_T0_{r}_a.png")
        for r in red_count:
            synthesized.append(f"dots_T0_{r}_b.png")
        return synthesized
    else:
        if len(file_names) != 20:
            return synthesize_filenames(red_count)
        else:
            return file_names


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
        c1=getattr(player, 'c1', None),
        c2=getattr(player, 'c2', None),
        u=getattr(player, 'u', None),
        # belief side
        h_true=getattr(player, 'h_true', None),      # r/400
        h_hat=getattr(player, 'h_hat', None),        # normalized belief ∈[0,1]
        # metadata that may help
        x=getattr(player, 'income_factor', None),
        pi=getattr(player, 'pi', None),
        red_count=getattr(player, 'red_count', getattr(player, 'r', None)),
    )
    arr = player.participant.vars.setdefault('main_rounds', [])
    arr.append(current_round_entry)

# ----Calculation helpers-----------------------------------------------------------------------------------------------
def run_binary_lottery(chosen, prize: float = 100):
    """
    Binary scoring lottery.
    Returns the prize if the player wins, else 0.
    """

    h_hat = float(chosen.get('h_hat') or 0.0)
    h_true = float(chosen.get('h_true') or 0.0)


    threshold = max(0.0, 1.0 - (h_hat - h_true) ** 2)
    U = random.random()

    if U <= threshold:
        return prize, threshold
    else:
        return 0, threshold

# ---- helpers per spec ----
def calc_c1_max(p, C) -> float:
    # c1_max = (π*x*y1 + R*y1 - p2) / (R*p1)
    return (p.pi * p.income_factor * C.Y1 + C.R * C.Y1 - p.p2) / (C.R * C.P1)

def c2_given(p, C) -> float:
    s = C.Y1 - C.P1 * float(p.c1)
    return (p.pi * p.income_factor * C.Y1 + C.R * s) / p.p2

def u_given(p) -> float:
    return float(p.c1) * p.c2