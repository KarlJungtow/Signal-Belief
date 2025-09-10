# __init__.py (or pages.py/models.py)
from otree.api import *
from pathlib import Path
from .question_reader import load_questions

doc = """Your app description"""


class C(BaseConstants):
    NAME_IN_URL = 'intro'
    PLAYERS_PER_GROUP = None
    QUESTIONS = load_questions(Path(__file__).with_name('questions.xlsx'))
    NUM_ROUNDS = 1  # all 5 questions on a single page

    # Optional sanity check
    assert len(QUESTIONS) >= 4, "Need at least 5 questions in questions.xlsx"


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Hard-coded 5 fields pulling label/choices at import time
    q1 = models.IntegerField(
        label=C.QUESTIONS[0]['label'],
        choices=C.QUESTIONS[0]['choices'],
        widget=widgets.RadioSelect,
    )
    q2 = models.IntegerField(
        label=C.QUESTIONS[1]['label'],
        choices=C.QUESTIONS[1]['choices'],
        widget=widgets.RadioSelect,
    )
    q3 = models.IntegerField(
        label=C.QUESTIONS[2]['label'],
        choices=C.QUESTIONS[2]['choices'],
        widget=widgets.RadioSelect,
    )
    q4 = models.IntegerField(
        label=C.QUESTIONS[3]['label'],
        choices=C.QUESTIONS[3]['choices'],
        widget=widgets.RadioSelect,
    )
    q5 = models.IntegerField(
        label=C.QUESTIONS[4]['label'],
        choices=C.QUESTIONS[4]['choices'],
        widget=widgets.RadioSelect,
    )


# PAGES
class WelcomePage(Page):
    pass


class GeneralInstructions(Page):
    pass


class ComprehensionTest(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2', 'q3', 'q4', 'q5']

    @staticmethod
    def error_message(player, values):
        # Block progression until all answers are correct
        correct = {
            'q1': C.QUESTIONS[0]['correct'],
            'q2': C.QUESTIONS[1]['correct'],
            'q3': C.QUESTIONS[2]['correct'],
            'q4': C.QUESTIONS[3]['correct'],
            'q5': C.QUESTIONS[4]['correct'],
        }
        errors = {}
        for field, right in correct.items():
            if values.get(field) != right:
                errors[field] = 'This is not correct. Please try again'
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
