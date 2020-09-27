import json
import requests

# An api key is emailed to you when you sign up to a plan
api_key = '3b925833a149188efe9324cc3433ed3c'

# First get a list of in-season sports
sports_response = requests.get('https://api.the-odds-api.com/v3/sports', params={
    'api_key': api_key
})

sports_json = json.loads(sports_response.text)

if not sports_json['success']:
    print(
        'There was a problem with the sports request:',
        sports_json['msg']
    )

else:
    print()
    print(
        'Successfully got {} sports'.format(len(sports_json['data'])),
        'Here\'s the list of sports:'
    )
    for sport in sports_json['data']:
        print(sport)
    # print(sports_json['data'][0])

# To get odds for a specific sport, use the sport key from the last request
#   or set sport to "upcoming" to see live and upcoming across all sports
sport_key = 'americanfootball_nfl'

odds_response = requests.get('https://api.the-odds-api.com/v3/odds', params={
    'api_key': api_key,
    'sport': sport_key,
    'region': 'us',  # uk | us | eu | au
    'mkt': 'h2h'  # h2h | spreads | totals
})

odds_json = json.loads(odds_response.text)
if not odds_json['success']:
    print(
        'There was a problem with the odds request:',
        odds_json['msg']
    )

else:
    # odds_json['data'] contains a list of live and
    #   upcoming events and odds for different bookmakers.
    # Events are ordered by start time (live events are first)
    print()
    print(
        'Successfully got {} events'.format(len(odds_json['data'])),
        'Here\'s the first event:'
    )
    print(odds_json['data'][1])
    totals = {'sport_key': 'americanfootball_nfl', 'sport_nice': 'NFL', 'teams': ['Buffalo Bills', 'New York Jets'],
              'commence_time': 1600016400, 'home_team': 'Buffalo Bills', 'sites': [
            {'site_key': 'unibet', 'site_nice': 'Unibet', 'last_update': 1599786194,
             'odds': {'totals': {'points': [39.5, 39.5], 'odds': [1.91, 1.91], 'position': ['over', 'under']}}},
            {'site_key': 'betonlineag', 'site_nice': 'BetOnline.ag', 'last_update': 1599786194,
             'odds': {'totals': {'points': [39.5, 39.5], 'odds': [1.92, 1.89], 'position': ['over', 'under']}}},
            {'site_key': 'lowvig', 'site_nice': 'LowVig.ag', 'last_update': 1599786179,
             'odds': {'totals': {'points': [39.5, 39.5], 'odds': [1.971, 1.935], 'position': ['over', 'under']}}},
            {'site_key': 'bookmaker', 'site_nice': 'Bookmaker', 'last_update': 1599786204,
             'odds': {'totals': {'position': ['over', 'under'], 'odds': [1.885, 1.935], 'points': [39.5, 39.5]}}},
            {'site_key': 'mybookieag', 'site_nice': 'MyBookie.ag', 'last_update': 1599785381,
             'odds': {'totals': {'points': ['39.5', '39.5'], 'odds': [1.91, 1.91], 'position': ['over', 'under']}}},
            {'site_key': 'draftkings', 'site_nice': 'DraftKings', 'last_update': 1599786208,
             'odds': {'totals': {'points': [39.5, 39.5], 'odds': [1.91, 1.91], 'position': ['over', 'under']}}},
            {'site_key': 'fanduel', 'site_nice': 'FanDuel', 'last_update': 1599786168,
             'odds': {'totals': {'points': [39.5, 39.5], 'odds': [1.91, 1.91], 'position': ['over', 'under']}}},
            {'site_key': 'intertops', 'site_nice': 'Intertops', 'last_update': 1599786200,
             'odds': {'totals': {'points': [39.5, 39.5], 'odds': [1.9091, 1.9091], 'position': ['over', 'under']}}},
            {'site_key': 'williamhill_us', 'site_nice': 'William Hill (US)', 'last_update': 1599786197,
             'odds': {'totals': {'points': [39.5, 39.5], 'odds': [1.91, 1.91], 'position': ['over', 'under']}}},
            {'site_key': 'betrivers', 'site_nice': 'BetRivers', 'last_update': 1599786212,
             'odds': {'totals': {'points': ['39.5', '39.5'], 'odds': [1.91, 1.91], 'position': ['over', 'under']}}},
            {'site_key': 'bovada', 'site_nice': 'Bovada', 'last_update': 1599786188, 'odds': {
                'totals': {'points': [39.5, 39.5], 'odds': [1.909091, 1.909091], 'position': ['over', 'under']}}}],
              'sites_count': 11}
    spreads = {'sport_key': 'americanfootball_nfl', 'sport_nice': 'NFL', 'teams': ['Buffalo Bills', 'New York Jets'],
               'commence_time': 1600016400, 'home_team': 'Buffalo Bills', 'sites': [
            {'site_key': 'unibet', 'site_nice': 'Unibet', 'last_update': 1599786238,
             'odds': {'spreads': {'odds': [1.91, 1.91], 'points': ['-6.5', '6.5']}}},
            {'site_key': 'betonlineag', 'site_nice': 'BetOnline.ag', 'last_update': 1599786240,
             'odds': {'spreads': {'odds': [1.87, 1.95], 'points': ['-6.5', '6.5']}}},
            {'site_key': 'lowvig', 'site_nice': 'LowVig.ag', 'last_update': 1599786225,
             'odds': {'spreads': {'odds': [1.909, 2.0], 'points': ['-6.5', '6.5']}}},
            {'site_key': 'pointsbetus', 'site_nice': 'PointsBet (US)', 'last_update': 1599786235,
             'odds': {'spreads': {'odds': [1.91, 1.91], 'points': ['-6.5', '6.5']}}},
            {'site_key': 'gtbets', 'site_nice': 'GTbets', 'last_update': 1599786207,
             'odds': {'spreads': {'odds': [1.877, 1.962], 'points': ['-6.5', '6.5']}}},
            {'site_key': 'mybookieag', 'site_nice': 'MyBookie.ag', 'last_update': 1599785381,
             'odds': {'spreads': {'odds': [1.87, 1.95], 'points': ['-6.5', '6.5']}}},
            {'site_key': 'draftkings', 'site_nice': 'DraftKings', 'last_update': 1599786208,
             'odds': {'spreads': {'odds': [1.91, 1.91], 'points': ['-6.5', '6.5']}}},
            {'site_key': 'fanduel', 'site_nice': 'FanDuel', 'last_update': 1599786214,
             'odds': {'spreads': {'odds': [1.83, 2.0], 'points': ['-6.5', '6.5']}}},
            {'site_key': 'intertops', 'site_nice': 'Intertops', 'last_update': 1599786250,
             'odds': {'spreads': {'odds': [1.8696, 1.9524], 'points': ['-6.50', '6.50']}}},
            {'site_key': 'williamhill_us', 'site_nice': 'William Hill (US)', 'last_update': 1599786241,
             'odds': {'spreads': {'odds': [1.87, 1.95], 'points': ['-6.5', '6.5']}}},
            {'site_key': 'betrivers', 'site_nice': 'BetRivers', 'last_update': 1599786212,
             'odds': {'spreads': {'odds': [1.91, 1.91], 'points': ['-6.5', '6.5']}}},
            {'site_key': 'bovada', 'site_nice': 'Bovada', 'last_update': 1599786234,
             'odds': {'spreads': {'odds': [1.87, 1.952381], 'points': ['-6.5', '6.5']}}}], 'sites_count': 12}

    h2h = {'sport_key': 'americanfootball_nfl', 'sport_nice': 'NFL', 'teams': ['Buffalo Bills', 'New York Jets'],
           'commence_time': 1600016400, 'home_team': 'Buffalo Bills', 'sites': [
            {'site_key': 'unibet', 'site_nice': 'Unibet', 'last_update': 1599786762, 'odds': {'h2h': [1.35, 3.25]}},
            {'site_key': 'betonlineag', 'site_nice': 'BetOnline.ag', 'last_update': 1599786779,
             'odds': {'h2h': [1.33, 3.5]}},
            {'site_key': 'lowvig', 'site_nice': 'LowVig.ag', 'last_update': 1599786774, 'odds': {'h2h': [1.33, 3.5]}},
            {'site_key': 'pointsbetus', 'site_nice': 'PointsBet (US)', 'last_update': 1599786774,
             'odds': {'h2h': [1.33, 3.4]}},
            {'site_key': 'gtbets', 'site_nice': 'GTbets', 'last_update': 1599786760, 'odds': {'h2h': [1.32, 3.55]}},
            {'site_key': 'bookmaker', 'site_nice': 'Bookmaker', 'last_update': 1599786769,
             'odds': {'h2h': [1.34, 3.43]}}, {'site_key': 'betfair', 'site_nice': 'Betfair', 'last_update': 1599786763,
                                              'odds': {'h2h': [1.38, 3.5], 'h2h_lay': [1.4, 3.65]}},
            {'site_key': 'draftkings', 'site_nice': 'DraftKings', 'last_update': 1599786761,
             'odds': {'h2h': [1.35, 3.25]}},
            {'site_key': 'fanduel', 'site_nice': 'FanDuel', 'last_update': 1599786751, 'odds': {'h2h': [1.33, 3.45]}},
            {'site_key': 'intertops', 'site_nice': 'Intertops', 'last_update': 1599786746,
             'odds': {'h2h': [1.36, 3.4]}},
            {'site_key': 'williamhill_us', 'site_nice': 'William Hill (US)', 'last_update': 1599786770,
             'odds': {'h2h': [1.33, 3.5]}},
            {'site_key': 'betrivers', 'site_nice': 'BetRivers', 'last_update': 1599786747,
             'odds': {'h2h': [1.35, 3.25]}},
            {'site_key': 'bovada', 'site_nice': 'Bovada', 'last_update': 1599786774, 'odds': {'h2h': [1.33, 3.5]}}],
           'sites_count': 13}

# Check your usage
print()
print('Remaining requests', odds_response.headers['x-requests-remaining'])
print('Used requests', odds_response.headers['x-requests-used'])


class TheOddsApi:

    def __init__(self):
        self.key = "2b6c4ce43498af94d0d6145c964a91b4"
        self.base_url = 'https://api.the-odds-api.com/v3/sports'
        self.remaining_requests = None

    def get_sports(self):
        # First get a list of in-season sports
        sports_response = requests.get(self.base_url, params={
            'api_key': self.key
        })

        sports_json = json.loads(sports_response.text)

        if not sports_json['success']:
            print(
                'There was a problem with the sports request:',
                sports_json['msg']
            )

        else:
            print()
            print(
                'Successfully got {} sports'.format(len(sports_json['data'])),
                'Here\'s the first sport:'
            )
            print(sports_json['data'][0])
            self.remaining_requests = sports_response.headers['x-requests-remaining']

        return sports_json
