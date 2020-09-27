import collections
import functools
import operator
from pprint import pprint

import arrow
from prettytable import PrettyTable
from sportradar import NFL
from yfpy import Data
from yfpy.query import YahooFantasySportsQuery


# logging.basicConfig(level=logging.INFO)
# logging.debug('Script has started.')


def get_roster_players(team_id_list):
    global game_week
    pos_values = {
        'QB': 1.2,
        'RB': 1.0,
        'WR': 1.0,
        'TE': 1.0,
        'W/R/T': 1.0,
        'DEF': 1.0,
        'K': 1.0,
        'D': 0.8,
    }

    player_list = list()
    for team_id in team_id_list:
        # Load team info; returns a Team object
        manager_info = yf.get_team_info(team_id=team_id)

        # Get manager name
        manager_name = get_manager_name(manager_info)

        # Set current game_week
        update_current_week(manager_info)

        # Load roster info; returns a list of Player objects
        players = yf.get_team_roster_player_info_by_week(team_id=team_id)
        for player in players:
            player = player['player']
            player_pos = player.primary_position
            roster_pos = player.selected_position_value  # Position in team's roster
            if roster_pos != 'BN':
                if player.is_undroppable == '1':
                    player_value = round(pos_values.get(player_pos) * 1.5, 1)
                    is_undroppable = True
                else:
                    player_value = pos_values.get(player_pos)
                    is_undroppable = False
                player_dict = {
                    'name': player.name.full,
                    'team_name': player.editorial_team_full_name,
                    'team_abbr': player.editorial_team_abbr,
                    'pos': player.primary_position,
                    'player_value': player_value,
                    'is_undroppable': is_undroppable,
                    'manager': manager_name
                }
                player_list.append(player_dict)

    return player_list


def get_manager_name(team_obj):
    managers = team_obj.managers
    manager = managers['manager']
    return manager.nickname


def update_current_week(team_obj):
    global game_week
    for match in team_obj.matchups:
        match = match['matchup']
        if match.status == 'midevent':
            game_week = str(match.week)


def get_weekly_schedule(week):
    SR_api_key = "8ud4engmjwxzk9gw7up653j8"
    nfl = NFL.NFL(SR_api_key)
    game_list = nfl.get_weekly_schedule(year=2020, nfl_season='REG', nfl_season_week=week).json()
    print(game_list)

    if int(game_list['week']['title']) != int(game_week):
        print('Error finding week')
    else:
        game_list = game_list['week']['games']

    game_dict_list = list()
    for item in game_list:
        game_dict = dict()
        away = item['away']['name']
        home = item['home']['name']
        away_abbr = item['away']['alias']
        home_abbr = item['home']['alias']

        game_dict['game_num'] = str(item['number'])
        game_dict['game_time'] = arrow.get(item['scheduled']).floor('hour')
        game_dict['away_team'] = away
        game_dict['home_team'] = home
        game_dict['away_abbr'] = away_abbr
        game_dict['home_abbr'] = home_abbr
        game_dict['teams'] = [away, home]
        game_dict['game_title'] = f'{away_abbr} vs. {home_abbr}'
        game_dict['broadcast'] = item['broadcast']['network']
        game_dict['values'] = list()
        game_dict['players'] = list()
        game_dict_list.append(game_dict)

    return game_dict_list


def assign_players_to_games(week_games, player_list):
    for week_game in week_games:
        game_players = week_game.get('players', [])  # Returns list of players
        player_count = 0
        for player in player_list:
            if player['team_name'] in week_game['teams']:
                player_count += 1
                player.update({'num': player_count})
                game_players.append(player)

            week_game['players'] = game_players
    print(weekly_games)
    return week_games


def sum_player_values(week_games):
    for week_game in week_games:
        week_game['values'] = sum(week_game['values'])
        if week_game['values'] == 0:
            week_game['values'] = float(0.0)

    return week_games


def sort_game_list(week_games):
    return sorted(week_games, key=lambda k: (k['game_time'], -k['values']))


def create_print_table(game_list):
    x = PrettyTable()
    x.field_names = ['Score', 'Game Time', 'Channel', 'Match']
    x.align['Game Time'] = 'l'
    x.align['Channel'] = 'c'
    x.align['Match'] = 'l'

    for game in game_list:
        score = game['values']
        match = game['away_team'] + ' vs. ' + game['home_team']
        game_time = arrow.get(game['game_time'])
        game_time_human = game_time.to('US/Central').humanize(granularity=["hour"])
        if game_time_human == "in 0 hours":
            game_time_human = "now"
        broadcast = game['broadcast']
        if game_time > arrow.now():
            x.add_row([score, game_time_human, broadcast, match])

    # TODO: Split value per game by

    return x


if __name__ == "__main__":
    # SETUP DATA
    auth_dir = "auth"
    league_id = "230376"
    game_id = "399"
    game_code = "nfl"
    all_output_as_json = False
    game_week = 2
    team_IDs = [3, 4]  # '1', '9']  # 3 = Mark, 4 = Lauren

    yf = YahooFantasySportsQuery(auth_dir=auth_dir,
                                 league_id=league_id,
                                 game_id=game_id,
                                 game_code=game_code,
                                 all_output_as_json=all_output_as_json)

    # Fetch and combine rosters by team using yfpy
    players = get_roster_players(team_IDs)
    print(players)

    # Fetch weekly NFL scheduled
    weekly_games = get_weekly_schedule(week=game_week)

    # Assign player position values, sum by team
    weekly_games = assign_players_to_games(week_games=weekly_games, player_list=players)
    print(weekly_games)

    #
    # # Sort list of games by game_time ASC, values DESC
    # weekly_games = sort_game_list(weekly_games)
    #
    # # Use PrettyTable to print table of game times
    # table = create_print_table(weekly_games)
    # print(table)

    # Tools to sum list of dictionaries
