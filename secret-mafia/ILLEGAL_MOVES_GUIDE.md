# Illegal Move Flags in Secret Mafia Dataset

## Overview

**Yes, there are clear flags for illegal moves!** The dataset contains explicit error messages when agents attempt invalid actions.

## Key Statistics

- **42.52%** of all player records contain at least one illegal move
- **11,818 out of 27,796** player records had illegal moves
- **17,385** total illegal move observations across all games

## How Illegal Moves Are Flagged

### Standard Format

When a player makes an illegal move, they receive an observation like:

```
[-1] Player X attempted an invalid move. Reason: [reason].
Please resubmit a valid move and remember to follow the game rules to avoid penalties.
```

The `[-1]` prefix indicates a **system message**.

### Consequences

Players who make illegal moves face two possible outcomes:

1. **Warning**: Get to retry with a corrected action (most common)
2. **Elimination**: Immediately eliminated from the game

Example of elimination:
```
[-1] Player 0 has been eliminated by making an invalid move.
```

## Types of Illegal Moves

### Most Common (Top 5)

| Reason | Count | % of Total |
|--------|-------|------------|
| Vote not in valid format or invalid target | 6,992 | 40.2% |
| Invalid investigation target | 1,394 | 8.0% |
| Invalid protection target | 952 | 5.5% |
| Cannot investigate oneself | 8 | <0.1% |
| Attempted to protect a player during the day phase | 5 | <0.1% |

### All Illegal Move Types

1. **Voting Errors** (6,992 cases)
   - Not using `[X]` format
   - Voting for dead/eliminated players
   - Voting for invalid player numbers

2. **Investigation Errors** (1,402 cases)
   - Detective investigating invalid targets
   - Investigating themselves
   - Investigating dead players
   - Non-Detective trying to investigate

3. **Protection Errors** (957 cases)
   - Doctor protecting invalid targets
   - Protecting during wrong phase
   - Protecting dead players

4. **Phase/Timing Errors**
   - Acting during wrong phase
   - Acting after already acting
   - Acting after game end

5. **Format Errors**
   - Long explanations instead of action format
   - Missing square brackets
   - Invalid player numbers

## Examples

### Example 1: Invalid Vote Format

**Observation:**
```
[-1] Player 5 attempted an invalid move.
Reason: Vote not in valid format or invalid target.
Please resubmit a valid move and remember to follow the game rules to avoid penalties.
```

**Player's attempted action:**
```
Based on the discussions, here's my reasoning:
* Player 1 has been attempting to create a negative dynamic
* Player 3 made sure I got more pressure

Therefore, I will vote for Player 3.
My vote: **[3]**
```

**Issue**: Used markdown formatting (`**[3]**`) instead of plain `[3]`

---

### Example 2: Invalid Protection Target

**Observation:**
```
[-1] Player 5 attempted an invalid move.
Reason: Invalid protection target.
Please resubmit a valid move and remember to follow the game rules to avoid penalties.
```

**Player's attempted action:**
```
I will protect Player 1.
```

**Issue**: Used words ("I will protect Player 1") instead of required format `[Player 1]` or `[1]`

---

### Example 3: Invalid Investigation Target

**Observation:**
```
[-1] Player 5 attempted an invalid move.
Reason: Invalid investigation target.
Please resubmit a valid move and remember to follow the game rules to avoid penalties.
```

**Player's attempted action:**
```
Player 5: [Player 2]
```

**Issue**: Included extra text ("Player 5:") before the action, or target was already dead/eliminated

---

### Example 4: Elimination for Invalid Move

**Observation:**
```
[-1] Welcome to Secret Mafia! You are Player 0.
Your role: Detective
[...]
[-1] Player 0 has been eliminated by making an invalid move.
[-1] Night phase - choose one player to investigate: [1], [2], [3], [5]
```

**Result**: Player immediately eliminated, game continues without them

## Models Most Prone to Illegal Moves

| Rank | Model | Illegal Moves | Total Games | % |
|------|-------|---------------|-------------|---|
| 1 | qwen/qwen-2.5-7b-instruct | 1,457 | 2,136 | 68.2% |
| 2 | google/gemma-3-12b-it | 753 | 1,213 | 62.1% |
| 3 | openai/gpt-4.1-nano | 1,085 | 2,192 | 49.5% |
| 4 | google/gemini-2.0-flash-lite-001 | 1,248 | 2,619 | 47.7% |
| 5 | qwen/qwen-turbo | 1,314 | 2,935 | 44.8% |

**Notable**: The smaller/faster models (7B, lite versions) have significantly higher illegal move rates, suggesting they struggle more with format compliance.

## Impact on Analysis

### Why This Matters

1. **Performance Evaluation**: Models making many illegal moves may have inflated loss rates due to eliminations, not strategy
2. **Instruction Following**: Illegal move rate is a proxy for instruction-following capability
3. **Data Quality**: Games with many illegal moves may have degraded strategic quality
4. **Fair Comparison**: Should compare models within similar illegal-move-rate bands

### Recommendations for Analysis

1. **Filter Option**: Consider filtering out games with excessive illegal moves
2. **Separate Metric**: Track illegal move rate as a separate capability metric
3. **Adjusted Win Rate**: Calculate win rate excluding games lost to elimination
4. **Role-Specific Analysis**: Some roles (Detective, Doctor) have higher illegal move risk due to complex night actions

## Detection in Code

To detect illegal moves in your analysis:

```python
import json

def has_illegal_moves(observations_json):
    """Check if a player made any illegal moves"""
    obs_dict = json.loads(observations_json)
    for timestamp, entry in obs_dict.items():
        if 'invalid move' in entry['observation'].lower():
            return True
    return False

def was_eliminated_by_illegal_move(observations_json):
    """Check if player was eliminated for illegal move"""
    obs_dict = json.loads(observations_json)
    for timestamp, entry in obs_dict.items():
        if 'eliminated by making an invalid move' in entry['observation']:
            return True
    return False

def extract_illegal_move_reason(observation):
    """Extract the reason for an illegal move"""
    import re
    match = re.search(r'Reason: ([^\n\.]+)', observation)
    if match:
        return match.group(1).strip()
    return None
```

## Summary

**Illegal moves are clearly flagged** in the observations with:
- ✅ Explicit error messages from the game system
- ✅ Clear reason descriptions
- ✅ Option to retry or immediate elimination
- ✅ Observable in the `observations` field

This makes it easy to filter, analyze, or account for illegal moves in your competition analysis!
