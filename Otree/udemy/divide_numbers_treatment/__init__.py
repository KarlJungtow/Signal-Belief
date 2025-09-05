from otree.api import *
import random

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'divide_numbers_treatment'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    DIVISOR_1 = 2
    DIVISOR_2 = 4



class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    division_result_entered = models.FloatField(label="Result")
    random_number = models.IntegerField(label="Random Number")
    is_treatment_1 = models.BooleanField
    division_result_correct = models.FloatField()

# FUNCTIONS
def creating_session(subsession):
    number_players = len(subsession.get_players())

# PAGES
class MyPage(Page):
    pass


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [MyPage, ResultsWaitPage, Results]
