#!/usr/bin/env python3
"""
Deep inspection of the Secret Mafia data structure
"""

from datasets import load_dataset
import pandas as pd
import json

print("Loading dataset...")
dataset = load_dataset("bobbycxy/mgc2025-secretmafia")
df = pd.DataFrame(dataset['train'])

print("\n" + "="*80)
print("DATASET SCHEMA")
print("="*80)
print("\nColumns and their types:")
for col in df.columns:
    print(f"  {col:20s} : {df[col].dtype}")
    print(f"    Sample value: {str(df[col].iloc[0])[:100]}...")
    print()

print("\n" + "="*80)
print("COMPLETE SINGLE RECORD EXAMPLE")
print("="*80)

# Get a single record
sample = df.iloc[0]
print(f"\nRecord for Player {sample['player_id']} in Game {sample['game_id']}")
print(f"Model: {sample['model_name']}")
print()

for field in df.columns:
    print(f"\n{'─'*80}")
    print(f"FIELD: {field}")
    print(f"{'─'*80}")
    value = sample[field]

    if field == 'observations':
        # Parse and pretty print observations
        obs_dict = json.loads(value)
        print(f"Type: Dictionary with {len(obs_dict)} timestamped entries")
        print("\nFirst 3 entries:")
        for i, (timestamp, entry) in enumerate(list(obs_dict.items())[:3]):
            print(f"\n  [{i+1}] Timestamp: {timestamp}")
            print(f"      Observation: {entry['observation'][:200]}...")
            print(f"      Action: {entry.get('action', 'N/A')}")

        if len(obs_dict) > 3:
            print(f"\n  ... and {len(obs_dict) - 3} more entries")

    elif field == 'rewards':
        # Parse rewards
        try:
            rewards = json.loads(value)
            print(f"Type: {type(rewards).__name__}")
            print(f"Value: {rewards}")
        except:
            print(f"Value: {value}")

    elif field == 'opponent_names':
        # Parse opponent names
        try:
            opponents = json.loads(value)
            print(f"Type: List with {len(opponents)} opponents")
            print(f"Opponents: {opponents}")
        except:
            print(f"Value: {value}")

    else:
        print(f"Value: {value}")

print("\n" + "="*80)
print("OBSERVATIONS STRUCTURE - DETAILED LOOK")
print("="*80)

# Get a game with more turns
long_game = df[df['num_turns'] > 10].iloc[0]
obs_dict = json.loads(long_game['observations'])

print(f"\nExample from a longer game (Game {long_game['game_id']}, {long_game['num_turns']} turns)")
print(f"Player {long_game['player_id']}: {long_game['model_name']}")
print(f"\nTotal observation entries: {len(obs_dict)}")

print("\n" + "─"*80)
print("SHOWING ALL ENTRIES FROM THIS PLAYER'S GAME:")
print("─"*80)

for i, (timestamp, entry) in enumerate(obs_dict.items()):
    print(f"\n[Entry {i+1}] {timestamp}")
    print(f"  Observation:")
    obs_lines = entry['observation'].split('\n')
    for line in obs_lines[:20]:  # First 20 lines
        print(f"    {line}")
    if len(obs_lines) > 20:
        print(f"    ... ({len(obs_lines) - 20} more lines)")
    print(f"  Action: {entry.get('action', 'N/A')}")

print("\n" + "="*80)
print("REWARDS STRUCTURE")
print("="*80)

# Look at rewards across different outcomes
print("\nSample rewards for Mafia wins:")
mafia_win_sample = df[df['reason'].str.contains('Mafia wins')].iloc[0]
print(f"  Game {mafia_win_sample['game_id']}, Player {mafia_win_sample['player_id']}")
print(f"  Rewards: {mafia_win_sample['rewards']}")

print("\nSample rewards for Village wins:")
village_win_sample = df[df['reason'].str.contains('Village wins')].iloc[0]
print(f"  Game {village_win_sample['game_id']}, Player {village_win_sample['player_id']}")
print(f"  Rewards: {village_win_sample['rewards']}")

print("\n" + "="*80)
print("GAME-LEVEL VIEW (All players from one game)")
print("="*80)

sample_game_id = df['game_id'].iloc[100]
game_records = df[df['game_id'] == sample_game_id].sort_values('player_id')

print(f"\nGame ID: {sample_game_id}")
print(f"Number of players: {len(game_records)}")
print(f"Outcome: {game_records.iloc[0]['reason']}")
print(f"Total turns: {game_records.iloc[0]['num_turns']}")

print("\nPlayer breakdown:")
for idx, player_rec in game_records.iterrows():
    obs_dict = json.loads(player_rec['observations'])
    first_obs = list(obs_dict.values())[0]['observation']

    # Extract role
    role = "Unknown"
    team = "Unknown"
    if 'Your role:' in first_obs:
        role_line = [line for line in first_obs.split('\n') if 'Your role:' in line][0]
        role = role_line.split('Your role:')[1].strip()
    if 'Team:' in first_obs:
        team_line = [line for line in first_obs.split('\n') if 'Team:' in line][0]
        team = team_line.split('Team:')[1].strip()

    print(f"\n  Player {player_rec['player_id']}: {player_rec['model_name']}")
    print(f"    Role: {role} ({team} team)")
    print(f"    Observations: {len(obs_dict)} timestamped entries")
    print(f"    Rewards: {player_rec['rewards']}")

print("\n" + "="*80)
print("SUMMARY OF DATA CONTENTS")
print("="*80)

print("""
The dataset contains:

1. **Game Metadata**:
   - game_id, player_game_id, player_id
   - env_name (always "SecretMafia-v0")
   - model_name (which AI model played)
   - opponent_names (list of other models in the game)

2. **Observations** (JSON string):
   - Dictionary keyed by timestamps
   - Each entry contains:
     * observation: The game state/messages the player saw
     * action: What the player did in response
   - Observations include:
     * Role assignment (Mafia, Doctor, Detective, Villager)
     * Day phase: Public discussion and voting
     * Night phase: Role-specific actions
     * Game events (eliminations, deaths, etc.)

3. **Game Outcomes**:
   - num_turns: How many turns the game lasted
   - status: Always "finished"
   - reason: Either "Mafia wins" or "Village wins"
   - rewards: Final reward value (appears to be win/loss indicator)

4. **What you can analyze**:
   - Model performance across different roles
   - Communication strategies (observation text)
   - Decision quality (actions chosen)
   - How quickly games are won/lost
   - Voting patterns
   - Role-specific action effectiveness
""")
