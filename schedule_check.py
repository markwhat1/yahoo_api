import collections
import functools
import operator
from pprint import pprint
import logging

import arrow
from prettytable import PrettyTable
from sportradar import NFL
from yfpy import Data
from yfpy.query import YahooFantasySportsQuery


logging.basicConfig(level=logging.INFO)
# logging.debug('Script has started.')


def get_roster_players(team_id_list):
    global game_week
    global managers
    pos_values = {
        'QB': 1.0,
        'RB': 1.0,
        'WR': 1.0,
        'TE': 1.0,
        'W/R/T': 1.0,
        'DEF': 1.0,
        'K': 1.0,
        'D': 0.5,
    }

    all_manager_players = list()
    for team_id in team_id_list:
        # Load team info; returns a Team object
        manager_info = yf.get_team_info(team_id=team_id)

        # Get manager name
        manager_name = get_manager_name(manager_info)
        managers.append(manager_name)

        # Set current game_week
        update_current_week(manager_info)

        # Load roster info; returns a list of Player objects
        players = yf.get_team_roster_player_info_by_week(team_id=team_id)
        manager_player_dict = dict()
        manager_player_dict['manager'] = manager_name
        manager_player_list = list()
        for player in players:
            player = player['player']
            player_pos = player.primary_position
            roster_pos = player.selected_position_value  # Position in team's roster
            if roster_pos != 'BN':
                # if player.is_undroppable == '1':
                #     player_value = round(pos_values.get(player_pos) * 1.5, 1)
                #     is_undroppable = True
                # else:
                #     player_value = pos_values.get(player_pos)
                #     is_undroppable = False
                player_value = pos_values.get(player_pos)
                player_dict = {
                    'name': player.name.full,
                    'team_name': player.editorial_team_full_name,
                    'team_abbr': player.editorial_team_abbr,
                    'pos': player.primary_position,
                    'player_value': player_value,
                    # 'is_undroppable': is_undroppable
                    # 'manager': manager_name
                }
                manager_player_list.append(player_dict)
        manager_player_dict['players'] = manager_player_list
        all_manager_players.append(manager_player_dict)

    return all_manager_players


def get_manager_name(team_obj):
    all_managers = team_obj.managers
    manager = all_managers['manager']
    manager_name = manager.nickname
    manager_name = manager_name.split(' ')[0]
    if manager_name == '--':
        manager_name = 'Deric\'s Dad'
    return manager_name


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

    assert (int(game_list['week']['title']) == int(game_week)), "Week from SportsRadar doesn't match Yahoo"

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
        game_dict_list.append(game_dict)

    return game_dict_list


def assign_players_to_games(week_games, manager_player_list):
    for week_game in week_games:
        for manager in manager_player_list:
            manager_name = manager['manager']
            players = manager['players']
            game_player_list = list()
            for player in players:
                if player['team_name'] in week_game['teams']:
                    game_player_list.append(player)
            week_game[manager_name] = game_player_list
    return week_games


def sum_player_values(week_games):
    for week_game in week_games:
        total_value = list()
        for manager in managers:
            if week_game[manager]:
                player_list = week_game[manager]
                manager_value = sum(x['player_value'] for x in player_list)
                week_game[manager] = manager_value
                total_value.append(manager_value)
            else:
                week_game[manager] = float(0.0)
        week_game['Total'] = sum(total_value)
    return week_games


def sort_game_list(week_games):
    return sorted(week_games, key=lambda k: (k['game_time'], -k['Total']))


def create_print_table(game_list):
    x = PrettyTable()
    first_fields = ['Game Time', 'Match', 'Channel']
    x.field_names = [*first_fields, *managers, 'Total']
    # x.align['Game Time'] = 'l'
    # x.align['Channel'] = 'c'
    # x.align['Match'] = 'l'

    for item in game_list:
        match = item['away_abbr'] + ' vs. ' + item['home_abbr']
        game_time = arrow.get(item['game_time'])
        game_time_human = game_time.to('US/Central').humanize(granularity=["hour"])
        broadcast = item['broadcast']
        if game_time_human == "in 0 hours":
            game_time_human = "now"
        row = [game_time_human, match, broadcast]
        for manager in managers:
            row.append(item[manager])
        row.append(item['Total'])
        if game_time > arrow.now():
            x.add_row(row)
        print(row)
    return x


if __name__ == "__main__":
    # SETUP DATA
    auth_dir = "auth"
    league_id = "230376"
    game_id = "399"
    game_code = "nfl"
    all_output_as_json = False
    game_week = 3
    managers = list()
    team_IDs = [3, 4]  # '1', '9']  # 3 = Mark, 4 = Lauren
    # team_IDs = range(1, 11)
    yf = YahooFantasySportsQuery(auth_dir=auth_dir,
                                 league_id=league_id,
                                 game_id=game_id,
                                 game_code=game_code,
                                 all_output_as_json=all_output_as_json)

    # Fetch and combine rosters by team using yfpy
    all_players = get_roster_players(team_IDs)

    # Fetch weekly NFL scheduled
    weekly_games = get_weekly_schedule(week=game_week)

    # Assign player position values, sum by team
    weekly_games = assign_players_to_games(week_games=weekly_games, manager_player_list=all_players)

    # Sum player values by Manager
    weekly_games = sum_player_values(weekly_games)

    # Sort list of games by game_time ASC, values DESC
    weekly_games = sort_game_list(weekly_games)

    # Use PrettyTable to print table of game times
    table = create_print_table(weekly_games)
    print(table)
