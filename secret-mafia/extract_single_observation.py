#!/usr/bin/env python3
"""
Extract a single complete observation sequence and format it nicely
"""

from datasets import load_dataset
import pandas as pd
import json

print("Loading dataset...")
dataset = load_dataset("bobbycxy/mgc2025-secretmafia")
df = pd.DataFrame(dataset['train'])

# Find a good example - medium length game with interesting dynamics
game_lengths = df.groupby('game_id').agg({
    'player_id': 'count',
    'num_turns': 'first',
    'reason': 'first'
})

# Get a 6-player game with 6-8 turns that Village won (less common)
village_wins = game_lengths[(game_lengths['player_id'] == 6) &
                            (game_lengths['num_turns'] >= 6) &
                            (game_lengths['num_turns'] <= 8) &
                            (game_lengths['reason'].str.contains('Village wins'))]

if len(village_wins) == 0:
    # Fall back to any 6-player, 6-8 turn game
    good_games = game_lengths[(game_lengths['player_id'] == 6) &
                              (game_lengths['num_turns'] >= 6) &
                              (game_lengths['num_turns'] <= 8)]
    sample_game_id = good_games.index[5]
else:
    sample_game_id = village_wins.index[5]

game_data = df[df['game_id'] == sample_game_id].sort_values('player_id')

# Pick an interesting player - let's try to find the Detective
detective_player = None
for idx, player_rec in game_data.iterrows():
    obs_dict = json.loads(player_rec['observations'])
    first_obs = list(obs_dict.values())[0]['observation']
    if 'Detective' in first_obs:
        detective_player = player_rec
        break

if detective_player is None:
    detective_player = game_data.iloc[0]  # Fall back to first player

# Get all player info for context
player_roster = {}
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

    player_roster[player_rec['player_id']] = {
        'model': player_rec['model_name'],
        'role': role,
        'team': team,
        'won': won
    }

# Now create the markdown file
md_content = []

md_content.append("# Single Player Observation Example")
md_content.append("")
md_content.append("This document shows **one complete observation sequence** from a single player's perspective in a Secret Mafia game.")
md_content.append("")

md_content.append("---")
md_content.append("")

md_content.append("## Game Metadata")
md_content.append("")
md_content.append(f"- **Game ID**: `{detective_player['game_id']}`")
md_content.append(f"- **Player ID**: `{detective_player['player_id']}`")
md_content.append(f"- **Model**: `{detective_player['model_name']}`")
md_content.append(f"- **Role**: {player_roster[detective_player['player_id']]['role']}")
md_content.append(f"- **Team**: {player_roster[detective_player['player_id']]['team']}")
md_content.append(f"- **Result**: {'✅ WON' if player_roster[detective_player['player_id']]['won'] else '❌ LOST'}")
md_content.append(f"- **Game Outcome**: {detective_player['reason']}")
md_content.append(f"- **Total Turns**: {detective_player['num_turns']}")
md_content.append("")

md_content.append("---")
md_content.append("")

md_content.append("## Player Roster")
md_content.append("")
md_content.append("| Player ID | Model | Role | Team | Result |")
md_content.append("|-----------|-------|------|------|--------|")

for pid in sorted(player_roster.keys()):
    info = player_roster[pid]
    result = "✅ Won" if info['won'] else "❌ Lost"
    model_short = info['model'][:40] + "..." if len(info['model']) > 40 else info['model']
    highlight = " **← This player**" if pid == detective_player['player_id'] else ""
    md_content.append(f"| {pid} | {model_short} | {info['role']} | {info['team']} | {result}{highlight} |")

md_content.append("")
md_content.append("---")
md_content.append("")

md_content.append("## Observation Sequence")
md_content.append("")
md_content.append("Below is the **complete sequence of observations and actions** for this player throughout the game.")
md_content.append("")

# Parse observations
obs_dict = json.loads(detective_player['observations'])

for turn_num, (timestamp, entry) in enumerate(obs_dict.items(), 1):
    observation = entry['observation']
    action = entry.get('action', '(no action recorded)')

    md_content.append(f"### Turn {turn_num}")
    md_content.append("")
    md_content.append(f"**Timestamp**: `{timestamp}`")
    md_content.append("")

    # Determine phase
    if 'Welcome to Secret Mafia' in observation:
        phase_emoji = "🎮"
        phase_name = "GAME START & NIGHT PHASE"
    elif 'Night phase' in observation:
        phase_emoji = "🌙"
        phase_name = "NIGHT PHASE"
    elif 'Day breaks' in observation or 'Discuss for' in observation:
        phase_emoji = "☀️"
        phase_name = "DAY PHASE - Discussion"
    elif 'Voting phase' in observation:
        phase_emoji = "🗳️"
        phase_name = "VOTING PHASE"
    else:
        phase_emoji = "▶️"
        phase_name = "ONGOING"

    md_content.append(f"**Phase**: {phase_emoji} {phase_name}")
    md_content.append("")

    # Parse and categorize observation content
    lines = observation.split('\n')

    md_content.append("#### 📥 What the player observes:")
    md_content.append("")
    md_content.append("```")

    for line in lines:
        if line.strip():
            md_content.append(line)

    md_content.append("```")
    md_content.append("")

    md_content.append("#### 📤 What the player does:")
    md_content.append("")
    md_content.append("```")
    md_content.append(action)
    md_content.append("```")
    md_content.append("")
    md_content.append("---")
    md_content.append("")

md_content.append("## Summary")
md_content.append("")
md_content.append(f"This observation sequence shows how Player {detective_player['player_id']} ")
md_content.append(f"({player_roster[detective_player['player_id']]['role']}) experienced the game over ")
md_content.append(f"{detective_player['num_turns']} turns.")
md_content.append("")
md_content.append("**Key observations:**")
md_content.append("")
md_content.append("1. The player receives their **role assignment** at the start")
md_content.append("2. Each turn alternates between **Night** (secret actions) and **Day** (public discussion & voting)")
md_content.append("3. The player sees:")
md_content.append("   - Game events (deaths, eliminations)")
md_content.append("   - Other players' messages (during day phase)")
md_content.append("   - Results of their actions (e.g., investigation results for Detective)")
md_content.append("4. The player must respond with:")
md_content.append("   - Role-specific actions at night (`[Player X]` format)")
md_content.append("   - Free-form discussion during day phases")
md_content.append("   - Vote during voting phase (`[X]` format)")
md_content.append("")
md_content.append("The `observations` field contains this **entire conversation history** in JSON format,")
md_content.append("allowing deep analysis of strategic decision-making, communication patterns, and gameplay dynamics.")

# Write to file
output = '\n'.join(md_content)

with open('EXAMPLE_OBSERVATION.md', 'w') as f:
    f.write(output)

print(f"Created EXAMPLE_OBSERVATION.md")
print(f"Game: {detective_player['game_id']}")
print(f"Player: {detective_player['player_id']} ({player_roster[detective_player['player_id']]['role']})")
print(f"Turns: {detective_player['num_turns']}")
