import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import math

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def get_player_data(user_id):
    """Fetch player data from the GeoGuessr API."""
    try:
        user_info_url = f"https://www.geoguessr.com/api/v3/users/{user_id}"
        stats_url = f"https://www.geoguessr.com/api/v3/users/{user_id}/stats"

        # Retrieve user info and stats
        user_info = requests.get(user_info_url)
        stats_info = requests.get(stats_url)

        # Log the raw responses
        print(f"User Info Response for {user_id}: {user_info.text}")
        print(f"Stats Response for {user_id}: {stats_info.text}")

        # Check if the responses are successful
        user_info.raise_for_status()
        stats_info.raise_for_status()

        # Extract relevant data
        user_info_json = user_info.json()
        stats_info_json = stats_info.json()

        elo = user_info_json.get('competitive', {}).get('elo', 0)
        last_elo_change = user_info_json.get('competitive', {}).get('lastRatingChange', 0)
        level = user_info_json.get('progress', {}).get('level', 0)
        games_played = stats_info_json.get('gamesPlayed', 0)
        average_score = stats_info_json.get('averageGameScore', {}).get('amount', 0)

        return {
            "elo": elo,
            "last_elo_change": last_elo_change,
            "level": level,
            "games_played": games_played,
            "average_score": float(average_score) if isinstance(average_score, str) else average_score
        }
    except Exception as e:
        print(f"Error fetching data for user {user_id}: {e}")
        return None


def normalize_value(value, min_value, max_value):
    """Normalize a value to a range between 0 and 1."""
    if max_value == min_value:
        return 0
    return (value - min_value) / (max_value - min_value)

def log_normalize(value, max_value):
    """Log-normalize a value to account for diminishing returns."""
    return math.log(value + 1) / math.log(max_value + 1)

def calculate_player_score(elo, last_elo_change, level, games_played, average_score):
    """Calculate the player's score based on multiple factors."""
    normalized_elo = normalize_value(elo, 800, 2400)  # Example Elo range
    normalized_last_elo_change = normalize_value(last_elo_change, -100, 100)  # Hypothetical change range
    normalized_level = normalize_value(level, 1, 100)  # Level range
    log_normalized_games = log_normalize(games_played, 10000)  # Number of games range
    normalized_avg_score = normalize_value(average_score, 0, 25000)  # Example average score range

    # Weights for each factor
    w_elo = 0.5
    w_last_elo_change = 0.1
    w_level = 0.2
    w_games = 0.15
    w_avg_score = 0.05

    # Calculate weighted score
    score = (
        (w_elo * normalized_elo) +
        (w_last_elo_change * normalized_last_elo_change) +
        (w_level * normalized_level) +
        (w_games * log_normalized_games) +
        (w_avg_score * normalized_avg_score)
    )
    return score

def balance_teams(user_ids):
    """Fetch player data and calculate balanced teams."""
    players_data = []
    for user_id in user_ids:
        player_data = get_player_data(user_id)
        if player_data:
            # Calculate score for the player
            player_score = calculate_player_score(
                player_data['elo'],
                player_data['last_elo_change'],
                player_data['level'],
                player_data['games_played'],
                player_data['average_score']
            )
            players_data.append({"username": user_id, "score": player_score})

    # Sort players by score in descending order
    players_data.sort(key=lambda p: p['score'], reverse=True)

    # Zigzag assignment to balance teams
    team_a, team_b = [], []
    for i, player in enumerate(players_data):
        if i % 2 == 0:
            team_a.append(player)
        else:
            team_b.append(player)

    return {"team_a": team_a, "team_b": team_b}

@app.route('/balance-teams', methods=['POST'])
def balance_endpoint():
    data = request.get_json()
    if data and data.get("message") == "balance_teams":
        user_ids = data.get('user_ids', [])
        if not user_ids:
            return jsonify({'status': 'error', 'message': 'No user_ids provided'}), 400
        balanced_teams = balance_teams(user_ids)
        return jsonify(balanced_teams)
    else:
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400

if __name__ == '__main__':
    app.run(debug=True)
