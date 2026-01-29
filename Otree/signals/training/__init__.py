from otree.api import *
import itertools
import random
from helper_functions import *


class C(BaseConstants):
    NAME_IN_URL = 'training'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 2

    P1 = 1.0
    I = 0.0
    R = 1.0 + I

    PIS = [2]
    INCOME = [5, 15]
    SIGNAL_SHOW_SECONDS = 1


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    combos = list(itertools.product(C.PIS, C.INCOME))
    for p in subsession.get_players():
        if subsession.round_number == 1:
            schedule = combos[:]
            random.shuffle(schedule)
            p.participant.vars['training_schedule'] = schedule
            p.image_file = "dots_A_280_x1_a.png"
        else:
            p.image_file = "dots_A_215_x1.png"
        pi, y1 = p.participant.vars['training_schedule'][
            subsession.round_number - 1
        ]
        p.participant.vars['treatment'] = []
        p.pi = pi
        p.y1 = y1
        p.y2 = 15 if y1 == 5 else 5
        p.p2 = pi * C.P1
        p.c1_max = calc_c1_max(p)

class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pi = models.FloatField()
    y1 = models.FloatField()
    y2 = models.FloatField()
    p2 = models.FloatField()
    c1_max = models.FloatField()
    belief_input_raw = models.FloatField(default=50)
    image_file = models.StringField()
    # Decision
    c1 = models.FloatField()

    # Outcomes
    c2 = models.FloatField()
    u = models.FloatField()


class Choice(Page):
    form_model = 'player'
    form_fields = ['c1']

    @staticmethod
    def vars_for_template(player: Player):
        return build_vars_for_template_choice(player, C)

    @staticmethod
    def error_message(player: Player, values):
        c1 = values['c1']
        if not (1 <= c1 <= player.c1_max):
            return f'c1 must be between 1 and {player.c1_max:.2f}.'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.c2 = c2_given(player, C)
        player.u = u_given(player)


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
    def error_message(player: Player, values):
        v = values.get("belief_input_raw")
        if v is None:
            return "Please enter your belief."
        if not (0 <= v <= 100):
            return "Enter the likelihood (0–100)."



class Result(Page):
    form_model = 'player'

    @staticmethod
    def vars_for_template(player: Player):

        def fmt2(x):
            # "up to 2 decimals" (no trailing zeros)
            s = f"{x:.2f}"
            s = s.rstrip('0').rstrip('.')
            return s

        belief = player.belief_input_raw / 100
        prize, prob = run_lottery_training(belief)   # don't call twice
        chance = prob * 100
        threshold = sround(chance)

        c2_low_val = calc_c2(player.y1, player.y2, C.P1, 0.5, player.c1, C.R)
        u_low_val = player.c1 * c2_low_val

        return {
            "c1": fmt2(player.c1),          # or f"{player.c1:.1f}" if you prefer
            "c2": fmt2(player.c2),
            "c2_low": fmt2(c2_low_val),
            "u_low": fmt2(u_low_val),
            "u": fmt2(player.u),
            "pi": player.pi,
            "h_hat": int(belief * 100),
            "threshold": fmt2(threshold),
            "prize": prize,
        }


page_sequence = [
    Signal,
    Belief,
    Choice,
    Result
]
