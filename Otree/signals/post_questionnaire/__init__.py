from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'post_questionnaire'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    LIKERT_1_7 = [
        [1, '1 – Strongly disagree'],
        [2, '2'],
        [3, '3'],
        [4, '4 – Neutral'],
        [5, '5'],
        [6, '6'],
        [7, '7 – Strongly agree'],
    ]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):


    age = models.IntegerField(
        label='What is your age',
    )
    gender = models.IntegerField(
        label='What is your gender',
        choices=[
                 [1, 'Male'],
                 [2, 'Female'],
                 [3, 'Non-Binary'],
                 [4, 'Diverse']
        ]
        ,
        widget=widgets.RadioSelect,
    )
    highest_degree = models.IntegerField(
        choices=[
            [1, 'Abitur / Fachabitur'],
            [2, 'Berufsausbildung'],
            [3, 'Bachelor'],
            [4, 'Diplom/Master/Magister'],
            [5, 'other'],
        ],
        widget=widgets.RadioSelect,
        label='What is the highest degree or level of education you have completed?'
    )
    # 1.
    q1 = models.IntegerField(
        choices=C.LIKERT_1_7,
        widget=widgets.RadioSelectHorizontal,
        label="I often start out expecting the worst, even though I will probably do OK."
    )

    # 2.
    q2 = models.IntegerField(
        choices=C.LIKERT_1_7,
        widget=widgets.RadioSelectHorizontal,
        label="I worry about how things will turn out."
    )

    # 3.
    q3 = models.IntegerField(
        choices=C.LIKERT_1_7,
        widget=widgets.RadioSelectHorizontal,
        label="I often worry that I won’t be able to carry through my intentions."
    )

    # 4.
    q4 = models.IntegerField(
        choices=C.LIKERT_1_7,
        widget=widgets.RadioSelectHorizontal,
        label="I spend lots of time imagining what could go wrong."
    )

    # 5.
    q5 = models.IntegerField(
        choices=C.LIKERT_1_7,
        widget=widgets.RadioSelectHorizontal,
        label="I imagine how I would feel if things went badly."
    )

    # 6.
    q6 = models.IntegerField(
        choices=C.LIKERT_1_7,
        widget=widgets.RadioSelectHorizontal,
        label="In these situations, sometimes I worry more about looking like a fool than doing really well."
    )
    # Question 5
    q7 = models.IntegerField(
        label="How do you see yourself: are you generally a person who is fully prepared to take risks or do you try to avoid taking risks? "
              "Please tick a box on the scale, where the value 0 means: ‘not at all willing to take risks’ and the value 10 means: "
              "‘very willing to take risks’.",
        choices=[[i, str(i)] for i in range(0, 11)],   # Likert 0–10
        widget=widgets.RadioSelectHorizontal
    )

    # Question 6
    q8 = models.IntegerField(
        label='Please rate the following statement: “Debt is an integral part of today’s life.”',
        choices=[
            [1, '1'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
        ],   # Likert 1–6
        widget=widgets.RadioSelectHorizontal
    )

    # Question 7
    q9 = models.IntegerField(
        label='What do you think how does the average participant in this experiment rate the following statement? '
              '“There is no excuse for borrowing money.”',
        choices=[
            [1, '1'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
        ],  # Likert 1–6
        widget=widgets.RadioSelectHorizontal
    )

    # Question 8
    q10 = models.StringField(
        label='Have you ever taken out a loan?',
        choices=[
            ['never', 'Never'],
            ['once', 'Once'],
            ['2_3', '2–3 times'],
            ['more_3', 'More than 3 times'],
        ],
        widget=widgets.RadioSelect
    )

    q11 = models.StringField(
        label=(
            "Imagine you put 100 € into a savings account with a fixed interest rate of 2% per year. "
            "You leave the money there for 5 years and do not make any further deposits or withdrawals. "
            "How much will you have on the account after 5 years?"
        ),
        choices=[
            ['more_110', 'More than 110 €'],
            ['exact_110', 'Exactly 110 €'],
            ['less_110', 'Less than 110 €'],
            ['dk', 'Don’t know'],
        ],
        widget=widgets.RadioSelect
    )

    # Question 10 → q12
    q12 = models.StringField(
        label=(
            "Imagine the interest rate on your savings account is 1% per year and inflation is 2% per year. "
            "After 1 year, with the money in this account, you would be able to buy…"
        ),
        choices=[
            ['more_today', 'More than today'],
            ['same_today', 'Exactly the same as today'],
            ['less_today', 'Less than today'],
            ['dk', 'Don’t know'],
        ],
        widget=widgets.RadioSelect
    )

    # Question 11 → q13
    q13 = models.StringField(
        label=(
            "Suppose inflation turns out to be higher than people expected when they signed their loan "
            "and savings contracts. Who benefits the most from this situation?"
        ),
        choices=[
            ['debtors', 'People with large fixed-rate debts (e.g. mortgages)'],
            ['savers', 'People with savings'],
            ['neither', 'People with no debts or savings'],
            ['dk', 'Don’t know'],
        ],
        widget=widgets.RadioSelect
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
page_sequence = [questionnaire_1, questionnaire_2, questionnaire_3, questionnaire_4]
