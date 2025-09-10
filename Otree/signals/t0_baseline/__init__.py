from otree.api import *
import time

from helper_functions import *

doc = """
Baseline treatment (T0): Choice -> Signal (4 countdown + 6s show) -> Belief.
No feedback. Priors 50/50.
"""


class C(BaseConstants):
    NAME_IN_URL = "t0_baseline"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    # Defaults from the spec
    Y1 = 10.0
    P1 = 1.0
    I = 0.0  # net interest
    R = 1.0 + I  # gross R

    # Signals: 10 compositions. Each used twice (once with x=0.5 and once with x=1.5) → total 20 images.
    RED_COUNTS = [120, 185, 190, 195, 199, 201, 205, 210, 215, 280]

    # Two income profiles per treatment
    XS = [0.5, 1.5]

    # UI timing (used by Signal page/template)
    COUNTDOWN_SECONDS = 0
    SIGNAL_SHOW_SECONDS = 4

    # Can be specified here; otherwise filenames like dots_{Treatment}_{NumRedDots}_{a/b} are expected
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

    #Time Tracking
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
    Belief mode can be configured in SESSION_CONFIGS as 'belief_mode': 'B1' or 'B2' (default B1).
    """

    create_session(subsession, C, "t0")


# ------------- Pages -------------
class Explanation(Page):
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

    # Calculate Time spent on page. NOTE: Reloading will reset offset timer
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.choice_time_spent = round(time.time() - player.choice_time_offset, 2)

class Signal(Page):
    # Show countdown, then show image for fixed time; auto-hide; then enable Next.
    timeout_seconds = C.COUNTDOWN_SECONDS + C.SIGNAL_SHOW_SECONDS

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            image_file=player.image_file,
            countdown_seconds=C.COUNTDOWN_SECONDS,
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


#Just for player Coordination to not progress too fast
class SyncGate(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [Explanation, Choice, Signal, Belief, SyncGate]