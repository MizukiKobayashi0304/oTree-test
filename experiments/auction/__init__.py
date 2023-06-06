from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
    Page,
    WaitPage,
)
import random  # must import to use random library - must import for every code file needed

doc = """
This is a second price sealed-bid auction.
"""


class Constants(BaseConstants):
    name_in_url = 'auction'
    players_per_group = 3
    num_rounds = 3


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    highest_bid = models.CurrencyField()
    second_highest_bid = models.CurrencyField()
    winner = models.IntegerField()


class Player(BasePlayer):
    value = models.CurrencyField()
    bid = models.CurrencyField()
    is_winner = models.BooleanField()


# FUNCTIONS
def auction_outcomes(g: Group):
    # will be a group function, because you need all players in group to determine
    # プレイヤーのリストをとってくる
    players = g.get_players()  # naming the variable players - it will now be a set of all players in group

    # Get the set of bids from the players
    # brackets = list will contain bid for all players
    # それぞれのプレイヤーのbidのリストを作成する
    bids = [p.bid for p in players]

    # Sort bids in descending order
    #bidを降順に並べ直す
    bids.sort(reverse=True)

    # set the highest and second highest bids to the appropriate group variables
    # Python uses 0-based arrays
    # 一番高いbidと二番目に高いbidを取得して、highest_bidとsecond_highest_bidに収納する
    g.highest_bid = bids[0]
    g.second_highest_bid = bids[1]

    # Tie Break
    # 引き分けの時の処理を行う
    # We always do this even when there is not a tie
    # first get the set of player IDs who bid the highest
    # bidが一番高かったプレイヤーのリストを取得する
    highest_bidders = [p.id_in_group for p in players if p.bid == g.highest_bid]

    # next randomly select one of these player IDs to be the winner
    # 一番高かったプレイヤーのリストからランダムに一人プレイヤーを選択してwinnerに入れる
    g.winner = random.choice(highest_bidders)

    # finally get the player model of the winning bidder and flag as winner
    # winnerになったplayerを取得して、is_winnerをTrueにする
    winning_player = g.get_player_by_id(g.winner)  # we want winner ID defined above
    winning_player.is_winner = True

    # Set payoffs
    # それぞれのplayerのpayoffを計算して代入する。
    for p in players:  # looping over all players when not using a list
        if p.is_winner:
            p.payoff = p.value - g.second_highest_bid
        else:
            p.payoff = 0

    # Add in total payoff over earnings


def creating_session(subsession):
    if subsession.round_number == 1 or subsession.round_number == 3:
        subsession.group_randomly()
    else:
        subsession.group_like_round(subsession.round_number - 1)
    print('in creating session')
    # Establish a total earnings variable for each participant and
    # Initialize to 0 at beginning of session.
    for p in subsession.get_players():  # loops for every single period
        p.value = random.random()*100  # value is between 0-100
        p.is_winner = False  # all players are non winners at first
        if subsession.round_number == 1:
            p.participant.vars['totalEarnings'] = 0
    

# PAGES
class Instructions(Page):
    def is_displayed(self):
        return self.round_number == 1


class Bid(Page):
    form_model = 'player'  # to get the form field you want from the player model (bid is under player model)
    form_fields = ['bid']

    @staticmethod
    def get_timeout_seconds(player: Player):
        return 60


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = 'auction_outcomes'
    body_text = 'Please wait for all participants to submit bids.'


class Results(Page):
    pass


class ThankYou(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds



page_sequence = [Instructions, Bid, ResultsWaitPage, Results, ThankYou]
