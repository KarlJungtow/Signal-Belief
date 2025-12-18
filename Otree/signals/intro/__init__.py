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
        label="Die Entscheidungen anderer Menschen beeinflussen meine Auszahlung.",
        choices=[
            [True, 'Richtig'],
            [False, 'Falsch'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    # Q2: multiple choice
    cq2_borrow_points = models.StringField(
        label=(
            "Angenommen, die Dotierung für Periode 1 beträgt 5. Wie viele Punkte leihen Sie sich, "
            "wenn Sie sich entscheiden, 9 Einheiten zu konsumieren?"
        ),
        choices=[
            ['nothing', 'Nichts'],
            ['4', '4'],
            ['14', '14'],
            ['10', '10'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    # Q3: True / False
    cq3_price_increase_prob = models.BooleanField(
        label="Ohne diesen Hinweis beträgt die Wahrscheinlichkeit, dass der Preis für Konsumgüter steigt, 50%.",
        choices=[
            [True, 'Richtig'],
            [False, 'Falsch'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    # Q4: multiple choice
    cq4_hint_duration = models.StringField(
        label='Wenn Sie auf die Schaltfläche „Hinweis anzeigen“ klicken, wird der Hinweis … Sekunden lang angezeigt.',
        choices=[
            ['8_seconds', '8 Sekunden'],
            ['30_seconds', '30 Sekunden'],
            ['1_minute', '1 Minute'],
            ['unlimited', 'Unbegrenzte Zeit'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    # Q5: True / False
    cq5_price_increase_dots = models.BooleanField(
        label='Der Preis steigt, wenn die Mehrheit der Punkte rot ist.',
        choices=[
            [True, 'Richtig'],
            [False, 'Falsch'],
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
                "Dies ist eine Studie zur individuellen Entscheidungsfindung,  "
                "daher haben die Entscheidungen anderer Personen keinen Einfluss auf Ihren Gewinn."
            )

        # Question 2: Correct answer = '4'
        if values['cq2_borrow_points'] != '4':
            errors['cq2_borrow_points'] = (
                "Wenn Sie in Periode 1 mehr Einheiten verbrauchen, als Sie in Ihrer Dotierung haben, "
                "dann leihen Sie sich C₁ − E₁ Einheiten Geld, die Sie zum Preisniveau in Periode 2 zurückzahlen."
                "In diesem Beispiel beträgt die Dotierung 5 und der Verbrauch 9, was zu einem Kredit von 4 Einheiten führt."
            )

        # Question 3: Correct answer = True
        if values['cq3_price_increase_prob'] is not True:
            errors['cq3_price_increase_prob'] = (
                "In Periode 1 beträgt der Preis des Konsumguts 1. In Periode 2 kann  "
                "der Preis auf 0,5 sinken (ein Rückgang um 50%) oder auf 2 steigen (ein Anstieg um 100%), "
                "wobei diese Ergebnisse gleich wahrscheinlich sind. Daher beträgt die Wahrscheinlichkeit, "
                "dass der Preis des Konsumguts steigt, 50%."
            )

        # Question 4: Correct answer = '8_seconds'
        if values['cq4_hint_duration'] != '8_seconds':
            errors['cq4_hint_duration'] = (
                "Der Preis-Hinweis wird in jeder Runde nur für 8 Sekunden angezeigt. "
                "In jeder Runde gibt es einen neuen Hinweis."
            )

        # Question 5: Correct answer = True
        if values['cq5_price_increase_dots'] is not True:
            errors['cq5_price_increase_dots'] = (
                "Wenn es mehr rote Punkte als blaue Punkte gibt, dann wird der Preis in Periode 2 2 betragen."
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
