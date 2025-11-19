#!/usr/bin/env python3
"""
Create visualizations for Secret Mafia results
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

print("Loading processed data...")
model_perf = pd.read_csv('model_performance_corrected.csv')
games_df = pd.read_csv('game_results_with_roles.csv')

# Filter to models with at least 50 games for meaningful statistics
min_games = 50
significant_models = model_perf[model_perf['total_games'] >= min_games].copy()

print(f"\nFound {len(significant_models)} models with at least {min_games} games")

# 1. Top models by win rate (with minimum games threshold)
print("\nCreating win rate visualization...")
top_n = 20
top_models = significant_models.nlargest(top_n, 'win_rate')

plt.figure(figsize=(14, 10))
bars = plt.barh(range(len(top_models)), top_models['win_rate'], color='steelblue')

# Color bars by win rate
colors = plt.cm.RdYlGn(top_models['win_rate'] / top_models['win_rate'].max())
for bar, color in zip(bars, colors):
    bar.set_color(color)

plt.yticks(range(len(top_models)), top_models['model_name'])
plt.xlabel('Win Rate', fontsize=12)
plt.title(f'Top {top_n} Models by Win Rate (min {min_games} games)', fontsize=14, fontweight='bold')
plt.xlim(0, 1)

# Add value labels
for i, (idx, row) in enumerate(top_models.iterrows()):
    plt.text(row['win_rate'] + 0.01, i,
             f"{row['win_rate']:.3f} ({int(row['total_games'])} games)",
             va='center', fontsize=9)

plt.tight_layout()
plt.savefig('top_models_win_rate.png', dpi=300, bbox_inches='tight')
print("  Saved: top_models_win_rate.png")

# 2. Win rate vs games played scatter
print("\nCreating win rate vs games played scatter...")
plt.figure(figsize=(12, 8))

plt.scatter(model_perf['total_games'], model_perf['win_rate'],
            alpha=0.6, s=50, c=model_perf['win_rate'], cmap='RdYlGn')

# Annotate top performers with many games
top_annotate = model_perf[
    (model_perf['total_games'] >= 500) |
    ((model_perf['win_rate'] > 0.4) & (model_perf['total_games'] >= 100))
]

for idx, row in top_annotate.iterrows():
    plt.annotate(row['model_name'],
                 (row['total_games'], row['win_rate']),
                 xytext=(5, 5), textcoords='offset points',
                 fontsize=8, alpha=0.7)

plt.xlabel('Total Games Played', fontsize=12)
plt.ylabel('Win Rate', fontsize=12)
plt.title('Model Win Rate vs Games Played', fontsize=14, fontweight='bold')
plt.colorbar(label='Win Rate')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('win_rate_vs_games.png', dpi=300, bbox_inches='tight')
print("  Saved: win_rate_vs_games.png")

# 3. Team win distribution
print("\nCreating team win distribution...")
team_wins = games_df.groupby('team')['won'].agg(['sum', 'count'])
team_wins['win_rate'] = team_wins['sum'] / team_wins['count']

plt.figure(figsize=(10, 6))
bars = plt.bar(team_wins.index, team_wins['win_rate'], color=['#e74c3c', '#3498db'])
plt.ylabel('Win Rate', fontsize=12)
plt.xlabel('Team', fontsize=12)
plt.title('Win Rate by Team (Mafia vs Village)', fontsize=14, fontweight='bold')
plt.ylim(0, 1)

# Add value labels
for i, (team, rate) in enumerate(team_wins['win_rate'].items()):
    plt.text(i, rate + 0.02, f'{rate:.3f}\n({int(team_wins.loc[team, "count"])} games)',
             ha='center', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('team_win_distribution.png', dpi=300, bbox_inches='tight')
print("  Saved: team_win_distribution.png")

# 4. Role distribution
print("\nCreating role distribution...")
role_counts = games_df['role'].value_counts()

plt.figure(figsize=(10, 6))
colors = plt.cm.Set3(range(len(role_counts)))
plt.pie(role_counts, labels=role_counts.index, autopct='%1.1f%%',
        startangle=90, colors=colors)
plt.title('Distribution of Roles in Games', fontsize=14, fontweight='bold')
plt.axis('equal')
plt.tight_layout()
plt.savefig('role_distribution.png', dpi=300, bbox_inches='tight')
print("  Saved: role_distribution.png")

# 5. Average turns distribution
print("\nCreating turns distribution...")
plt.figure(figsize=(12, 6))
plt.hist(games_df['num_turns'], bins=23, edgecolor='black', alpha=0.7, color='steelblue')
plt.xlabel('Number of Turns', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.title('Distribution of Game Lengths', fontsize=14, fontweight='bold')
plt.axvline(games_df['num_turns'].mean(), color='red', linestyle='--',
            linewidth=2, label=f'Mean: {games_df["num_turns"].mean():.2f}')
plt.legend()
plt.tight_layout()
plt.savefig('game_length_distribution.png', dpi=300, bbox_inches='tight')
print("  Saved: game_length_distribution.png")

# 6. Top models comparison (with confidence intervals)
print("\nCreating comprehensive top models comparison...")
top_models_detailed = significant_models.nlargest(15, 'win_rate').copy()

# Calculate Wilson score confidence intervals (95%)
def wilson_ci(wins, n, z=1.96):
    phat = wins / n
    denominator = 1 + z**2/n
    centre = (phat + z**2/(2*n)) / denominator
    spread = z * np.sqrt((phat*(1-phat) + z**2/(4*n))/n) / denominator
    return centre - spread, centre + spread

top_models_detailed['ci_lower'] = top_models_detailed.apply(
    lambda row: wilson_ci(row['wins'], row['total_games'])[0], axis=1
)
top_models_detailed['ci_upper'] = top_models_detailed.apply(
    lambda row: wilson_ci(row['wins'], row['total_games'])[1], axis=1
)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10))

# Left plot: Win rate with confidence intervals
y_pos = range(len(top_models_detailed))
ax1.barh(y_pos, top_models_detailed['win_rate'], color='steelblue', alpha=0.7)
ax1.errorbar(top_models_detailed['win_rate'], y_pos,
             xerr=[top_models_detailed['win_rate'] - top_models_detailed['ci_lower'],
                   top_models_detailed['ci_upper'] - top_models_detailed['win_rate']],
             fmt='none', ecolor='black', capsize=5, alpha=0.5)

ax1.set_yticks(y_pos)
ax1.set_yticklabels(top_models_detailed['model_name'], fontsize=9)
ax1.set_xlabel('Win Rate (with 95% CI)', fontsize=11)
ax1.set_title('Top 15 Models by Win Rate', fontsize=12, fontweight='bold')
ax1.axvline(0.5, color='red', linestyle='--', alpha=0.3, label='50% baseline')
ax1.legend()
ax1.grid(alpha=0.3)

# Right plot: Games played
ax2.barh(y_pos, top_models_detailed['total_games'], color='coral', alpha=0.7)
ax2.set_yticks(y_pos)
ax2.set_yticklabels([''] * len(y_pos))  # Hide labels on right plot
ax2.set_xlabel('Total Games Played', fontsize=11)
ax2.set_title('Number of Games', fontsize=12, fontweight='bold')
ax2.grid(alpha=0.3)

# Add value labels
for i, (idx, row) in enumerate(top_models_detailed.iterrows()):
    ax2.text(row['total_games'] + 20, i, f"{int(row['total_games'])}",
             va='center', fontsize=9)

plt.tight_layout()
plt.savefig('top_models_comprehensive.png', dpi=300, bbox_inches='tight')
print("  Saved: top_models_comprehensive.png")

print("\n" + "="*60)
print("ALL VISUALIZATIONS COMPLETE!")
print("="*60)
