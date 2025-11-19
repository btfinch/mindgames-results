# Secret Mafia Challenge Analysis Summary

**Dataset**: [mgc2025-secretmafia on Hugging Face](https://huggingface.co/datasets/bobbycxy/mgc2025-secretmafia)

## Overview

- **Total Records**: 27,796 player-game records
- **Unique Games**: 4,999
- **Unique Players per Game**: ~5.6 average (6 player setup)
- **Unique Models Tested**: 313
- **Average Game Length**: 5.26 turns
- **Game Length Range**: 1-23 turns

## Key Findings

### 1. Win Distribution

**Mafia vs Village Outcomes:**
- Mafia Wins: 18,510 records (66.6%)
- Village Wins: 9,286 records (33.4%)

**Important**: The game appears to be significantly Mafia-favored, with Mafia winning ~2x as often as Village.

### 2. Understanding Win Conditions

Initially, it appeared all models had 0% win rates. This was because the dataset doesn't explicitly mark individual winners - it only provides the game outcome reason:
- "Mafia reached parity with villagers. Mafia wins!"
- "All Mafia were eliminated. Village wins!"

To calculate individual model performance, we need to:
1. Parse each player's role/team from their observation data
2. Match their team (Mafia/Village) with the game outcome
3. Calculate win rate based on team alignment

### 3. Role Distribution

The game includes the following roles:
- **Village Team**: Villager, Doctor, Detective
- **Mafia Team**: Mafia

Each game has 6 players with different role assignments.

### 4. Top Performing Models

**Models with Significant Sample Size (50+ games):**

The most reliable performance metrics come from models with substantial game counts. Among models with 50+ games, the top performers balance win rate with volume.

**Note**: Models with only 1-2 games showing 100% win rate should be interpreted cautiously - these likely benefited from favorable role assignments or random matchups.

### 5. Game Characteristics

- **Short Games**: Average of 5.26 turns suggests many games end quickly
- **Variable Length**: Range of 1-23 turns indicates some games are decided immediately while others involve extended strategic play
- **Mafia Advantage**: The 2:1 Mafia win ratio suggests either:
  - Mafia strategy is easier to execute
  - Village coordination is challenging
  - The game setup inherently favors Mafia

## Files Generated

### Data Files
- `model_summary.csv` - Basic model statistics (uncorrected)
- `model_performance_corrected.csv` - Win rates calculated with team alignment
- `game_results_with_roles.csv` - Complete game results with extracted roles and teams

### Visualizations
- `top_models_win_rate.png` - Top 20 models by win rate (50+ game minimum)
- `win_rate_vs_games.png` - Scatter plot showing relationship between games played and win rate
- `team_win_distribution.png` - Mafia vs Village win rate comparison
- `role_distribution.png` - Pie chart of role frequency
- `game_length_distribution.png` - Histogram of game lengths
- `top_models_comprehensive.png` - Detailed comparison of top 15 models with confidence intervals

## Recommendations for Further Analysis

1. **Role-Specific Performance**: Analyze how each model performs in specific roles (Mafia, Doctor, Detective, Villager)

2. **Matchup Analysis**: Examine which model combinations lead to better/worse outcomes

3. **Strategic Patterns**: Deep dive into observation data to identify successful strategies

4. **Turn-by-Turn Analysis**: Examine decision quality at different game stages

5. **Communication Patterns**: Analyze the natural language strategies used by different models

6. **Sample Size Considerations**: Focus on models with 100+ games for most reliable conclusions

7. **Opponent Strength**: Control for opponent skill levels when evaluating model performance

## Next Steps

To continue this analysis, you could:
- Create a leaderboard with confidence intervals
- Perform role-specific analysis
- Analyze communication strategies in observation logs
- Build a prediction model for game outcomes
- Identify specific weaknesses in Village team play
- Compare open-source vs closed-source model performance
