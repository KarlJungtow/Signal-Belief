from otree.api import *
import itertools
import random
from helper_functions import *

doc = """
Baseline treatment (T0): Choice -> Signal (4 countdown + 6s show) -> Belief.
No feedback. Priors 50/50.
"""


class C(BaseConstants):
    RED_COUNTS = get_red_counts()
    XS = get_income_profile()

    NAME_IN_URL = 't4'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1#len(RED_COUNTS) * len(XS)

    # Defaults from the spec
    Y1 = 10.0
    P1 = 1.0
    I = 0.0  # net interest
    R = 1.0 + I  # gross R

    SIGNAL_SHOW_SECONDS = 6
    # Can be specified here, otherwise filenames like dots_{Treatment}_{NumRedDots}_{a/b} are expected
    IMAGE_FILES = None


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Round parameters
    current_role = models.StringField()
    income_factor = models.FloatField()  # 0.5 or 1.5
    red_count = models.IntegerField(default=0)  # red count
    h_true = models.FloatField()  # r/400
    pi = models.FloatField()  # inflation factor: 1.5 if r > 200 else 0.5
    p2 = models.FloatField()  # period-2 price (= pi * p1 by default)
    image_file = models.StringField()
    r = models.FloatField()
    c1_max = models.FloatField()

    # Decision
    c1 = models.FloatField()

    # Belief entry (raw and normalized)
    belief_input_raw = models.FloatField()  # 0–400 (B1)
    h_hat = models.FloatField()  # normalized to [0,1]

    # Implied outcomes
    c2 = models.FloatField()
    u = models.FloatField()

    # ---- helpers per spec ----


# -- oTree lifecycle hooks (function-based API) --
def creating_session(subsession: Subsession):
    """
    Build 20 rounds per participant:
      - Take the 10 red counts.
      - Duplicate once so each red count is paired with x=0.5 and x=1.5.
      - Shuffle the 20 (r, x) pairs within the treatment.
    Assign image file names. If C.IMAGE_FILES is not provided, synthesize names.
    Belief mode can be configured in SESSION_CONFIGS as 'belief_mode': 'B1' or 'B2' (default B1).
    """
    # Build 20 pairs (r, x): each r appears once with x=0.5 and once with x=1.5
    pairs = list(itertools.product(C.RED_COUNTS, [0.5, 1.5]))
    roles_master = ['borrower'] * 10 + ['saver'] * 10
    # Precompute a 20-item image list if explicit files not provided
    image_files_master = synthesize_filenames(C.RED_COUNTS, C.IMAGE_FILES)

    # For each participant, randomize order and assign per-round parameters
    for p in subsession.get_players():
        if subsession.round_number == 1:
            schedule = pairs[:]
            random.shuffle(schedule)

            images = image_files_master[:]
            random.shuffle(images)

            roles = roles_master[:]
            random.shuffle(roles)

            p.participant.vars['t4_schedule'] = schedule
            p.participant.vars['t4_images'] = images
            p.participant.vars['t4_roles'] = roles

        r, x = p.participant.vars['t4_schedule'][subsession.round_number - 1]
        image_file = p.participant.vars['t4_images'][subsession.round_number - 1]
        current_role = p.participant.vars['t4_roles'][subsession.round_number - 1]

        p.income_factor = float(x)
        p.r = int(r)
        p.h_true = p.r / 400.0
        p.pi = 1.5 if p.r > 200 else 0.5
        p.p2 = p.pi * C.P1
        p.image_file = image_file
        p.current_role = current_role
        p.c1_max = calc_c1_max(p, C)

        if p.current_role == 'borrower':
            p.c1 = C.Y1 - 3
        else:
            p.c1 = C.Y1 + 3


# ------------- Pages -------------
class Explanation(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class IncomeInfo(Page):
    form_model = 'player'

    @staticmethod
    def vars_for_template(player: Player):
        # Build a payoff table like the document’s panel: c1 = 1..20; columns for π=0.5 and π=1.5
        return dict(
            y1=C.Y1,
            p1=C.P1,
            R=C.R,
            x=player.income_factor,
            y2_pi1=player.income_factor * C.Y1,
            c1=player.c1,
            table_rows=build_payoff_table(
                player.income_factor, C.P1, C.Y1, C.R, player.c1_max
            ),
        )


class Signal(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            image_file=player.image_file,
            show_seconds=C.SIGNAL_SHOW_SECONDS,
        )


class Belief(Page):
    form_model = 'player'
    form_fields = ['belief_input_raw']

    @staticmethod
    def error_message(player: Player, values):
        v = values.get('belief_input_raw')
        if v is None:
            return 'Please enter your belief.'
        if not (0 <= v <= 400):
            return 'Enter how many red dots you saw (0–400).'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Normalize belief for storing
        player.h_hat = float(player.belief_input_raw) / 400.0

        # Compute implied outcomes now (hidden from subject; used in payoff stage)
        player.c2 = c2_given(player, C)
        player.u = u_given(player)
        record_main_round(player, app_label='t4')


class SyncGate(WaitPage):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [
    Explanation,
    SyncGate,
    IncomeInfo,
    Signal,
    Belief,
]
