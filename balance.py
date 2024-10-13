import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_player_data(user_id):
    """
    Fetch relevant player data from the GeoGuessr API.

    Parameters
    ----------
    user_id : str
        The user ID to fetch data for.

    Returns
    -------
    dict
        A dictionary containing the player's Elo, last Elo change, level, number of games played, and average score.
        If there is an error fetching the data, returns None.
    """
    try:
        user_info_url = f"https://www.geoguessr.com/api/v3/users/{user_id}"
        stats_url = f"https://www.geoguessr.com/api/v3/users/{user_id}/stats"

        # Retrieve user info
        user_info = requests.get(user_info_url).json()
        stats_info = requests.get(stats_url).json()

        # Extract relevant data
        elo = user_info.get('rating', 0)
        last_elo_change = user_info.get('lastEloChange', 0)
        level = user_info.get('level', 0)
        games_played = stats_info.get('gamesPlayed', 0)
        average_score = stats_info.get('averageScore', 0)

        return {
            "elo": elo,
            "last_elo_change": last_elo_change,
            "level": level,
            "games_played": games_played,
            "average_score": average_score
        }
    except Exception as e:
        print(f"Error fetching data for user {user_id}: {e}")
        return None

def normalize_value(value, min_value, max_value):
    """Normalize a value to a range between 0 and 1."""
    if max_value == min_value:
        return 0
    return (value - min_value) / (max_value - min_value)

def calculate_player_score(elo, last_elo_change, level, games_played, average_score):
    # Normalize the values based on hypothetical ranges for GeoGuessr
    """
    Calculate a score for a player based on their GeoGuessr statistics.

    The score is a weighted sum of normalized values for Elo, last Elo change, level, number of games played, and average score.

    The weights are (in order): 0.4, 0.1, 0.2, 0.2, 0.1.

    Returns a score between 0 and 1, where 1 is the highest possible score.
    """
    normalized_elo = normalize_value(elo, 800, 2400)  # Example Elo range
    normalized_last_elo_change = normalize_value(last_elo_change, -100, 100)  # Hypothetical change range
    normalized_level = normalize_value(level, 1, 100)  # Level range
    normalized_games_played = normalize_value(games_played, 10, 1000)  # Number of games range
    normalized_avg_score = normalize_value(average_score, 0, 5000)  # Example average score range

    # Weighted sum for the overall score
    score = (
        (normalized_elo * 0.4) +
        (normalized_last_elo_change * 0.1) +
        (normalized_level * 0.2) +
        (normalized_games_played * 0.2) +
        (normalized_avg_score * 0.1)
    )
    return score

def balance_teams(usernames):
    """
    Balance a list of usernames into two teams based on their GeoGuessr
    statistics.

    The algorithm works as follows:

    1. For each username, fetch the relevant player data from the
       GeoGuessr API.
    2. Calculate a score for each player based on their Elo, level,
       number of games played, and average score.
    3. Sort the players by score in descending order.
    4. Alternate assignment to two teams (Team A and Team B).

    The return value is a dictionary with the keys "Team A" and "Team B"
    containing the usernames for each team.
    """
    players_data = []
    for username in usernames:
        player_data = get_player_data(username)
        if player_data:
            # Calculate score for the player
            player_score = calculate_player_score(
                player_data['elo'],
                player_data['last_elo_change'],
                player_data['level'],
                player_data['games_played'],
                player_data['average_score']
            )
            players_data.append({"username": username, "score": player_score})

    # Sort players by score
    players_data.sort(key=lambda x: x['score'], reverse=True)

    # Alternate assignment to two teams
    team_a, team_b = [], []
    for i, player in enumerate(players_data):
        if i % 2 == 0:
            team_a.append(player['username'])
        else:
            team_b.append(player['username'])

    # Output the teams
    return {"Team A": team_a, "Team B": team_b}

@app.route('/usernames', methods=['POST'])
def get_usernames():
    """
    Handles POST requests to /usernames with a JSON body containing a single
    key-value pair: "usernames": [username1, username2, ...]. The function
    returns a JSON response with two keys: "Team A" and "Team B", each containing
    a list of usernames. The algorithm for balancing the teams is described in
    the balance_teams function.
    """
    data = request.json
    usernames = data['usernames']
    teams = balance_teams(usernames)
    return jsonify(teams)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
