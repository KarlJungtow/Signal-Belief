from otree.api import *
import time
from helper_functions import *

class C(BaseConstants):
    RED_COUNTS = get_red_counts()
    XS = get_income_profile()

    NAME_IN_URL = "t0_baseline"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1#len(RED_COUNTS) * len(XS)

    # Defaults from the spec
    Y1 = 10.0
    P1 = 1.0
    I = 0.0  # net interest
    R = 1.0 + I  # gross R

    SIGNAL_SHOW_SECONDS = 6

    # Can be specified here; otherwise filenames like
    # dots_{Treatment}_{NumRedDots}_{x=05/x=15} are expected
    IMAGE_FILES = None


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Round parameters
    income_factor = models.FloatField()  # x, 0.5 or 1.5
    red_count = models.IntegerField(default=0)  # real number of red dots
    h_true = models.FloatField()  # red_count / 400
    pi = models.FloatField()  # inflation factor: 1.5 if r > 200 else 0.5
    p2 = models.FloatField()  # period-2 price (= pi * p1 by default)
    image_file = models.StringField()

    # Decision
    c1_max = models.FloatField()
    c1 = models.FloatField()

    # Belief entry (raw and normalized)
    belief_input_raw = models.FloatField()  # 0–400 (B1)
    h_hat = models.FloatField()  # normalized to [0, 1]

    # Implied outcomes
    c2 = models.FloatField()
    u = models.FloatField()

    # Time tracking
    choice_time_offset = models.FloatField()
    choice_time_spent = models.FloatField()

    belief_time_offset = models.FloatField()
    belief_time_spent = models.FloatField()


# -- oTree lifecycle hooks (function-based API) --
def creating_session(subsession: Subsession):
    """
    Build 20 (r, x) pairs per participant:
      - Take the 10 red counts.
      - Pair each with x in {0.5, 1.5}.
      - Shuffle the 20 (r, x) pairs within the treatment.
    Assign image file names. If C.IMAGE_FILES is not provided, synthesize names.
    Belief mode can be configured in SESSION_CONFIGS as 'belief_mode': 'B1' or 'B2'
    (default B1).
    """
    create_session(subsession, C, "t0")


# ------------- Pages -------------
class Explanation(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

# Just for player coordination to not progress too fast
class SyncGate(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class Choice(Page):
    form_model = "player"
    form_fields = ["c1"]

    @staticmethod
    def vars_for_template(player: Player):
        player.choice_time_offset = time.time()
        return build_vars_for_template_choice(player, C)

    @staticmethod
    def error_message(player: Player, values):
        c1 = values.get("c1")
        if c1 is None:
            return "Please choose c1."
        if not (1 <= c1 <= player.c1_max):
            return f"c1 must be between 1 and {player.c1_max:.2f}."

    # Calculate time spent on page. NOTE: Reloading will reset offset timer
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.choice_time_spent = round(time.time() - player.choice_time_offset, 2)


class Signal(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            image_file=player.image_file,
            show_seconds=C.SIGNAL_SHOW_SECONDS,
            reds=player.red_count,
        )


class Belief(Page):
    form_model = "player"
    form_fields = ["belief_input_raw"]

    # Only hook to call time()
    @staticmethod
    def vars_for_template(player: Player):
        player.belief_time_offset = time.time()
        return {}

    @staticmethod
    def error_message(player: Player, values):
        v = values.get("belief_input_raw")
        if v is None:
            return "Please enter your belief."
        if not (0 <= v <= 400):
            return "Enter how many red dots you saw (0–400)."

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.belief_time_spent = round(time.time() - player.belief_time_offset, 2)

        # Normalize belief for storing
        player.h_hat = float(player.belief_input_raw) / 400.0

        # Compute implied outcomes now (hidden from subject; used in payoff stage)
        player.c2 = c2_given(player, C)
        player.u = u_given(player)
        record_main_round(player, app_label="t0_baseline")



page_sequence = [
    Explanation,
    SyncGate,
    Choice,
    Signal,
    Belief,
]
