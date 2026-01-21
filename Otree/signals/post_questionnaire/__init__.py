from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'post_questionnaire'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    LIKERT_1_7 = [
        [1, '1 – Stimme überhaupt nicht zu'],
        [2, '2'],
        [3, '3'],
        [4, '4'],
        [5, '5'],
        [6, '6'],
        [7, '7 – Stimme voll und ganz zu'],
    ]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):


    age = models.IntegerField(
        label='Wie alt sind Sie?',
    )
    gender = models.IntegerField(
        label='Was ist Ihr Geschlecht?',
        choices=[
                 [1, 'Männlich'],
                 [2, 'Weiblich'],
                 [3, 'Sonstiges'],
                 [4, 'Keine Angabe']
        ]
        ,
        widget=widgets.RadioSelect,
    )
    highest_degree = models.IntegerField(
        choices=[
            [1, '(Fach-)Abitur / (Fach-)Hochschulreife'],
            [2, 'Berufsausbildung (Lehre) / Fachschule'],
            [3, 'Bachelor (oder im Bachelorstudium)'],
            [4, 'Master / Diplom / Magister / Staatsexamen (oder im Masterstudium)'],
            [5, 'Sonstiges'],
            [6, 'Keine Angabe'],
        ],
        widget=widgets.RadioSelect,
        label="Welcher Bildungsabschluss ist derzeit Ihr höchster Abschluss "
              "(oder in welchem Abschluss befinden Sie sich aktuell)?"
    )
    # 1.
    q1 = models.IntegerField(
        choices=C.LIKERT_1_7,
        widget=widgets.RadioSelectHorizontal,
        label="Ich gehe oft von vornherein vom Schlimmsten aus, obwohl ich wahrscheinlich ganz gut zurechtkommen werde."
    )

    # 2.
    q2 = models.IntegerField(
        choices=C.LIKERT_1_7,
        widget=widgets.RadioSelectHorizontal,
        label="Ich mache mir Sorgen darüber, wie die Dinge ausgehen werden."
    )

    # 3.
    q3 = models.IntegerField(
        choices=C.LIKERT_1_7,
        widget=widgets.RadioSelectHorizontal,
        label="Ich mache mir oft Sorgen, dass ich meine Vorhaben nicht umsetzen kann."
    )

    # 4.
    q4 = models.IntegerField(
        choices=C.LIKERT_1_7,
        widget=widgets.RadioSelectHorizontal,
        label="Ich verbringe viel Zeit damit, mir vorzustellen, was schiefgehen könnte."
    )

    # 5.
    q5 = models.IntegerField(
        choices=C.LIKERT_1_7,
        widget=widgets.RadioSelectHorizontal,
        label="Ich stelle mir vor, wie ich mich fühlen würde, wenn es schlecht läuft."
    )

    # 6.
    q6 = models.IntegerField(
        choices=C.LIKERT_1_7,
        widget=widgets.RadioSelectHorizontal,
        label="In solchen Situationen mache ich mir manchmal mehr Sorgen, mich zu blamieren, als darum, ob ich wirklich gut abschneide."
    )
    # Question 5
    q7 = models.IntegerField(
        label="Wie schätzen Sie sich selbst ein: Sind Sie generell ein Mensch, der bereit ist, Risiken einzugehen, "
        "oder versuchen Sie eher, Risiken zu vermeiden? Bitte kreuzen Sie einen Wert auf der Skala an, wobei 0 bedeutet: 'überhaupt nicht bereit, "
        "Risiken einzugehen' und 10 bedeutet: 'sehr bereit, Risiken einzugehen'.",
        choices=[[i, str(i)] for i in range(0, 11)],   # Likert 0–10
        widget=widgets.RadioSelectHorizontal
    )

    # Question 6
    q8 = models.IntegerField(
        label="Bitte bewerten Sie die folgende Aussage: 'Schulden sind ein fester Bestandteil des heutigen Lebens.'",
        choices=[
            [1, '1: Stimme überhaupt nicht zu'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6: Stimme voll und ganz zu'],
        ],   # Likert 1–6
        widget=widgets.RadioSelectHorizontal
    )

    # Question 7
    q9 = models.IntegerField(
        label="Wie, glauben Sie, bewertet der durchschnittliche Teilnehmer bzw. die durchschnittliche Teilnehmerin dieses Experiments die folgende Aussage?"
        " 'Es gibt keine Entschuldigung dafür, sich Geld zu leihen'.",
        choices=[
            [1, '1: Stimme überhaupt nicht zu'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6: Stimme voll und ganz zu'],
        ],  # Likert 1–6
        widget=widgets.RadioSelectHorizontal
    )

    # Question 8
    q10 = models.StringField(
        label='Haben Sie schon einmal einen Kredit aufgenommen?',
        choices=[
            ['1', 'nie'],
            ['2', 'einmal'],
            ['3', 'zwei- bis dreimal'],
            ['4', 'mehr als dreimal'],
            ['5', 'keine Angabe'],
        ],
        widget=widgets.RadioSelect
    )

    q11 = models.StringField(
        label=(
            "Stellen Sie sich vor, Sie legen 100 € auf ein Sparkonto mit einem festen Zinssatz von 2 % pro Jahr. "
            "Sie lassen das Geld dort 5 Jahre liegen und tätigen keine weiteren Einzahlungen oder Abhebungen. "
            "Wie viel Geld haben Sie nach 5 Jahren auf dem Konto?"
        ),
        choices=[
            ['more_110', 'mehr als 110 €'],
            ['exact_110', 'genau 110 €'],
            ['less_110', 'weniger als 110 €'],
            ['dk', 'weiß ich nicht'],
        ],
        widget=widgets.RadioSelect
    )

    # Question 10 → q12
    q12 = models.StringField(
        label=(
            "Stellen Sie sich vor, der Zinssatz auf Ihrem Sparkonto beträgt 1 % pro Jahr und die Inflation beträgt 2 % pro Jahr."
            "Was könnten Sie sich nach 1 Jahr mit dem Geld auf diesem Konto kaufen?"
        ),
        choices=[
            ['more_today', 'mehr als heute'],
            ['same_today', 'genau so viel wie heute'],
            ['less_today', 'weniger als heute'],
            ['dk', 'weiß ich nicht'],
        ],
        widget=widgets.RadioSelect
    )

    # Question 11 → q13
    q13 = models.StringField(
        label=(
            "Angenommen, die Inflation fällt höher aus, als die Menschen erwartet haben, als sie ihre Kredit- und Sparverträge abgeschlossen haben."
            "Wer profitiert am meisten von der höheren Inflation?"
        ),
        choices=[
            ['debtors', 'Menschen mit festverzinslichen Kreditverträgen (z.B. Hypothekenkrediten)'],
            ['savers', 'Menschen mit Ersparnissen'],
            ['neither', 'Menschen, die weder Ersparnisse noch Kredite haben'],
            ['dk', 'weiß ich nicht'],
        ],
        widget=widgets.RadioSelect
    )

    # Question 12 → q14
    q14 = models.IntegerField(
        label=(
            "Wenn Sie an einem Rennen teilnehmen und die Person auf dem zweiten Platz überholen: "
            "Auf welchem Platz sind Sie dann?"
        ),
        blank=False,
    )

    # Question 13 → q15
    q15 = models.IntegerField(
        label=(
            "Ein Bauer hatte 15 Schafe und bis auf 8 sind alle gestorben. "
            "Wie viele sind übrig?"
        ),
        blank=False,
    )

    # Question 14 → q16
    q16 = models.IntegerField(
        label=(
            "Wenn drei Elfen drei Spielzeuge in einer Stunde einpacken können, wie viele Elfen werden benötigt, "
            "um sechs Spielzeuge in zwei Stunden einzupacken?"
        ),
        blank=False,
    )



# PAGES
class questionnaire_1(Page):
    form_model = "player"
    form_fields = ["gender", "age", "highest_degree"]

class questionnaire_2(Page):
    form_model = "player"
    form_fields = ["q1", "q2", "q3", "q4", "q5", "q6"]

class questionnaire_3(Page):
    form_model = "player"
    form_fields = ["q7", "q8", "q9", "q10"]

class questionnaire_4(Page):
    form_model = "player"
    form_fields = ["q11", "q12", "q13"]

class questionnaire_5(Page):
    form_model = "player"
    form_fields = ["q14", "q15", "q16"]
page_sequence = [questionnaire_1, questionnaire_2, questionnaire_3, questionnaire_4, questionnaire_5]
