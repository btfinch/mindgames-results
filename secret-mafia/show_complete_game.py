#!/usr/bin/env python3
"""
Show a complete game with all players' perspectives
"""

from datasets import load_dataset
import pandas as pd
import json

print("Loading dataset...")
dataset = load_dataset("bobbycxy/mgc2025-secretmafia")
df = pd.DataFrame(dataset['train'])

# Find a medium-length game with all 6 players
game_lengths = df.groupby('game_id').agg({
    'player_id': 'count',
    'num_turns': 'first'
})

# Get a 6-player game with 5-7 turns
good_games = game_lengths[(game_lengths['player_id'] == 6) &
                          (game_lengths['num_turns'] >= 5) &
                          (game_lengths['num_turns'] <= 7)]

sample_game_id = good_games.index[10]  # Pick the 10th one
game_data = df[df['game_id'] == sample_game_id].sort_values('player_id')

print("\n" + "="*80)
print(f"COMPLETE GAME EXAMPLE - Game #{sample_game_id}")
print("="*80)

print(f"\nGame Outcome: {game_data.iloc[0]['reason']}")
print(f"Total Turns: {game_data.iloc[0]['num_turns']}")

print("\n" + "─"*80)
print("PLAYER ROSTER")
print("─"*80)

# First pass: get all roles
player_info = {}
for idx, player_rec in game_data.iterrows():
    obs_dict = json.loads(player_rec['observations'])
    first_obs = list(obs_dict.values())[0]['observation']

    role = "Unknown"
    team = "Unknown"
    if 'Your role:' in first_obs:
        role_line = [line for line in first_obs.split('\n') if 'Your role:' in line][0]
        role = role_line.split('Your role:')[1].strip()
    if 'Team:' in first_obs:
        team_line = [line for line in first_obs.split('\n') if 'Team:' in line][0]
        team = team_line.split('Team:')[1].strip()

    reward = json.loads(player_rec['rewards'])[str(player_rec['player_id'])]
    won = reward == 1

    player_info[player_rec['player_id']] = {
        'model': player_rec['model_name'],
        'role': role,
        'team': team,
        'won': won,
        'observations': obs_dict
    }

    status_emoji = "✅" if won else "❌"
    team_emoji = "🔴" if team == "Mafia" else "🔵"
    print(f"\n{team_emoji} Player {player_rec['player_id']}: {player_rec['model_name'][:50]}")
    print(f"   Role: {role} ({team} team) {status_emoji}")

print("\n" + "="*80)
print("TURN-BY-TURN GAME FLOW")
print("="*80)

# Reconstruct game timeline by looking at all players' observations
# We'll follow Player 0's perspective as the main narrative
main_player = 0
main_obs = player_info[main_player]['observations']

for turn_idx, (timestamp, entry) in enumerate(main_obs.items(), 1):
    print(f"\n{'='*80}")
    print(f"TURN {turn_idx} - {timestamp}")
    print(f"{'='*80}")

    observation = entry['observation']
    action = entry.get('action', 'N/A')

    # Parse observation to understand what's happening
    lines = observation.split('\n')

    # Identify phase
    if 'Night phase' in observation:
        phase = "NIGHT"
    elif 'Day breaks' in observation or 'Discuss for' in observation:
        phase = "DAY - Discussion"
    elif 'VOTE' in observation or 'was eliminated by vote' in observation:
        phase = "DAY - Voting"
    elif 'Welcome to Secret Mafia' in observation:
        phase = "GAME START"
    else:
        phase = "ONGOING"

    print(f"\n📍 Phase: {phase}")
    print(f"👁️  Player {main_player} sees:")

    # Show key information
    for line in lines[:30]:  # First 30 lines
        if line.strip():
            # Highlight important lines
            if '[-1]' in line:
                print(f"   🔔 {line}")
            elif line.startswith('[') and line[1].isdigit():
                player_num = line[1]
                print(f"   💬 [Player {player_num}] {line[4:]}")
            else:
                print(f"      {line}")

    if len(lines) > 30:
        print(f"   ... ({len(lines) - 30} more lines)")

    print(f"\n⚡ Player {main_player} action: {action}")

    # Show what other players did this turn (if visible)
    if turn_idx <= len(main_obs):
        other_actions = []
        for pid, pinfo in player_info.items():
            if pid != main_player and turn_idx <= len(pinfo['observations']):
                other_obs_list = list(pinfo['observations'].values())
                if turn_idx - 1 < len(other_obs_list):
                    other_action = other_obs_list[turn_idx - 1].get('action', 'N/A')
                    if other_action and other_action != 'N/A':
                        role = pinfo['role']
                        other_actions.append(f"Player {pid} ({role}): {other_action[:50]}")

        if other_actions:
            print(f"\n🎭 Behind the scenes (other players' actions):")
            for act in other_actions[:3]:  # Show first 3
                print(f"   - {act}")

print("\n" + "="*80)
print("GAME RESULT")
print("="*80)

print(f"\n🏆 Outcome: {game_data.iloc[0]['reason']}")
print(f"\n👥 Winners:")
for pid, pinfo in player_info.items():
    if pinfo['won']:
        print(f"   Player {pid}: {pinfo['model'][:40]} ({pinfo['role']}, {pinfo['team']} team)")

print(f"\n💀 Losers:")
for pid, pinfo in player_info.items():
    if not pinfo['won']:
        print(f"   Player {pid}: {pinfo['model'][:40]} ({pinfo['role']}, {pinfo['team']} team)")

print("\n" + "="*80)
