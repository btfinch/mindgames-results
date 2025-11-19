#!/usr/bin/env python3
"""
Initial exploration of the Secret Mafia dataset from Mind Games Challenge 2025
"""

from datasets import load_dataset
import pandas as pd
import json

print("Loading dataset from Hugging Face...")
dataset = load_dataset("bobbycxy/mgc2025-secretmafia")

# Convert to pandas for easier exploration
df = pd.DataFrame(dataset['train'])

print(f"\n{'='*60}")
print("DATASET OVERVIEW")
print(f"{'='*60}")
print(f"Total records: {len(df):,}")
print(f"Columns: {list(df.columns)}")
print(f"\nData types:")
print(df.dtypes)

print(f"\n{'='*60}")
print("BASIC STATISTICS")
print(f"{'='*60}")
print(f"Unique games: {df['game_id'].nunique():,}")
print(f"Unique players: {df['player_id'].nunique():,}")
print(f"Unique models: {df['model_name'].nunique()}")
print(f"Average turns per game: {df['num_turns'].mean():.2f}")
print(f"Min turns: {df['num_turns'].min()}")
print(f"Max turns: {df['num_turns'].max()}")

print(f"\n{'='*60}")
print("TOP 10 MODELS BY GAME COUNT")
print(f"{'='*60}")
model_counts = df['model_name'].value_counts().head(10)
for i, (model, count) in enumerate(model_counts.items(), 1):
    print(f"{i:2d}. {model}: {count:,} games")

print(f"\n{'='*60}")
print("GAME STATUS DISTRIBUTION")
print(f"{'='*60}")
print(df['status'].value_counts())

print(f"\n{'='*60}")
print("REASON DISTRIBUTION")
print(f"{'='*60}")
print(df['reason'].value_counts())

# Save a summary CSV
print(f"\n{'='*60}")
print("SAVING SUMMARY DATA")
print(f"{'='*60}")

# Model performance summary
model_summary = df.groupby('model_name').agg({
    'game_id': 'count',
    'num_turns': 'mean',
    'status': lambda x: (x == 'win').sum() if 'win' in x.values else 0
}).rename(columns={
    'game_id': 'total_games',
    'num_turns': 'avg_turns',
    'status': 'wins'
})
model_summary['win_rate'] = model_summary['wins'] / model_summary['total_games']
model_summary = model_summary.sort_values('win_rate', ascending=False)

model_summary.to_csv('model_summary.csv')
print("Saved: model_summary.csv")

# Sample a few observations to understand content
print(f"\n{'='*60}")
print("SAMPLE OBSERVATION (first 1000 chars)")
print(f"{'='*60}")
sample_obs = df.iloc[0]['observations']
print(sample_obs[:1000] if len(sample_obs) > 1000 else sample_obs)

print(f"\n{'='*60}")
print("COMPLETE!")
print(f"{'='*60}")
