from otree.api import *
import itertools, random
from helper_functions import *

doc = """
Baseline treatment (T0): Choice -> Signal (4 countdown + 6s show) -> Belief.
No feedback. Priors 50/50.
"""

class C(BaseConstants):
    NAME_IN_URL = 't1'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    # Defaults from the spec
    Y1 = 10.0
    P1 = 1.0
    I = 0.0             # net interest
    R = 1.0 + I         # gross R

    # Signals: 10 compositions. Each used twice (once with x=0.5 and once with x=1.5) → total 20 images.
    RED_COUNTS = [120, 185, 190, 195, 199, 201, 205, 210, 215, 280]

    # Two income profiles per treatment
    XS = [0.5, 1.5]

    IMAGE_FILES = None # Can be specified here, otherwise filenames like dots_{Treatment}_{NumRedDots}_{a/b} is expected

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    # Round parameters
    income_factor = models.FloatField()          # 0.5 or 1.5
    red_count = models.IntegerField(default=0)        # red count
    h_true = models.FloatField()     # r/400
    pi = models.FloatField()         # inflation factor: 1.5 if r>200 else 0.5
    p2 = models.FloatField()         # period-2 price (= pi * p1 by default)
    image_file = models.StringField()
    r = models.FloatField()
    # Decision
    c1_max = models.FloatField()
    c1 = models.FloatField()

    # Belief entry (raw and normalized)
    belief_input_raw = models.FloatField()  # 0-400 (B1)
    h_hat = models.FloatField()             # normalized to [0,1]

    # Implied outcomes
    c2 = models.FloatField()
    u = models.FloatField()

    # ---- helpers per spec ----
    def calc_c1_max(self) -> float:
        # c1_max = (π x y1 + R*y1 - p2) / (R*p1)
        return (self.pi * self.income_factor * C.Y1 + C.R * C.Y1 - self.p2) / (C.R * C.P1)

    def c2_given(self, c1: float) -> float:
        # s = y1 - p1*c1; c2 = (π x y1 + R*s)/p2 ; with p2 = π * p1 (default)
        s = C.Y1 - C.P1 * float(c1)
        return (self.pi * self.income_factor * C.Y1 + C.R * s) / self.p2

    def u_given(self, c1: float) -> float:
        return float(c1) * self.c2_given(c1)

# -- oTree lifecycle hooks (function-based API) --

def creating_session(subsession: Subsession):
    """
    Build 20 rounds per participant:
      - Take the 10 red counts.
      - Duplicate once so each red count is paired with x=0.5 and x=1.5.
      - Shuffle the 20 (r,x) pairs within the treatment.
    Assign image file names. If C.IMAGE_FILES is not provided, synthesize names.
    Belief mode can be configured in SESSION_CONFIGS as 'belief_mode': 'B1' or 'B2' (default B1).
    """
    # Build 20 pairs (r,x): each r appears once with x=0.5 and once with x=1.5
    #pairs = [(r, 0.5) for r in C.RED_COUNTS] + [(r, 1.5) for r in C.RED_COUNTS]
    pairs = list(itertools.product(C.RED_COUNTS, [0.5, 1.5]))
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
            p.participant.vars['t1_schedule'] = schedule
            p.participant.vars['t1_images'] = images

        r, x = p.participant.vars['t1_schedule'][subsession.round_number - 1]
        image_file = p.participant.vars['t1_images'][subsession.round_number - 1]

        p.income_factor = float(x)
        p.r = int(r)
        p.h_true = p.r / 400.0
        p.pi = 1.5 if p.r > 200 else 0.5
        p.p2 = p.pi * C.P1
        p.image_file = image_file
        p.c1_max = p.calc_c1_max()

# ------------- Pages -------------
class Explanation(Page):
    def is_displayed(player):
        return player.round_number == 1


class Choice(Page):
    form_model = 'player'
    form_fields = ['c1']

    @staticmethod
    def vars_for_template(player: Player):
        # Build a payoff table like the document’s panel: c1 = 1..20; columns for π=0.5 and π=1.5
        return dict(
            y1=C.Y1,
            p1=C.P1,
            R = C.R,
            x=player.income_factor,
            # Note: in baseline the subject chooses c1 BEFORE seeing the signal; prior is 50/50
            y2_pi05=0.5 * player.income_factor * C.Y1,
            y2_pi15=1.5 * player.income_factor * C.Y1,
            c1_max=player.c1_max,
            table_rows=build_payoff_table(player.income_factor, C.P1, C.Y1, C.R),
        )

    @staticmethod
    def error_message(player: Player, values):
        c1 = values.get('c1')
        if c1 is None:
            return 'Please choose c1.'
        if not (1 <= c1 <= player.c1_max):
            return f'c1 must be between 1 and {player.c1_max:.2f}.'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        #Normalize belief for storing
        player.h_hat = float(player.belief_input_raw) / 400.0

        # Compute implied outcomes now (hidden from subject; used in payoff stage)
        player.c2 = player.c2_given(player.c1)
        player.u = player.u_given(player.c1)

        record_main_round(player, app_label='t1')


class Signal(Page):
    # No form: show countdown, then show image 6s, auto-hide, then enable Next.
    timeout_seconds = 10  # 10s countdown + 6s show (user can proceed when enabled)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            image_file=player.image_file,
            countdown_seconds=4,
            show_seconds=6,
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


class SyncGate(WaitPage):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS



page_sequence = [Signal, Belief, Choice, SyncGate]
