from otree.api import *
import random
from helper_functions import *

doc = """
Stage 7: Draw one of the 100 main rounds uniformly; then randomly choose
consumption vs belief. If belief is chosen and enabled, pay with the binary
lottery: Pr(win 100) = 1 - (h_hat - h_true)^2.
"""

class C(BaseConstants):
    NAME_IN_URL = 'payoff'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

class Subsession(BaseSubsession): pass
class Group(BaseGroup): pass

class Player(BasePlayer):
    # selection
    paid_index = models.IntegerField()     # index in main_rounds
    paid_treatment = models.StringField()
    paid_round = models.IntegerField()
    payoff_type = models.StringField()     # 'consumption' or 'belief'

    # belief lottery draw
    U_draw = models.FloatField()
    threshold = models.FloatField()
    won_belief = models.BooleanField()
    true_red_count = models.IntegerField
    belief_raw = models.IntegerField

    # raw point outcomes
    u_points = models.FloatField()
    belief_points = models.FloatField()
    threshold = models.FloatField()

    # final money (CurrencyField)
    final_payoff = models.CurrencyField()
    conversion_rate = models.FloatField
    showup_fee = models.FloatField()

def belief_enabled(session):
    return session.config.get('belief_pay_enabled', True)

def set_final_payoff(player: Player):
    rounds = player.participant.vars.get('main_rounds', [])
    # Safety: ignore if somehow empty
    if not rounds:
        player.payoff_type = 'consumption'
        player.paid_index = 0
        player.paid_treatment = 'n/a'
        player.paid_round = 0
        player.u_points = 0
        player.final_payoff = player.session.config.get('showup_fee')
        return

    # 1) Uniform draw over the 100 main rounds
    player.paid_index = random.randrange(len(rounds))
    chosen = rounds[player.paid_index]

    #From which Treatment is the payoff chosen?
    player.paid_treatment = chosen.get('treatment')
    player.paid_round = int(chosen.get('round', 0))

    # 2) Randomly choose payoff type
    player.payoff_type = random.choice(['consumption', 'belief'])

    # 3) Compute payoff
    player.showup_fee = float(player.session.config.get('showup_fee'))
    player.conversion_rate = float(player.session.config.get('conversion_rate'))
    belief_prize = float(player.session.config.get('binary_lotterie_prize'))

    if player.payoff_type == 'consumption' or not belief_enabled(player.session):
        player.u_points = float(chosen.get('u') or 0.0)
        player.payoff = player.u_points * player.conversion_rate
    else:
        # Binary scoring lottery: Pr(win 100) = 1 - (h_hat - h_true)^2
        player.belief_points, player.threshold = run_binary_lottery(chosen, belief_prize)
        player.threshold = round(player.threshold, 2)
        player.payoff = player.belief_points * player.conversion_rate
        player.true_red_count = chosen.get('red_count')
        player.belief_raw = chosen.get('belief_input_raw')
    player.payoff += player.showup_fee

class Final(Page):
    @staticmethod
    def vars_for_template(player: Player):
        if not player.participant.vars.get('final_payoff_set'):
            set_final_payoff(player)
            player.participant.vars['final_payoff_set'] = True
        return dict(belief_enabled=belief_enabled(player.session))

page_sequence = [Final]
