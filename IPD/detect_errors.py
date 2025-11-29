import re
import json
from typing import Union, Optional, Set, Tuple
from datetime import datetime

import polars as pl
import pandas as pd


def detect_player_errors(df: pl.DataFrame, start_date: Optional[Union[str, datetime]]=None, end_date: Optional[Union[str, datetime]]=None) -> Set[Tuple[str, int, int]]:
    """
    Reads a CSV file and detects which players generated errors in their observations.

    Args:
        df (pl.DataFrame): a polars DataFrame
        start_date (Union[str, datetime]): Optional start date filter (string in format 'YYYY-MM-DD' or datetime)
        end_date (Union[str, datetime]): Optional end date filter (string in format 'YYYY-MM-DD' or datetime)

    Returns:
        Set[str, int, int]: A set of tuples containing (date, game_id, player_id) for games with errors.
    """
    errors = []

    for row in df.iter_rows(named=True):
        game_id = row.get('game_id')
        observations = row.get('observations')

        # Try to parse observations as JSON
        try:
            obs_data = json.loads(observations)
        except json.JSONDecodeError:
            # If it's not valid JSON, try to find errors using regex
            player_errors = find_errors_in_text(observations)
            for player_id in player_errors:
                errors.append((game_id, player_id))
            continue

        # If observations is a dict, check for errors
        if isinstance(obs_data, dict):
            game_in_date_range = False

            for timestamp, content in obs_data.items():
                # Check if timestamp is within date range
                if start_date or end_date:
                    if not is_timestamp_in_range(timestamp, start_date, end_date):
                        continue
                    game_in_date_range = True
                else:
                    game_in_date_range = True

                if isinstance(content, dict) and 'observation' in content:
                    obs_text = content['observation']
                    player_errors = find_errors_in_text(obs_text)
                    for player_id in player_errors:
                        errors.append((timestamp.split(" ")[0], game_id, player_id))

            # Skip this game if no timestamps matched the date range
            if (start_date or end_date) and not game_in_date_range:
                continue

    return set(errors)  # remove duplicates


def find_errors_in_text(text: str) -> Set[int]:
    """
    Extracts player IDs that generated errors from observation text.

    Looks for the "[0] [An error occurred:" to identify which player had an error.

    Args:
        text (str): The observation text to search

    Returns:
        Set[int]: Set of player IDs (integers) that generated errors
    """
    player_errors = set()

    # Pattern to match "[player_id] [An error occurred:"
    pattern = r'\[(\d+)\]\s*\[An error occurred:'
    matches = re.finditer(pattern, text)

    for match in matches:
        player_id = int(match.group(1))
        player_errors.add(player_id)

    return player_errors


def is_timestamp_in_range(timestamp: Union[str, datetime], start_date: Optional[Union[str, datetime]] =None, end_date: Optional[Union[str, datetime]]=None) -> bool:
    """
    Checks if a timestamp falls within the specified date range.

    Args:
        timestamp (Union[str, datetime]): Timestamp string (e.g., '2025-08-18 02:22:29.7802+00')
        start_date (Union[str, datetime]): Start date (string in 'YYYY-MM-DD' format or datetime object)
        end_date (Union[str, datetime]): End date (string in 'YYYY-MM-DD' format or datetime object)

    Returns:
        bool: Boolean indicating if timestamp is in range
    """
    try:
        ts = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        ts_date = ts.date()

        if start_date:
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if ts_date < start_date:
                return False

        if end_date:
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            if ts_date > end_date:
                return False
        return True
    except (ValueError, AttributeError):
        # If timestamp parsing fails, include it by default
        return True


def main():
    path = r'hf://datasets/bobbycxy/mgc2025-threeplayeripd/threeplayeripd.parquet'
    df = pl.read_parquet(path) if path.endswith('.parquet') else pl.read_csv(path)

    # Filter by date range to select phase 2 (use None to skip filtering)
    start_date = None  # e.g., '2025-08-01'
    end_date = None  # e.g., '2025-08-20'

    errors = detect_player_errors(df, start_date, end_date)
    pd.DataFrame(errors, columns=["date", "game_id", "player"]).to_csv(r"./detected_errors.csv")

    if errors:
        print(f"Found {len(errors)} error(s):\n")
        for timestamp, game_id, player_id in errors:
            print(f"Timestamp: {timestamp}, Game ID: {game_id}, Player: {player_id}")
    else:
        print("No errors detected.")


if __name__ == '__main__':
    main()