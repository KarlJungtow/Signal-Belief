from otree.api import *
import random
from helper_functions import *

class C(BaseConstants):
    NAME_IN_URL = 'Payoff'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    SUFFIXES = ['A', 'B', 'C']
class Group(BaseGroup):
    pass


class Subsession(BaseSubsession):
    pass

class Player(BasePlayer):

    # ------------------------------
    # Selection / bookkeeping
    # ------------------------------
    paid_index = models.IntegerField()  # (unused now, but you can use it if you want)

    # ------------------------------
    # Chosen consumption rounds (3)
    # ------------------------------
    round_con_A = models.IntegerField()
    round_con_B = models.IntegerField()
    round_con_C = models.IntegerField()

    # Chosen belief rounds (3)
    round_bel_A = models.IntegerField()
    round_bel_B = models.IntegerField()
    round_bel_C = models.IntegerField()

    # Parameters from main rounds
    y1_A = models.IntegerField()
    y1_B = models.IntegerField()
    y1_C = models.IntegerField()

    c1_A = models.FloatField()
    c1_B = models.FloatField()
    c1_C = models.FloatField()

    c2_A = models.FloatField()
    c2_B = models.FloatField()
    c2_C = models.FloatField()

    con_p2_A = models.FloatField()
    con_p2_B = models.FloatField()
    con_p2_C = models.FloatField()

    bel_p2_A = models.FloatField()
    bel_p2_B = models.FloatField()
    bel_p2_C = models.FloatField()

    # Belief lottery draw
    U_draw_A = models.FloatField()
    threshold_A = models.FloatField()
    won_belief_A = models.BooleanField()
    true_red_count_A = models.IntegerField()
    belief_raw_A = models.FloatField()

    U_draw_B = models.FloatField()
    threshold_B = models.FloatField()
    won_belief_B = models.BooleanField()
    true_red_count_B = models.IntegerField()
    belief_raw_B = models.FloatField()

    U_draw_C = models.FloatField()
    threshold_C = models.FloatField()
    won_belief_C = models.BooleanField()
    true_red_count_C = models.IntegerField()
    belief_raw_C = models.FloatField()

    # Raw point outcomes
    u_points_A = models.FloatField()
    u_points_B = models.FloatField()
    u_points_C = models.FloatField()

    # Euro equivalents of consumption payoff
    u_euros_A = models.FloatField()
    u_euros_B = models.FloatField()
    u_euros_C = models.FloatField()

    belief_points_A = models.FloatField()
    belief_points_B = models.FloatField()
    belief_points_C = models.FloatField()

    # Final money (CurrencyField)
    final_payoff = models.CurrencyField()
    conversion_rate = models.FloatField()
    showup_fee = models.FloatField()



    def _triplet(self, prefix):
        """Return [prefix_A, prefix_B, prefix_C] as a list of values."""
        return [getattr(self, f"{prefix}_{s}") for s in C.SUFFIXES]

    # -------- Read-only convenience properties --------

    @property
    def con_rounds(self):
        return self._triplet("round_con")

    @property
    def bel_rounds(self):
        return self._triplet("round_bel")

    @property
    def U_draws(self):
        return self._triplet("U_draw")

    @property
    def thresholds(self):
        return self._triplet("threshold")

    @property
    def won_beliefs(self):
        return self._triplet("won_belief")

    @property
    def true_red_counts(self):
        return self._triplet("true_red_count")

    @property
    def belief_raws(self):
        return self._triplet("belief_raw")

    @property
    def u_points(self):
        return self._triplet("u_points")

    @property
    def u_euros(self):
        return self._triplet("u_euros")

    @property
    def belief_points(self):
        return self._triplet("belief_points")

    @property
    def y1(self):
        return self._triplet("y1")

    @property
    def c1_list(self):
        return self._triplet("c1")

    @property
    def c2_list(self):
        return self._triplet("c2")

    @property
    def con_p2(self):
        return self._triplet("con_p2")

    @property
    def bel_p2(self):
        return self._triplet("bel_p2")

def set_final_payoff(player: Player):
    # reset built-in payoff
    player.payoff = 0

    # main_rounds is a list of dicts created by record_main_round(...)
    rounds = player.participant.vars.get('main_rounds', [])

    # split by treatment
    rounds_A = [r for r in rounds if r.get('treatment') == "Treatment_A"]
    rounds_B = [r for r in rounds if r.get('treatment') == "Treatment_B"]
    rounds_C = [r for r in rounds if r.get('treatment') == "Treatment_C"]

    # choose 3 consumption rounds (one per treatment)
    chosen_consumption_rounds = (
        random.sample(rounds_A, 1) +
        random.sample(rounds_B, 1) +
        random.sample(rounds_C, 1)
    )

    # choose 3 belief rounds (one per treatment)
    chosen_belief_rounds = (
        random.sample(rounds_A, 1) +
        random.sample(rounds_B, 1) +
        random.sample(rounds_C, 1)
    )

    player.conversion_rate = float(player.session.config.get('conversion_rate'))
    belief_prize = float(player.session.config.get('binary_lotterie_prize'))

    # ------------- CONSUMPTION PAYOFFS (3 rounds) -------------
    for chosen, suffix in zip(chosen_consumption_rounds, C.SUFFIXES):
        # which round was chosen
        setattr(player, f"round_con_{suffix}", int(chosen.get('round', 0)))

        # store parameters
        setattr(player, f"y1_{suffix}", int(chosen.get('y1', 0)))
        setattr(player, f"c1_{suffix}", chosen.get('c1', 0))
        setattr(player, f"c2_{suffix}", chosen.get('c2', 0))
        setattr(player, f"con_p2_{suffix}", chosen.get('pi', 0))

        # utility points
        u_val = round(float(chosen.get('u') or 0.0), 2)
        setattr(player, f"u_points_{suffix}", u_val)

        # euro equivalent (points × conversion_rate)
        u_eur = round(u_val * player.conversion_rate, 2)
        setattr(player, f"u_euros_{suffix}", u_eur)

        # add consumption payoff
        player.payoff += u_val * player.conversion_rate

    # ------------- BELIEF PAYOFFS (3 rounds) -------------
    for chosen, suffix in zip(chosen_belief_rounds, C.SUFFIXES):
        setattr(player, f"round_bel_{suffix}", int(chosen.get('round', 0)))
        setattr(player, f"bel_p2_{suffix}", chosen.get('pi', 0))

        belief_pts, threshold_val = run_binary_lottery(chosen, belief_prize)
        setattr(player, f"belief_points_{suffix}", belief_pts)
        setattr(player, f"threshold_{suffix}", threshold_val)

        # add belief payoff
        player.payoff += belief_pts * player.conversion_rate

        # diagnostics
        setattr(player, f"true_red_count_{suffix}", chosen.get('red_count', 0))
        setattr(player, f"belief_raw_{suffix}", chosen.get('belief_input_raw', 0.0))

    # ------------- Show-up fee & final -------------
    player.showup_fee = float(player.session.config.get('showup_fee'))
    player.payoff += player.showup_fee

    # mirror into your custom field as well
    player.final_payoff = player.payoff



class Final(Page):
    @staticmethod
    def vars_for_template(player: Player):
        if not player.participant.vars.get('final_payoff_set'):
            set_final_payoff(player)
            player.participant.vars['final_payoff_set'] = True

        thresholds_pct = [t * 100 for t in player.thresholds]

        return dict(
            con_rounds=player.con_rounds,
            bel_rounds=player.bel_rounds,
            y1=player.y1,
            y2=[15 if v == 5 else 5 for v in player.y1],            # if you store y2_A/B/C in Player
            c1_list=player.c1_list,
            c2_list=player.c2_list,
            con_p2=player.con_p2,
            u_points=player.u_points,
            u_euros=player.u_euros,
            belief_raws=player.belief_raws,
            bel_p2=player.bel_p2,
            thresholds_pct=thresholds_pct,
            belief_points=player.belief_points,
        )


page_sequence = [Final]


page_sequence = [
    Final,
]
