# Secret Mafia Dataset Structure

## Overview

The dataset contains **27,796 player records** from **4,999 games** where AI models play a social deduction game called Secret Mafia (similar to Mafia/Werewolf).

## Record Structure

Each record represents **one player's perspective** in a single game. A 6-player game generates 6 separate records.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `player_game_id` | int | Unique identifier for this player-game combination |
| `game_id` | int | Game identifier (shared across all 6 players) |
| `player_id` | int | Player number (0-5) in this game |
| `env_name` | string | Always "SecretMafia-v0" |
| `model_name` | string | AI model that played this player (e.g., "google/gemini-2.0-flash-001") |
| `opponent_names` | JSON dict | Maps player_id → model_name for opponents |
| `observations` | JSON dict | Timestamped sequence of game states and actions (see below) |
| `rewards` | JSON dict | Final rewards per player: 1 for winners, -1 for losers |
| `num_turns` | int | Number of turns the game lasted (1-23) |
| `status` | string | Always "finished" |
| `reason` | string | Game outcome: "Mafia wins" or "Village wins" |

## Game Rules

### Teams & Roles

**Village Team** (must eliminate all Mafia to win):
- **Villager**: No special powers, votes during day
- **Doctor**: Protects one player from elimination each night
- **Detective**: Investigates one player each night to check if they're Mafia

**Mafia Team** (must reach parity with village to win):
- **Mafia**: Eliminates one player each night, pretends to be village during day

### Game Flow

1. **Night Phase**: Role-specific actions happen
   - Mafia chooses a victim to eliminate
   - Doctor chooses someone to protect
   - Detective investigates someone

2. **Day Phase**: Public discussion (3 rounds) then vote
   - All players see who died/was eliminated
   - Players discuss and accuse each other
   - Everyone votes to eliminate a suspect
   - Player with most votes is eliminated

3. Repeat until win condition met

## Observations Structure

The `observations` field is the **richest data source**. It's a JSON dictionary keyed by timestamps:

```json
{
  "2025-07-09 09:19:52.03938+00": {
    "observation": "[Full game state text]",
    "action": "[What the player did]"
  },
  "2025-07-09 09:20:15.12345+00": {
    "observation": "[Next game state]",
    "action": "[Next action]"
  }
}
```

### What's in an observation?

**Initial observation** (always first):
```
[-1] Welcome to Secret Mafia! You are Player 0.
Your role: Doctor
Team: Village
Description: Protect one player each night from Mafia elimination.

Players: Player 0, Player 1, Player 2, Player 3, Player 4, Player 5

During DAY phase: Speak freely and vote.
During NIGHT phase: '[Player X]' to protect a player.
Win by identifying and eliminating all Mafia members.

[-1] Night phase - choose one player to protect: [1], [2], [3], [4], [5]
```

**Night phase observations**:
```
[-1] Player 2 was killed during the night.
[-1] Day breaks. Discuss for 3 rounds, then a vote will follow.
```

**Day phase observations** (includes all player messages):
```
[3] I think Player 5 is suspicious. They've been very quiet.
[1] I agree with Player 3. Player 5, what's your defense?
[5] I'm just observing carefully. I suspect Player 3 is trying to deflect.
```

**Vote results**:
```
[0] VOTE: Player 5
[1] VOTE: Player 5
[3] VOTE: Player 4
...
[-1] Player 5 was eliminated by vote.
```

### What's in an action?

**Night actions**:
- `"[Player 3]"` - Mafia kills Player 3, Doctor protects Player 3, or Detective investigates Player 3

**Day actions**:
- Free-form text during discussion rounds
- `"[3]"` or `"VOTE: Player 3"` during voting

## Example: Complete Game from One Player's View

**Player 1 (Detective, Village team)**

1. **Turn 1** (Night): Investigate Player 4 → learns "Player 4 IS NOT a Mafia member"
2. **Turn 2** (Day): Sees "Player 2 was killed", reads other players' messages, discusses, votes Player 3
3. **Turn 3** (Night): Player 3 eliminated, investigates Player 0 → learns "Player 0 IS NOT a Mafia member"
4. **Turn 4** (Day): Discusses, votes Player 5
5. Game ends: "All Mafia were eliminated. Village wins!"

The player's observations contain:
- Their role and team assignment
- All night action results
- All public chat messages
- All vote results
- Their own actions at each step

## Rewards Explained

The `rewards` field shows final payoffs for all players:

```json
{"0": -1, "1": 1, "2": -1, "3": 1, "4": 1, "5": 1}
```

- `1` = Winner (was on winning team)
- `-1` = Loser (was on losing team)

In this example:
- Players 1, 3, 4, 5 won (likely Village team when Village won, or Mafia team when Mafia won)
- Players 0, 2 lost

## What Can You Analyze?

### 1. **Model Performance**
- Win rates by model
- Win rates by role (is a model better as Mafia vs Detective?)
- Win rates by team assignment

### 2. **Strategic Patterns**
- What do successful Mafia players say during day discussions?
- When do successful Detectives reveal their findings?
- How do Doctors decide who to protect?

### 3. **Communication Analysis**
- Length of messages (verbose vs concise)
- Sentiment (aggressive vs cooperative)
- Persuasion tactics (logical arguments vs emotional appeals)
- Deception quality (how well Mafia players blend in)

### 4. **Decision Quality**
- Voting accuracy (did players vote for actual Mafia?)
- Investigation effectiveness (Detective choice quality)
- Protection effectiveness (Doctor saves)
- Survival rates per role

### 5. **Game Dynamics**
- What causes quick vs long games?
- When does Mafia typically win vs lose?
- Impact of early eliminations on outcomes
- Role distribution impact on win rates

### 6. **Model Comparison**
- Which models are better at deception?
- Which models are better at deduction?
- Open-source vs closed-source performance
- Model size vs performance correlation

## Data Quality Notes

- All games are complete (status = "finished")
- Average game: 5.56 players per game (some may have disconnects/errors)
- Games range from 1 turn (instant loss) to 23 turns (extended strategic play)
- Mafia wins 66.6% of games (significant imbalance)

## Files for Analysis

- `game_results_with_roles.csv` - Every record with extracted role/team/win status
- `model_performance_corrected.csv` - Aggregated win rates by model
- Raw dataset on Hugging Face for full observation text
