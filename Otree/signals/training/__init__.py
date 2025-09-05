from otree.api import *
import itertools, random

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

class Subsession(BaseSubsession): pass

def creating_session(subsession):
    combos = list(itertools.product(C.PIS, C.XS))
    for p in subsession.get_players():
        if subsession.round_number == 1:
            schedule = combos[:]
            random.shuffle(schedule)
            p.participant.vars['training_schedule'] = schedule
        pi, income_factor = p.participant.vars['training_schedule'][subsession.round_number - 1]
        p.pi = pi
        p.income_factor = income_factor
        p.p2 = pi * C.P1
        p.c1_max_cached = p.calc_c1_max()

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    pi = models.FloatField()
    income_factor = models.FloatField()
    p2 = models.FloatField()
    c1_max_cached = models.FloatField()
    c1 = models.FloatField()
    c2_realized = models.FloatField()
    u_realized = models.FloatField()

    def calc_c1_max(self):
        return (self.pi * self.income_factor * C.Y1 + C.R * C.Y1 - self.p2) / (C.R * C.P1)

    def c2_given(self, c1, pi):
        s = C.Y1 - C.P1 * float(c1)
        p2 = pi * C.P1
        return (pi * self.income_factor * C.Y1 + C.R * s) / p2

    def u_given(self, c1, pi):
        return float(c1) * self.c2_given(c1, pi)

class Choice(Page):
    form_model = 'player'
    form_fields = ['c1']

    @staticmethod
    def vars_for_template(player: Player):
        rows = []
        for c in range(1, 21):  # 1 through 20, like in Table 1
            c = float(c)
            # π = 0.5
            c2_05 = player.c2_given(c, 0.5)
            u_05 = c * c2_05 if c2_05 >= 1 else None
            # π = 1.5
            c2_15 = player.c2_given(c, 1.5)
            u_15 = c * c2_15 if c2_15 >= 1 else None
            rows.append(dict(
                c1=int(c),
                u05=u_05,
                u15=u_15,
                infeasible05=(c2_05 < 1),
                infeasible15=(c2_15 < 1),
            ))

        return dict(
            y1=C.Y1,
            p1=C.P1,
            x=player.income_factor,
            y2_pi05=0.5 * player.income_factor * C.Y1,
            y2_pi15=1.5 * player.income_factor * C.Y1,
            c1_max=player.c1_max_cached,
            start_c1=1,
            table_rows=rows,
        )

    @staticmethod
    def error_message(player, values):
        c1 = values['c1']
        if not (1 <= c1 <= player.c1_max_cached):
            return f'c1 must be between 1 and {player.c1_max_cached:.2f}.'

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.c2_realized = player.c2_given(player.c1, player.pi)
        player.u_realized = player.c1 * player.c2_realized

class SyncGate(WaitPage):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [Choice, SyncGate]
