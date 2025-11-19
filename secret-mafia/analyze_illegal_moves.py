#!/usr/bin/env python3
"""
Analyze illegal moves and how they're flagged in the dataset
"""

from datasets import load_dataset
import pandas as pd
import json
import re

print("Loading dataset...")
dataset = load_dataset("bobbycxy/mgc2025-secretmafia")
df = pd.DataFrame(dataset['train'])

print("\n" + "="*80)
print("SEARCHING FOR ILLEGAL MOVE INDICATORS")
print("="*80)

# Search for illegal moves in observations
illegal_move_records = []

for idx, row in df.iterrows():
    if idx % 5000 == 0:
        print(f"Processing record {idx}/{len(df)}...")

    try:
        obs_dict = json.loads(row['observations'])

        for timestamp, entry in obs_dict.items():
            observation = entry['observation']
            action = entry.get('action', '')

            # Look for indicators of invalid/illegal moves
            if 'invalid' in observation.lower() or 'attempted an invalid move' in observation.lower():
                illegal_move_records.append({
                    'game_id': row['game_id'],
                    'player_id': row['player_id'],
                    'model_name': row['model_name'],
                    'timestamp': timestamp,
                    'observation': observation,
                    'action': action,
                    'num_turns': row['num_turns']
                })
    except:
        pass

print(f"\nFound {len(illegal_move_records)} observations with illegal move flags")

# Analyze the types of illegal moves
print("\n" + "="*80)
print("TYPES OF ILLEGAL MOVES")
print("="*80)

illegal_types = {}
for record in illegal_move_records:
    obs = record['observation']

    # Extract the reason
    if 'Reason:' in obs:
        reason_match = re.search(r'Reason: ([^\n\.]+)', obs)
        if reason_match:
            reason = reason_match.group(1).strip()
            illegal_types[reason] = illegal_types.get(reason, 0) + 1

print("\nIllegal move reasons:")
for reason, count in sorted(illegal_types.items(), key=lambda x: x[1], reverse=True):
    print(f"  {count:4d} - {reason}")

# Show examples of each type
print("\n" + "="*80)
print("EXAMPLES OF ILLEGAL MOVES")
print("="*80)

shown_types = set()
for record in illegal_move_records[:30]:  # Show first 30
    obs = record['observation']

    # Extract reason
    reason = "Unknown"
    if 'Reason:' in obs:
        reason_match = re.search(r'Reason: ([^\n\.]+)', obs)
        if reason_match:
            reason = reason_match.group(1).strip()

    if reason not in shown_types:
        shown_types.add(reason)

        print(f"\n{'─'*80}")
        print(f"EXAMPLE: {reason}")
        print(f"{'─'*80}")
        print(f"Game: {record['game_id']}, Player: {record['player_id']}")
        print(f"Model: {record['model_name']}")
        print(f"\nFull observation:")
        print(obs)
        print(f"\nPlayer's attempted action:")
        print(record['action'][:500] if len(record['action']) > 500 else record['action'])

# Check if players were penalized/eliminated for illegal moves
print("\n" + "="*80)
print("CONSEQUENCES OF ILLEGAL MOVES")
print("="*80)

# Group by game and player to see if they recovered or were eliminated
illegal_by_player = {}
for record in illegal_move_records:
    key = (record['game_id'], record['player_id'])
    if key not in illegal_by_player:
        illegal_by_player[key] = []
    illegal_by_player[key].append(record)

print(f"\nPlayers who made illegal moves: {len(illegal_by_player)}")

# Check a few examples to see what happened
print("\nChecking outcomes for players who made illegal moves...")

sample_illegal_players = list(illegal_by_player.keys())[:10]
for game_id, player_id in sample_illegal_players:
    # Get the full record
    full_record = df[(df['game_id'] == game_id) & (df['player_id'] == player_id)].iloc[0]

    obs_dict = json.loads(full_record['observations'])
    num_illegal = len([o for o in obs_dict.values() if 'invalid' in o['observation'].lower()])

    # Check if player was eliminated
    eliminated = False
    for obs in obs_dict.values():
        if 'eliminated by making an invalid move' in obs['observation']:
            eliminated = True
            break

    reward = json.loads(full_record['rewards'])[str(player_id)]

    print(f"\nGame {game_id}, Player {player_id} ({full_record['model_name'][:40]})")
    print(f"  Illegal moves: {num_illegal}")
    print(f"  Eliminated for invalid move: {eliminated}")
    print(f"  Final reward: {reward} ({'Won' if reward == 1 else 'Lost'})")

# Statistics on illegal moves
print("\n" + "="*80)
print("ILLEGAL MOVE STATISTICS")
print("="*80)

total_records = len(df)
records_with_illegal = len(set([(r['game_id'], r['player_id']) for r in illegal_move_records]))

print(f"\nTotal player records: {total_records:,}")
print(f"Records with at least one illegal move: {records_with_illegal:,}")
print(f"Percentage: {100 * records_with_illegal / total_records:.2f}%")

# Models most prone to illegal moves
print("\nTop 10 models making illegal moves:")
model_illegal_counts = {}
for key in illegal_by_player.keys():
    game_id, player_id = key
    record = df[(df['game_id'] == game_id) & (df['player_id'] == player_id)].iloc[0]
    model = record['model_name']
    model_illegal_counts[model] = model_illegal_counts.get(model, 0) + 1

for i, (model, count) in enumerate(sorted(model_illegal_counts.items(),
                                          key=lambda x: x[1], reverse=True)[:10], 1):
    # Get total games for this model
    total_games = len(df[df['model_name'] == model])
    pct = 100 * count / total_games
    print(f"{i:2d}. {model[:50]:50s} - {count:3d}/{total_games:4d} games ({pct:5.1f}%)")

print("\n" + "="*80)
