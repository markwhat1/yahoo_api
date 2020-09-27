import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import itertools


def ruwt_scraper(date, excitement, rating):
    URL = f'https://areyouwatchingthis.com/scores/{date}'

    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')

    ruwt_class = soup.find_all('li', attrs={'class': excitement})

    data = []
    data_dict = {}
    for i in ruwt_class:
        try:
            score1 = int(re.sub("\D", "", i.find_all('span', class_='score')[0].text))
        except IndexError:
            score1 = 0
        try:
            score2 = int(re.sub("\D", "", i.find_all('span', class_='score')[1].text))
        except IndexError:
            score2 = 0
        try:
            team1 = i.find_all('a', class_='team')[0].text.strip()
        except IndexError:
            team1 = i.find('a', class_='field').text.strip()
        try:
            team2 = i.find_all('a', class_='team')[1].text.strip()
        except IndexError:
            team2 = ''
        data_dict = {
            'sport': i.find('a', class_='sport').text.strip(),
            'team1': team1,
            'team2': team2,
            'score1': score1,
            'score2': score2,
            'score_diff': abs(score1 - score2),
            'score_sum': score1 + score2,
            'rating': rating
        }
        data.append(data_dict)

    df = pd.DataFrame(data)

    return df


def this_date_in_ruwt(date):
    df_severe = ruwt_scraper(date, 'severe', 1)
    df_high = ruwt_scraper(date, 'high', 1)
    df_elevated = ruwt_scraper(date, 'elevated', 0)
    df_guarded = ruwt_scraper(date, 'guarded', 0)
    pdList = [df_severe, df_high, df_elevated, df_guarded]
    df = pd.concat(pdList)

    df.to_csv(f'/Users/blakeduncan/Downloads/RUWT/{date}.csv', index=False)

    return df


date = []
for i in date:
    this_date_in_ruwt(i)



import pandas as pd
import glob

path = r'/Users/blakeduncan/Downloads/RUWT' # use your path
all_files = glob.glob(path + "/*.csv")

li = []

for filename in all_files:
    df = pd.read_csv(filename)
    li.append(df)

frame = pd.concat(li, axis=0, ignore_index=True)

frame.to_csv(f'/Users/blakeduncan/Downloads/RUWT.csv', index=False)

frame = frame['sport'].value_counts()
print(frame)
