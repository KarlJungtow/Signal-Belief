from otree.api import *
import itertools
import random
from helper_functions import *


class C(BaseConstants):
    NAME_IN_URL = 'training'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 4

    Y1 = 10.0
    P1 = 1.0
    I = 0.0
    R = 1.0 + I

    PIS = [0.5, 1.5]
    XS = [0.5, 1.5]


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    combos = list(itertools.product(C.PIS, C.XS))
    for p in subsession.get_players():
        if subsession.round_number == 1:
            schedule = combos[:]
            random.shuffle(schedule)
            p.participant.vars['training_schedule'] = schedule

        pi, income_factor = p.participant.vars['training_schedule'][
            subsession.round_number - 1
        ]
        p.pi = pi
        p.income_factor = income_factor
        p.p2 = pi * C.P1
        p.c1_max = calc_c1_max(p, C)


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pi = models.FloatField()
    income_factor = models.FloatField()
    p2 = models.FloatField()
    c1_max = models.FloatField()

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

page_sequence = [
    Choice,
]
