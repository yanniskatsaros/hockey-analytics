import sqlite3

def create_tables(database_name):
    """
    Builds all table structure in a new SQLite3 database
    """
    if not isinstance(database_name, str):
        raise TypeError("Database name must be a string.")

    if not '.' in database_name:
        # define extension
        database_name += '.db'

    # define table structure
    create_statement = """
    CREATE TABLE IF NOT EXISTS players (
        player_id INT PRIMARY KEY,
        first_name VARCHAR,
        last_name VARCHAR,
        nhl_api_link VARCHAR,
        position VARCHAR,
        jersey_number INT,
        birth_date DATE,
        nationality VARCHAR,
        height FLOAT,
        weight FLOAT,
        shoots_catches VARCHAR
    );

    CREATE TABLE IF NOT EXISTS teams (
        team_id INT PRIMARY KEY,
        team_name VARCHAR,
        nhl_api_link VARCHAR,
        abbreviation VARCHAR
    );

    CREATE TABLE IF NOT EXISTS officials (
        official_id INT PRIMARY KEY,
        official_name VARCHAR,
        official_type VARCHAR,
        nhl_api_link VARCHAR
    );

    CREATE TABLE IF NOT EXISTS games (
        game_id INT PRIMARY KEY,
        start_datetime DATETIME,
        end_datetime DATETIME,
        gmt_offset INT,
        home_team_id INT,
        away_team_id INT,
        official_1_id INT,
        official_2_id INT,
        official_3_id INT,
        official_4_id INT,
        FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
        FOREIGN KEY (away_team_id) REFERENCES teams(team_id),
        FOREIGN KEY (official_1_id) REFERENCES officials(official_id),
        FOREIGN KEY (official_2_id) REFERENCES officials(official_id),
        FOREIGN KEY (official_3_id) REFERENCES officials(official_id),
        FOREIGN KEY (official_4_id) REFERENCES officials(official_id)
    );

    CREATE TABLE IF NOT EXISTS plays (
        game_id INT PRIMARY KEY,
        period INT,
        time_elapsed VARCHAR,
        home_players_on_ice INT,
        away_players_on_ice INT,
        play_type VARCHAR,
        play_coordinate_x INT,
        play_coordinate_y INT,
        player_1_id INT,
        player_2_id INT,
        home_player_1_id INT,
        home_player_2_id INT,
        home_player_3_id INT,
        home_player_4_id INT,
        home_player_5_id INT,
        home_player_6_id INT,
        away_player_1_id INT,
        away_player_2_id INT,
        away_player_3_id INT,
        away_player_4_id INT,
        away_player_5_id INT,
        away_player_6_id INT,
        FOREIGN KEY (player_1_id) REFERENCES players(player_id),
        FOREIGN KEY (player_2_id) REFERENCES players(player_id),
        FOREIGN KEY (home_player_1_id) REFERENCES players(player_id),
        FOREIGN KEY (home_player_2_id) REFERENCES players(player_id),
        FOREIGN KEY (home_player_3_id) REFERENCES players(player_id),
        FOREIGN KEY (home_player_4_id) REFERENCES players(player_id),
        FOREIGN KEY (home_player_5_id) REFERENCES players(player_id),
        FOREIGN KEY (home_player_6_id) REFERENCES players(player_id),
        FOREIGN KEY (away_player_1_id) REFERENCES players(player_id),
        FOREIGN KEY (away_player_2_id) REFERENCES players(player_id),
        FOREIGN KEY (away_player_3_id) REFERENCES players(player_id),
        FOREIGN KEY (away_player_4_id) REFERENCES players(player_id),
        FOREIGN KEY (away_player_5_id) REFERENCES players(player_id),
        FOREIGN KEY (away_player_6_id) REFERENCES players(player_id)
    );
    """

    with sqlite3.connect(database_name) as conn:
        cursor = conn.cursor()
        cursor.execute(create_statement)

    return
