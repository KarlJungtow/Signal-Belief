# __init__.py (or pages.py/models.py)
from otree.api import *
from pathlib import Path

doc = """Your app description"""


class C(BaseConstants):
    NAME_IN_URL = 'intro'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1  # all 5 questions on a single page

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    # Q1: True / False
    cq1_other_influence = models.BooleanField(
        label="Other people's decisions will influence my payoff.",
        choices=[
            [True, 'True'],
            [False, 'False'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    # Q2: multiple choice
    cq2_borrow_points = models.StringField(
        label=(
            "Suppose Period 1 endowment is 5. How many points do you borrow "
            "if you decide to consume 9 units?"
        ),
        choices=[
            ['nothing', 'Nothing'],
            ['4', '4'],
            ['14', '14'],
            ['10', '10'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    # Q3: True / False
    cq3_price_increase_prob = models.BooleanField(
        label="Without the hint, the probability of price of consumption good to increase is 50%.",
        choices=[
            [True, 'True'],
            [False, 'False'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    # Q4: multiple choice
    cq4_hint_duration = models.StringField(
        label='When you click on “Get hint” button, the hint will be shown for …',
        choices=[
            ['8_seconds', '8 seconds'],
            ['30_seconds', '30 seconds'],
            ['1_minute', '1 minute'],
            ['unlimited', 'Unlimited time'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    # Q5: True / False
    cq5_price_increase_dots = models.BooleanField(
        label='The price will increase if the majority of the dots are red.',
        choices=[
            [True, 'True'],
            [False, 'False'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

class WelcomePage(Page):
    pass

class GeneralInstructions(Page):
    pass

class ComprehensionTest(Page):
    form_model = 'player'
    form_fields = ['cq1_other_influence', 'cq2_borrow_points', 'cq3_price_increase_prob', 'cq4_hint_duration', 'cq5_price_increase_dots']

    def error_message(self, values):
        errors = {}
        # Question 1: Correct answer = False
        if values['cq1_other_influence'] is not False:
            errors['cq1_other_influence'] = (
                "This is an individual decision-making study, so other people’s "
                "decisions do not influence your payoff."
            )

        # Question 2: Correct answer = '4'
        if values['cq2_borrow_points'] != '4':
            errors['cq2_borrow_points'] = (
                "If you consume more units than you have in your endowment in Period 1, "
                "then you borrow C₁ − E₁ units of money which you will repay at the price "
                "level in Period 2. In this example, the endowment is 5 and consumption is 9, "
                "resulting in a 4 unit loan."
            )

        # Question 3: Correct answer = True
        if values['cq3_price_increase_prob'] is not True:
            errors['cq3_price_increase_prob'] = (
                "In Period 1, the price of the consumption good is 1. In Period 2, the price "
                "can decrease to 0.5 (a 50% decrease) or increase to 2 (a 100% increase), and "
                "these outcomes are equally likely. Therefore, the probability that the price "
                "of the consumption good will increase is 50%."
            )

        # Question 4: Correct answer = '8_seconds'
        if values['cq4_hint_duration'] != '8_seconds':
            errors['cq4_hint_duration'] = (
                "The price hint in each round will be shown only for 8 seconds. "
                "Each round, there will be a new hint."
            )

        # Question 5: Correct answer = True
        if values['cq5_price_increase_dots'] is not True:
            errors['cq5_price_increase_dots'] = (
                "If there are more red dots than blue dots, then the price in Period 2 will be 2."
            )

        # If no errors, return None; otherwise oTree will display field-specific feedback
        return errors or None

class SyncGate(WaitPage):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [
    WelcomePage,
    GeneralInstructions,
    ComprehensionTest,
    SyncGate,
]
