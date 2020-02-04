import re
from bs4 import BeautifulSoup
import requests
import pandas as pd
from dateutil.parser import parse
from pytz import timezone
from typing import Tuple, List

def _get_api_plays(year : int, season : str, game_number : int) -> str:
    """
    Parameters 
    ----------
    year : int
        The season starting year of the game
        Example: 2018 (for the 2018-2019 season)

    season : str
        The season "flag"; must be one of
        {'pre', 'regular', 'post', 'all-star'}

    game_number : int
        The game number. Valid range:
            * 1 - 1271 (pre year 2020)
            * 1 - 1312 (post year 2020; with the addition of Seattle Hockey Team)
    
    Returns
    -------
    str
        The data as a JSON text format
    """
    # input error-checking
    if year < 1917:
        raise ValueError('Year must be > 1917!')
    
    seasons = {'pre', 'regular', 'post', 'all-star'}
    if season not in seasons:
        raise ValueError(f'Season must be one of : {seasons}')
    
    if (game_number < 0) or (game_number > 1313):
        raise ValueError('Game ID must be between 0 - 1312')

    # season is actually an integer in the API
    season_dict = {
        'pre' : '01',
        'regular' : '02',
        'post' : '03',
        'all-star' : '04'
    }
    season : str = season_dict.get(season)

    # game id is needed for the URL in the API
    game_id = f'{year}{season}{str(game_number).zfill(4)}'
    url = f'https://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live'
    json : str = requests.get(url).json()

    return json



def _parse_api_plays(json : str) -> pd.DataFrame:
    """
    Parameters
    ----------
    json : str
        A JSON text of the play-by-play data

    Returns
    -------
    pd.DataFrame
        A dataframe of the parsed JSON
    """ 
    # get list of all plays from the game
    play_list = json.get('liveData').get('plays').get('allPlays')

    get_date_obj : datetime = parse(json.get('gameData').get('datetime').get('dateTime'))
    date_central : datetime = get_date_obj.astimezone(timezone('US/Central'))
    game_date : str = date_central.strftime('%Y-%m-%d')

    # get game information that does not change by play
    game_id = json.get('gameData').get('game').get('pk')
    visiting_team_id = json.get('gameData').get('teams').get('away').get('id')
    visiting_team_code = json.get('gameData').get('teams').get('away').get('triCode')
    home_team_id = json.get('gameData').get('teams').get('home').get('id')
    home_team_code = json.get('gameData').get('teams').get('home').get('triCode')

    plays = {
        'game_id' : [],
        'game_date' : [],
        'away_team_id' : [],
        'away_team_code' : [],
        'home_team_id' : [],
        'home_team_code' : [],
        'event_id' : [],
        'play_type' : [],
        'play_type_id' : [],
        'play_description' : [],
        'period' : [],
        'time_elapsed' : [],
        'time_remaining' : [],
        'player1_id' : [],
        'player1_name' : [],
        'player2_id' : [],
        'player2_name' : []
    }

    for play in play_list:
        plays['game_id'].append(game_id)
        plays['game_date'].append(game_date)
        plays["away_team_id"].append(visiting_team_id)
        plays["away_team_code"].append(visiting_team_code)
        plays["home_team_id"].append(home_team_id)
        plays["home_team_code"].append(home_team_code)
        plays['event_id'].append(play.get('about').get('eventId'))
        plays['play_type'].append(play.get('result').get('event'))
        plays['play_type_id'].append(play.get('result').get('eventTypeId'))
        plays['play_description'].append(play.get('result').get('description'))
        plays['period'].append(play.get('about').get('period'))
        plays['time_elapsed'].append(play.get('about').get('periodTime'))
        plays['time_remaining'].append(play.get('about').get('periodTimeRemaining'))
        
        if play.get('players') is None:
            # add None type to the list to make all the lists the same length for the Pandas conversion to DataFrame
            plays['player1_id'].append(None)
            plays['player1_name'].append(None)
            plays['player2_id'].append(None)
            plays['player2_name'].append(None)
        else:
            # add Player 1 info
            player1 = play.get('players')[0]
            plays['player1_id'].append(player1.get('player').get('id'))
            plays['player1_name'].append(player1.get('player').get('fullName'))
            
            # check if there is a second player in the play, if not add None type to the list
            if len(play.get('players')) == 2:
                player2 = play.get('players')[1]
                plays['player2_id'].append(player2.get('player').get('id'))
                plays['player2_name'].append(player2.get('player').get('fullName'))            
            else:
                plays['player2_id'].append(None)
                plays['player2_name'].append(None)        
        
    return pd.DataFrame(plays)


def _get_players_on_ice(year : int, season : str, game_number : int) -> Tuple[str]:
    """
    Parameters 
    ----------
    year : int
        The season starting year of the game
        Example: 2018 (for the 2018-2019 season)

    season : str
        The season "flag"; must be one of
        {'pre', 'regular', 'post', 'all-star'}

    game_number : int
        The game number. Valid range:
            * 1 - 1271 (pre year 2020)
            * 1 - 1312 (post year 2020; with the addition of Seattle Hockey Team)
    
    Returns
    -------
    str
        The data in HTML text format
    """
    # input error-checking
    if year < 1917:
        raise ValueError('Year must be > 1917!')
    
    seasons = {'pre', 'regular', 'post', 'all-star'}
    if season not in seasons:
        raise ValueError(f'Season must be one of : {seasons}')
    
    if (game_number < 0) or (game_number > 1313):
        raise ValueError('Game ID must be between 0 - 1312')

    # season is actually an integer in the API
    season_dict = {
        'pre' : '01',
        'regular' : '02',
        'post' : '03',
        'all-star' : '04'
    }
    season : str = season_dict.get(season)

    # the URL requires year as 20182019 for example
    year_id : str = f'{year}{int(year) + 1}'    
    game_id : str = f'{season}{str(game_number).zfill(4)}'

    url = f'http://www.nhl.com/scores/htmlreports/{year_id}/PL{game_id}.HTM'
    response = requests.get(url)

    return response.text, year, game_id


def _parse_players_on_ice(html : str, year : int, game_id : str) -> pd.DataFrame:
    """
    Parameters
    ----------
    html : str
        An HTML text of the play-by-play data
    
    year : int
        The season starting year of the game
        Example: 2018 (for the 2018-2019 season)
    
    game_id : str
        The id for the game, which is a combination
        of the season id and game id

    Returns
    -------
    pd.DataFrame
        A dataframe of the parsed HTML
    """
    soup = BeautifulSoup(html, 'lxml')
    # trs - table rows in an HTML table
    trs = soup.find_all('tr', class_='evenColor')
    # set up dictionary to hold data lists before converting to Pandas dataframe
    play_by_play_data = {
        'event_id' : [],
        'period' : [],
        'strength' : [],
        'time_elapsed' : [],
        'time_remaining' : [],
        'play_type' : [],
        'play_description' : [],
        'away_on_ice' : [],
        'home_on_ice' : []
    }

    # create keys for HTML table data locations
    key_lookup = {
        1 : 'event_id',
        3 : 'period',
        5 : 'strength',
        7 : 'time_elapsed',
        8 : 'time_remaining',
        9 : 'play_type',
        11 : 'play_description',
        13 : 'away_on_ice',
        15 : 'home_on_ice'
    }

    # create lookup table for plays to match the NHL API data
    play_lookup = {
        'FAC' : 'FACEOFF',
        'GIVE' : 'GIVEAWAY',
        'TAKE' : 'TAKEAWAY',
        'HIT' : 'HIT',
        'SHOT' : 'SHOT',
        'MISS' : 'MISSED_SHOT',
        'STOP' : 'STOP',
        'BLOCK' : 'BLOCKED_SHOT',
        'GOAL' : 'GOAL',
        'PENL' : 'PENALTY',
        'PEND' : 'PERIOD_END',
        'PSTR' : 'PERIOD_START',
        'GEND' : 'GAME_END'
    }

    # scrape data from HTML table
    pattern = r'\n+'
    for row in trs[4:]:
        for i, cell in enumerate(row):     
            if i in (1, 3, 5, 9, 11, 13, 15):
                text = cell.text.replace('\xa0', ' ')
                text = re.sub(pattern, '', text)
                
                key = key_lookup.get(i)
                play_by_play_data[key].append(text)

    # scrape time elapsed data from HTML table separately
    # we need to do this because the time elapsed & time
    # remaining columns get merged into one during the scrape
    for row in trs[4:]:
        for i, cell in enumerate(row):     
            if i == 7:
                text = cell.text.replace('\xa0', ' ')
                text = re.sub(pattern, '', text)
                
                delimiter = cell.text.find(':') + 3
                text_expired = cell.text[0:delimiter].zfill(5)
                text_remaining = cell.text[delimiter:].zfill(5)

                key_expired = key_lookup.get(i)
                key_remaining = key_lookup.get(i + 1)
                play_by_play_data[key_expired].append(text_expired)
                play_by_play_data[key_remaining].append(text_remaining)

    # convert data to Pandas dataframe
    plays_scrape = pd.DataFrame(play_by_play_data)

    # split home on ice column into individual columns
    home_on_ice = ( plays_scrape['home_on_ice']
                    .str.strip()
                    .str.replace('[aA-zZ]', '')
                    .str.split(' ', expand=True) )
    home_cols = ['home_1', 'home_2', 'home_3', 'home_4', 'home_5', 'home_6']
    home_on_ice.columns = home_cols

    # split away on ice column into individual columns
    away_on_ice = ( plays_scrape['away_on_ice']
                    .str.strip()
                    .str.replace('[aA-zZ]', '')
                    .str.split(' ', expand=True) )
    away_cols = ['away_1', 'away_2', 'away_3', 'away_4', 'away_5', 'away_6']
    away_on_ice.columns = away_cols

    # add the on ice player columns
    plays_scrape[away_cols] = away_on_ice
    plays_scrape[home_cols] = home_on_ice

    # add game id to the df
    plays_scrape['game_id'] = game_id

    plays_scrape['play_type_id'] = plays_scrape['play_type'].map(play_lookup)

    # reorder columns
    cols = ['game_id',
            'event_id',
            'period',
            'strength',
            'time_elapsed',
            'time_remaining',
            'play_type',
            'play_type_id',
            'play_description',
            'away_on_ice',
            'home_on_ice',
            'away_1','away_2','away_3','away_4','away_5','away_6',
            'home_1','home_2','home_3','home_4','home_5','home_6']
    plays_scrape = plays_scrape[cols]
    plays_scrape['period'] = pd.to_numeric(plays_scrape['period'])

    # get roster data to convert jersey numbers to player_id
    # create dictionary to convert season from numerical index
    # back to human-friendly index
    season_dict = {
        '01' : 'pre',
        '02' : 'regular',
        '03' : 'post',
        '04' : 'all-star'
    }
    # get season number from game_id then convert using season_dict
    season = game_id[:2]
    season : str = season_dict.get(season)
    game_number = int(game_id[2:])
    
    # pull roster data to get player IDs to add to dataframe
    roster_data = get_roster(year, season, game_number)

    # add player ID to dataframe
    # create dictionary to add player IDs
    roster_data['player_guid'] = roster_data['home_away'] + roster_data['jersey_number']
    player_dict = roster_data.set_index('player_guid').to_dict()['player_id']

    # create guid columns for scraped data
    plays_scrape.update(plays_scrape.loc[:,'away_1':'away_6'].apply(lambda x: 'away' + x))
    plays_scrape.update(plays_scrape.loc[:,'home_1':'home_6'].apply(lambda x: 'home' + x))

    # update scraped data with player IDs
    plays_scrape.update(plays_scrape.loc[:,'away_1':'away_6'].replace(player_dict))
    plays_scrape.update(plays_scrape.loc[:,'home_1':'home_6'].replace(player_dict))

    return plays_scrape


def get_roster(year : int, season : str, game_number : int) -> pd.DataFrame:
    """
    Parameters 
    ----------
    year : int
        The season starting year of the game
        Example: 2018 (for the 2018-2019 season)

    season : str
        The season "flag"; must be one of
        {'pre', 'regular', 'post', 'all-star'}

    game_number : int
        The game number. Valid range:
            * 1 - 1271 (pre year 2020)
            * 1 - 1312 (post year 2020; with the addition of Seattle Hockey Team)
    
    Returns
    -------
    pd.DataFrame
        The data as a pandas DataFrame
    """
    # input error-checking
    if year < 1917:
        raise ValueError('Year must be > 1917!')
    
    seasons = {'pre', 'regular', 'post', 'all-star'}
    if season not in seasons:
        raise ValueError(f'Season must be one of : {seasons}')
    
    if (game_number < 0) or (game_number > 1313):
        raise ValueError('Game ID must be between 0 - 1312')

    # season is actually an integer in the API
    season_dict = {
        'pre' : '01',
        'regular' : '02',
        'post' : '03',
        'all-star' : '04'
    }
    season : str = season_dict.get(season)

    # game id is needed for the URL in the API
    game_id = f'{year}{season}{str(game_number).zfill(4)}'
    url = f'https://statsapi.web.nhl.com/api/v1/game/{game_id}/boxscore'
    json : str = requests.get(url).json()

    teams_list : List[str] = json.get('teams')
    players = {
        'home_away' : [],
        'team_id' : [],
        'player_id' : [],
        'player_name' : [],
        'player_position' : [],
        'jersey_number' : []
    }

    for team in teams_list:
        for player in teams_list.get(team).get('players'):
            players['home_away'].append(team)
            (players['team_id']
                .append(teams_list
                    .get(team)
                    .get('team')
                    .get('id')))
            players['player_id'].append(player)
            (players['player_name']
                .append(teams_list
                    .get(team)
                    .get('players')
                    .get(player)
                    .get('person')
                    .get('fullName')))
            (players['player_position']
                .append(teams_list
                    .get(team)
                    .get('players')
                    .get(player)
                    .get('position')
                    .get('abbreviation')))
            (players['jersey_number']
                .append(teams_list
                    .get(team)
                    .get('players')
                    .get(player)
                    .get('jerseyNumber')))
        
    players = pd.DataFrame(players)
    return players


def _combine_api_scrape_data(api_df : pd.DataFrame, scrape_df : pd.DataFrame, year : int) -> pd.DataFrame:
    """
    Parameters 
    ----------
    api_df : DataFrame
        A Pandas DataFrame constructed using the
        _parse_api_plays() method

    scrape_df : DataFrame
        A Pandas DataFrame constructed using the
        _parse_players_on_ice() method
        {'pre', 'regular', 'post', 'all-star'}
    
    year : int
        The season starting year of the game
        Example: 2018 (for the 2018-2019 season)
        
    Returns
    -------
    pd.DataFrame
        The combined data as a pandas DataFrame
    """
    # create updated game_id in scrape_df to match
    # the game_id column in api_df
    scrape_df['game_id'] = (str(year) + scrape_df['game_id']).astype(int)

    # create list of play types to filter out
    filter_plays = [
        'GAME_SCHEDULED',
        'PERIOD_READY',
        'PERIOD_START',
        'PERIOD_END',
        'PERIOD_OFFICIAL',
        'GAME_END',
        'PENALTY',
        'STOP'
        ]

    # filter out unnecessary plays from both dfs
    # we need to filter these out since they don't take time off
    # the clock & it will mess up the join
    api_df = api_df[~api_df['play_type_id'].isin(filter_plays)]
    scrape_df = scrape_df[~scrape_df['play_type_id'].isin(filter_plays)]

    # create list of columns to keep in scrape_df
    scrape_cols = [
        'game_id',
        'period',
        'time_elapsed',
        'away_1','away_2','away_3','away_4','away_5','away_6',
        'home_1','home_2','home_3','home_4','home_5','home_6'
    ]

    # filter out un-needed columns
    scrape_df = scrape_df[scrape_cols]

    # join the dataframes together
    combined_df = pd.merge(left=api_df, right= scrape_df, on = ['game_id', 'period', 'time_elapsed'])
    
    return combined_df

# TODO formalize functions to match SQL tables' column names

if __name__ == "__main__":
