from otree.api import *
import time
from helper_functions import *

class C(BaseConstants):
    NAME_IN_URL = "t1"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = get_round_count()

    # Defaults from the spec
    P1 = 1.0
    I = 0.0  # net interest
    R = 1.0 + I  # gross R

    SIGNAL_SHOW_SECONDS = 6



class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Round parameters
    y1 = models.FloatField()
    y2 = models.FloatField()
    red_count = models.IntegerField(default=0)  # red count
    h_true = models.FloatField()  # r/400
    pi = models.FloatField()  # inflation factor: 1.5 if r > 200 else 0.5
    p2 = models.FloatField()  # period-2 price (= pi * p1 by default)
    image_file = models.StringField()
    r = models.FloatField() #TODO Check delete

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
    belief_time_offset = models.FloatField()
    belief_time_spent = models.FloatField()

    choice_time_offset = models.FloatField()
    choice_time_spent = models.FloatField()

# -- oTree lifecycle hooks (function-based API) --
def creating_session(subsession: Subsession):
    """
    Build 20 rounds per participant:
      - Take the 10 red counts.
      - Duplicate once so each red count is paired with x=0.5 and x=1.5.
      - Shuffle the 20 (r, x) pairs within the treatment.
    Assign image file names. If C.IMAGE_FILES is not provided, synthesize names.
    Belief mode can be configured in SESSION_CONFIGS as 'belief_mode': 'B1' or 'B2'
    (default B1).
    """
    create_session(subsession, C, "t1")


# ------------- Pages -------------
class Explanation(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class SyncGate(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Choice(Page):
    form_model = "player"
    form_fields = ["c1"]

    @staticmethod
    def vars_for_template(player: Player):
        # Build a payoff table like the document’s panel: c1 = 1..20;
        # columns for π=0.5 and π=1.5
        player.choice_time_offset = time.time()
        return build_vars_for_template_choice(player, C)

    @staticmethod
    def error_message(player: Player, values):
        c1 = values.get("c1")
        if c1 is None:
            return "Please choose c1."
        if not (1 <= c1 <= player.c1_max):
            return f"c1 must be between 1 and {player.c1_max:.2f}."

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.choice_time_spent = round(time.time() - player.choice_time_offset, 2)
        # Normalize belief for storing
        player.h_hat = float(player.belief_input_raw) / 100.0

        # Compute implied outcomes now (hidden from subject; used in payoff stage)
        player.c2 = c2_given(player, C)
        player.u = u_given(player)

        record_main_round(player, app_label="t1")


class Signal(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            image_file=player.image_file,
            show_seconds= C.SIGNAL_SHOW_SECONDS,
        )


class Belief(Page):
    form_model = "player"
    form_fields = ["belief_input_raw"]

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

    def before_next_page(player: Player, timeout_happened):
        player.belief_time_spent = round(time.time() - player.belief_time_offset, 2)


page_sequence = [
    Explanation,
    SyncGate,
    Signal,
    Belief,
    Choice,
]
