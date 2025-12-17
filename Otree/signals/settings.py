from os import environ

SESSION_CONFIGS = [
    dict(
        name='signals',
        app_sequence=[
                    'intro',
                    'training',
                    'Treatment_A',
                    'Treatment_C',
                    'Treatment_B',
                    'post_questionnaire',
                    'payoff'
            ],
        num_demo_participants=1,
        showup_fee=7.0,
        conversion_rate=0.1,
        binary_lotterie_prize=20,
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.2, participation_fee=4.00, doc=""
)

PARTICIPANT_FIELDS = ["num_obvious_blue", "num_obvious_red"]
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = False

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '7322295187447'
