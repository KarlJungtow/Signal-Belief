from otree.api import *

class C(BaseConstants):
    NAME_IN_URL = 'wait_sync'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

class Subsession(BaseSubsession): pass
class Group(BaseGroup): pass
class Player(BasePlayer): pass

class SyncAll(WaitPage):
    wait_for_all_groups = True  # ← ensures every participant in session must arrive
    title_text = "Bitte warten"
    body_text = "Bitte warten Sie, bis alle Teilnehmer diesen Punkt erreicht haben. Der nächste Teil beginnt dann gemeinsam."

page_sequence = [SyncAll]