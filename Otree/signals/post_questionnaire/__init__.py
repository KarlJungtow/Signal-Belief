from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'post_questionnaire'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    gender = models.StringField()
    age = models.IntegerField()
    risk_aversion = models.IntegerField(
        choices=[
            [1, 'Low'],
            [2, 'Medium'],
            [3, 'High'],
        ],
        widget=widgets.RadioSelectHorizontal
    )



# PAGES
class questionnaire(Page):
    form_model = "player"
    form_fields = ["gender", "age", "risk_aversion"]


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [questionnaire]
