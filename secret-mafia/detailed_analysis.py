#!/usr/bin/env python3
"""
Detailed analysis of Secret Mafia results to understand win conditions
"""

from datasets import load_dataset
import pandas as pd
import json

print("Loading dataset...")
dataset = load_dataset("bobbycxy/mgc2025-secretmafia")
df = pd.DataFrame(dataset['train'])

print("\n" + "="*60)
print("UNDERSTANDING WIN CONDITIONS")
print("="*60)

# Check unique statuses and reasons
print("\nUnique status values:")
print(df['status'].unique())

print("\nUnique reason values:")
print(df['reason'].unique())

# The dataset has 27,796 records from 4,999 games
# Each game has 6 players, so we should see ~6 records per game
print(f"\nRecords per game: {len(df) / df['game_id'].nunique():.2f}")

# Let's look at a complete game to understand the structure
sample_game_id = df['game_id'].iloc[0]
sample_game = df[df['game_id'] == sample_game_id].sort_values('player_id')

print(f"\n{'='*60}")
print(f"SAMPLE GAME #{sample_game_id}")
print(f"{'='*60}")

for idx, row in sample_game.iterrows():
    print(f"\nPlayer {row['player_id']} ({row['model_name']}):")
    print(f"  Status: {row['status']}")
    print(f"  Reason: {row['reason']}")
    print(f"  Num turns: {row['num_turns']}")

    # Parse observation to see role
    try:
        obs = json.loads(row['observations'])
        first_obs_key = list(obs.keys())[0]
        first_obs = obs[first_obs_key]['observation']

        # Extract role from observation
        if 'Your role:' in first_obs:
            role_line = [line for line in first_obs.split('\n') if 'Your role:' in line][0]
            print(f"  Role: {role_line.split('Your role:')[1].strip()}")
    except:
        pass

# Analyze win conditions by reason
print(f"\n{'='*60}")
print("WIN ANALYSIS BY REASON")
print(f"{'='*60}")

mafia_wins = df[df['reason'] == 'Mafia reached parity with villagers. Mafia wins!']
village_wins = df[df['reason'] == 'All Mafia were eliminated. Village wins!']

print(f"\nMafia win records: {len(mafia_wins):,}")
print(f"Village win records: {len(village_wins):,}")

# Check if we need to look at roles to determine individual winners
print(f"\n{'='*60}")
print("CHECKING ROLES IN OBSERVATIONS")
print(f"{'='*60}")

# Sample 100 random records and extract roles
sample_roles = []
for idx, row in df.sample(min(100, len(df))).iterrows():
    try:
        obs = json.loads(row['observations'])
        first_obs_key = list(obs.keys())[0]
        first_obs = obs[first_obs_key]['observation']

        if 'Your role:' in first_obs:
            role_line = [line for line in first_obs.split('\n') if 'Your role:' in line][0]
            role = role_line.split('Your role:')[1].strip()
            team_line = [line for line in first_obs.split('\n') if 'Team:' in line][0]
            team = team_line.split('Team:')[1].strip()
            sample_roles.append((role, team, row['reason']))
    except:
        pass

print("\nSample of roles and outcomes:")
role_df = pd.DataFrame(sample_roles, columns=['Role', 'Team', 'Outcome'])
print(role_df.groupby(['Team', 'Outcome']).size())

# Calculate actual win rates based on team alignment
print(f"\n{'='*60}")
print("RECALCULATING WIN RATES WITH TEAM ALIGNMENT")
print(f"{'='*60}")

# Extract role and team for all records (this may take a moment)
print("Extracting roles and teams from all records...")
roles_data = []

for idx, row in df.iterrows():
    if idx % 5000 == 0:
        print(f"  Processing record {idx:,}/{len(df):,}...")

    try:
        obs = json.loads(row['observations'])
        first_obs_key = list(obs.keys())[0]
        first_obs = obs[first_obs_key]['observation']

        role = None
        team = None

        if 'Your role:' in first_obs:
            role_line = [line for line in first_obs.split('\n') if 'Your role:' in line][0]
            role = role_line.split('Your role:')[1].strip()

        if 'Team:' in first_obs:
            team_line = [line for line in first_obs.split('\n') if 'Team:' in line][0]
            team = team_line.split('Team:')[1].strip()

        # Determine if this player won
        won = False
        if team == 'Mafia' and 'Mafia wins' in row['reason']:
            won = True
        elif team == 'Village' and 'Village wins' in row['reason']:
            won = True

        roles_data.append({
            'game_id': row['game_id'],
            'player_id': row['player_id'],
            'model_name': row['model_name'],
            'role': role,
            'team': team,
            'outcome': row['reason'],
            'won': won,
            'num_turns': row['num_turns']
        })
    except Exception as e:
        pass

roles_df = pd.DataFrame(roles_data)

# Calculate corrected win rates
print(f"\n{'='*60}")
print("MODEL WIN RATES (WITH TEAM ALIGNMENT)")
print(f"{'='*60}")

model_perf = roles_df.groupby('model_name').agg({
    'game_id': 'count',
    'won': 'sum',
    'num_turns': 'mean'
}).rename(columns={'game_id': 'total_games', 'won': 'wins', 'num_turns': 'avg_turns'})

model_perf['win_rate'] = model_perf['wins'] / model_perf['total_games']
model_perf = model_perf.sort_values('win_rate', ascending=False)

print("\nTop 20 models by win rate:")
print(model_perf.head(20).to_string())

# Save corrected results
model_perf.to_csv('model_performance_corrected.csv')
roles_df.to_csv('game_results_with_roles.csv', index=False)

print(f"\n{'='*60}")
print("SAVED FILES")
print(f"{'='*60}")
print("  - model_performance_corrected.csv")
print("  - game_results_with_roles.csv")
