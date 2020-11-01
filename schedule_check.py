import logging
import time

import arrow
from prettytable import PrettyTable
from sportradar import NFL
from yfpy.query import YahooFantasySportsQuery
import requests
from apprise import Apprise
from markdownify import markdownify
import html2markdown
from pushover import Client
from notifiers import get_notifier
import imgkit
from pygments.formatters import HtmlFormatter


logging.getLogger("yfpy.query").setLevel(logging.INFO)
logging.getLogger("sportradar").setLevel(logging.WARNING)
logging.getLogger("notifiers.core").setLevel(logging.INFO)

game_week = ''
managers = list()


def get_current_week():
    global game_week
    league_info = yf.get_league_info()
    game_week = int(league_info.current_week)


def assign_pos_values(player):
    """
    Takes Player object, returns value
    :param player: Player object
    :type player: yfpy.models.Player
    :return: Player value
    :rtype: float
    """
    pos_values = {
        'QB': 1,
        'RB': 1,
        'WR': 1,
        'TE': 1,
        'DEF': 1,
        'K': 1,
        'D': 0,
    }
    player_pos = player.primary_position
    # if player.is_undroppable == '1':
    #     return round(pos_values.get(player_pos) * 1.5, 1)
    # else:
    #     return pos_values.get(player_pos)
    return pos_values.get(player_pos)


def get_multiple_manager_rosters(manager_ids):
    """
    Returns multiple manager rosters in list of dictionaries

    :param manager_ids: team_id
    :type manager_ids: list
    :return: list of manager player dictionaries
    :rtype: list
    """
    rosters = list()
    for manager_id in manager_ids:
        try:
            roster_dict = get_manager_roster(manager_id=manager_id)
            rosters.append(roster_dict)
        except Exception as e:
            print("Error: {}".format(e))

    return rosters


def get_manager_roster(manager_id):
    """
    Returns manager roster dictionary.

    Ex: {
    'manager': 'Mark',
    'players', ['player1_dict',
                'player2_dict']
    }

    :param manager_id: team_id
    :type manager_id: int
    :return: manager roster dictionary
    :rtype: dict
    """
    global game_week
    global managers

    # Load roster info; returns a list of Player objects
    players = yf.get_team_roster_player_info_by_week(team_id=manager_id)
    manager_player_dict = dict()

    # Get manager name
    manager_name = get_manager_name(manager_id)
    managers.append(manager_name)
    manager_player_dict['manager'] = manager_name

    manager_player_list = list()
    for player in players:
        player = player['player']
        roster_pos = player.selected_position_value  # Position in team's roster
        if roster_pos not in ['BN', 'D']:
            player_value = assign_pos_values(player)
            player_dict = {
                'name': player.name.full,
                'team_name': player.editorial_team_full_name,
                'team_abbr': player.editorial_team_abbr,
                'pos': player.primary_position,
                'player_value': player_value,
            }
            manager_player_list.append(player_dict)
    manager_player_dict['players'] = manager_player_list
    return manager_player_dict


def get_manager_name(manager_id):
    """
    Returns manager name from a team object.

    :param manager_id: team_id
    :type team_obj: int
    :return: Manager's nickname
    :rtype: str
    """
    # Get yfpy.models.Team object
    manager_info = yf.get_team_info(team_id=manager_id)
    all_managers = manager_info.managers
    manager = all_managers['manager']
    manager_name = manager.nickname
    manager_name = manager_name.split(' ')[0]
    if manager_name == '--':
        manager_name = 'John'
    return manager_name


def get_weekly_schedule(week):
    """
    Return weekly schedule from SportRadar API.

    :param week: NFL schedule week
    :type week: int
    :return: List of game dictionaries
    :rtype: list
    """
    api_key = "8ud4engmjwxzk9gw7up653j8"
    SR_url = f'http://api.sportradar.us/nfl/official/trial/v6/en/games' \
             f'/2020/REG/{week}/schedule.json?api_key={api_key}'
    games = requests.get(SR_url).json()

    game_list = games['week']['games']
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
    """
    Assigns managers players to games by team.

    :param week_games: List of games from SportsRadar API
    :type week_games: list
    :param manager_player_list: List of players from each manager's roster
    :type manager_player_list: list
    :return: List of games with players assigned to them
    :rtype: list
    """
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


def sum_player_values(week_games: list) -> list:
    for week_game in week_games:
        total_value = list()
        for manager in managers:
            if week_game[manager]:
                player_list = week_game[manager]
                manager_value = sum(x['player_value'] for x in player_list)
                week_game[manager] = manager_value
                total_value.append(manager_value)
            else:
                week_game[manager] = 0
        week_game['Total'] = sum(total_value)
    return week_games


def sort_game_list(week_games):
    """
    Return list of weekly games sorted by game_time and total value.

    :param week_games: List of NFL game dictionaries
    :type week_games: list
    :return: Sorted list of SportsRadar games
    :rtype: list
    """
    return sorted(week_games, key=lambda k: (k['game_time'], -k['Total']))


def create_and_print_table(game_list):
    x = PrettyTable()
    first_fields = ['Game Time', 'Match', 'Channel']
    x.field_names = [*first_fields, *managers, 'Total']

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

    # print(x)
    return x.get_html_string()


def convert_to_markdown(html):
    return html2markdown.convert(html)


def send_with_pushbullet(body):
    access_token = 'o.jsROdhjhdzgGs6RBlEckp2dgifwU1Ke6'
    obj = Apprise.instantiate(f'pbul://{access_token}/?format=html')
    obj.notify(title='Schedule Breakdown', body=body)


def send_with_pushover(body):
    options = {
        'format': 'png',
        'crop-w': '400',
    }
    imgkit.from_string(body, 'out.jpg', options=options)

    PUSHOVER_USER_KEY = 'uJB6YmsCNkb76mhouohPmYwXDw54V6'
    PUSHOVER_TOKEN = 'astxh7puz1chu9yk3wtd2pqp6fjowy'
    pushover = get_notifier('pushover')
    pushover.notify(token=PUSHOVER_TOKEN, user=PUSHOVER_USER_KEY,
                    message='This week', title='Schedule Breakdown',
                    device='iPhone', attachment='out.jpg')


if __name__ == "__main__":
    # SETUP DATA
    auth_dir = "auth"
    league_id = "230376"
    game_id = "399"
    game_code = "nfl"
    all_output_as_json = False
    team_IDs = [3, 4]  # 3 = Mark, 4 = Lauren
    # team_IDs = range(1, 11)
    yf = YahooFantasySportsQuery(auth_dir=auth_dir,
                                 league_id=league_id,
                                 game_id=game_id,
                                 game_code=game_code,
                                 all_output_as_json=all_output_as_json)

    # Update game_week to current week
    get_current_week()

    # Assign players to current week's games
    weekly_games = assign_players_to_games(week_games=get_weekly_schedule(),
                                           manager_player_list=get_multiple_manager_rosters(team_IDs))

    # Sum player values by Manager
    weekly_games = sum_player_values(weekly_games)

    # Sort list of games by game_time ASC, values DESC
    sorted_weekly_games = sort_game_list(weekly_games)

    # Use PrettyTable to print table of game times
    html = create_and_print_table(sorted_weekly_games)
    print("HTML\n\n" + html)
    # markdown = html2markdown.convert(html)
    # print('MARKDOWN\n\n' + markdown)

    send_with_pushover(html)
