import logging
import os
import pprint
import unittest
import warnings
from unittest import skip, TestCase
import collections, functools, operator
from operator import itemgetter
import datetime

from yfpy import Data
from yfpy.models import Game, StatCategories, User, Scoreboard, Settings, Standings, League, Player, Team, \
    TeamPoints, TeamStandings, Roster
from yfpy.query import YahooFantasySportsQuery
# import nflgame
import requests
from sportradar import NFL
import arrow
from prettytable import PrettyTable

game_week = 3


class YFQuery:

    def __init__(self):
        # Suppress YahooFantasySportsQuery debug logging
        logging.getLogger("yfpy.query").setLevel(level=logging.INFO)

        # Ignore resource warnings from unittest module
        warnings.simplefilter("ignore", ResourceWarning)

        # Turn on/off example code stdout printing output
        self.print_output = True

        # Put private.json (see README.md) in examples directory
        auth_dir = "auth"

        # Example code will output data here
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

        # Example vars using public Yahoo league (still requires auth through a personal Yahoo account - see README.md)
        self.game_id = "399"  # 2020 NFL season game_id
        self.game_code = "nfl"
        self.season = "2020"
        self.league_id = "230376"

        # Test vars
        self.chosen_week = 1
        self.chosen_date = "2020-09-11"  # NHL
        self.team_id = 3
        self.team_name = "The Brady Bunch"
        self.player_id = "7200"  # NFL: Aaron Rodgers
        self.player_key = self.game_id + ".p." + self.player_id

        # Instantiate yfpy objects
        self.yahoo_data = Data(self.data_dir)
        self.yahoo_query = YahooFantasySportsQuery(auth_dir, self.league_id, game_id=self.game_id,
                                                   game_code=self.game_code, offline=False, all_output_as_json=False)

        # Manually override league key for example code to work
        self.yahoo_query.league_key = self.game_id + ".l." + self.league_id

    # ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ •
    # ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ SAVING AND LOADING FANTASY FOOTBALL GAME DATA • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ •
    # ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ •

    def get_team_roster_player_info(self, team_id):
        query_result_data = self.yahoo_query.get_team_roster_player_info_by_week(team_id=team_id)
        return query_result_data


SR_api_key = '8ud4engmjwxzk9gw7up653j8'
yf = YFQuery()


def get_roster_team_counts(team_id_list):
    team_list = list()
    team_import_dict = dict()
    for team_ID in team_IDs:
        players = yf.get_team_roster_player_info(team_id=team_ID)
        pos_values = {'QB': 1.0, 'RB': 1.0, 'WR': 1.0, 'TE': 1.0, 'W/R/T': 1.0, 'DEF': 1.0, 'K': 1.0, 'D': 0.5}
        for player in players:
            player = player['player']
            pos = player.selected_position.position
            if pos != 'BN':
                player_value = pos_values.get(pos)
                # player_value = 0.5 if pos == 'D' else 1.0
                team = player.editorial_team_full_name
                player_dict = {team: player_value}
                team_list.append(player_dict)

    team_values = dict(functools.reduce(operator.add,
                                        map(collections.Counter, team_list)))

    team_values = dict(sorted(team_values.items(), key=operator.itemgetter(1), reverse=True))

    return team_values


def get_weekly_schedule(week):
    nfl = NFL.NFL(SR_api_key)
    game_list = nfl.get_weekly_schedule(year=2020, nfl_season='REG', nfl_season_week=week).json()

    if int(game_list['week']['title']) != int(game_week):
        print('Error finding week')
    else:
        game_list = game_list['week']['games']

    game_dict_list = list()
    for game in game_list:
        game_dict = dict()
        game_num = str(game['number'])
        away = game['away']['name']
        home = game['home']['name']

        game_dict['game_num'] = game_num
        game_dict['game_time'] = game['scheduled']
        game_dict['arrow_time'] = arrow.get(game['scheduled'])
        game_dict['human_time'] = arrow.get(game['scheduled']).to('US/Central').humanize(granularity=["hour"])
        # game_dict['game_utc_offset'] = game['utc_offset']
        game_dict['away_team'] = away
        game_dict['home_team'] = home
        game_dict['teams'] = [away, home]
        game_dict['broadcast'] = game['broadcast']['network']
        game_dict['values'] = list()
        game_dict_list.append(game_dict)

    return game_dict_list


team_IDs = ['3', '4']
roster_counts = get_roster_team_counts(team_IDs)
weekly_games = get_weekly_schedule(week=game_week)


def get_value(elem):
    return elem['values']


def get_gametime(elem):
    return elem['game_time']


def sort_game_list(week_games):
    return sorted(week_games, key=lambda k: (k['human_time'], -k['values']))


for game in weekly_games:
    for team, value in roster_counts.items():
        if team in game['teams']:
            game['values'].append(value)

for game in weekly_games:
    game['values'] = sum(game['values'])
    if game['values'] == 0:
        game['values'] = float(0.0)

weekly_games = sort_game_list(weekly_games)

x = PrettyTable()
x.field_names = ['Score', 'Game Time', 'Channel', 'Matchup']
x.align['Matchup'] = 'l'
x.align['Channel'] = 'c'
print('Best Games of the Week')

for game in weekly_games:
    score = game['values']
    away_team = game['away_team']
    home_team = game['home_team']
    matchup = f'{home_team} vs {away_team}'
    game_time = arrow.get(game['game_time'])
    game_time_human = game_time.to('US/Central').humanize(granularity=["hour"])
    broadcast = game['broadcast']
    if game_time > arrow.now():
        x.add_row([score, game_time_human, broadcast, matchup])
    # print(f'Score: {score} - {home_team} vs {away_team} [{game_time} on {broadcast}]')

print(x.get_string())
