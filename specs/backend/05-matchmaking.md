# Matchmaking System Specification

This specification defines the matchmaking system for Ultimate Tic-Tac-Toe.

## Overview

The matchmaking system matches players who want to play a game. It uses a simple first-come-first-served approach where any two players in the queue will be matched together.

## Components

The matchmaking system consists of the following components:

1. **Waiting Queue** - Stores players waiting for a match
2. **Match Storage** - Stores information about matched players
3. **TTL Mechanism** - Ensures players who disconnect are removed from the system
4. **Synchronization** - Ensures thread-safe operations

## Data Structures

### Waiting Players

A cache of players waiting for a match with the following structure:
- Key: Player ID
- Value: Player object
- TTL: 30 seconds

### Matched Games

A cache of matched games with the following structure:
- Key: Player ID
- Value: Tuple of (game_id, opponent_name, accepted)
- TTL: 30 seconds

## Operations

### Adding a Player to Matchmaking

1. Verify the player exists
2. Acquire a lock to ensure thread safety
3. Check if the player is already in the waiting list
   - If yes, refresh their presence and return success
4. Remove any previous matched game for this player
5. Add the player to the waiting list
6. Release the lock
7. Return success

### Removing a Player from Matchmaking

1. Acquire a lock to ensure thread safety
2. Check if the player is in the waiting list
   - If yes, remove them
3. Check if the player has a matched game
   - If yes, get the game ID
   - Find and remove the other player's match with the same game ID
   - Remove the player's match
4. Release the lock
5. Return status of whether the player was waiting or matched

### Updating Player Presence (Ping)

1. Acquire a lock to ensure thread safety
2. Check if the player is in the waiting list
   - If yes, refresh their TTL and return true
3. Check if the player has a matched game
   - If yes, refresh TTL and mark as accepted
   - Return true
4. If not in waiting or matched, return false
5. Release the lock

### Finding a Match

1. Acquire a lock to ensure thread safety
2. Check if the player already has a matched game
   - If yes, check if both players have accepted
   - If both accepted, clean up and return game, opponent name, and acceptance status
   - If waiting for other player, return opponent name and false for acceptance
3. Check if the player is in the waiting list
   - If not, return error
4. If there's only one player in the waiting list, return no match
5. Find another player in the waiting list
6. Create a game with the two players
7. Store the game ID and opponent names for both players
8. Remove both players from the waiting list
9. Return opponent name and false for acceptance
10. Release the lock

### Checking Player Status

- `is_player_in_queue(player_id)` - Checks if a player is in the waiting queue
- `has_pending_match(player_id)` - Checks if a player has a pending match

## Implementation Notes

1. **Thread Safety** - All operations should be thread-safe using a synchronization primitive such as a mutex
2. **TTL Handling** - The system should automatically expire entries based on TTL
3. **Error Handling** - Handle errors gracefully, especially during game creation
4. **Random Assignment** - When creating a game, randomly assign which player is X and which is O

## Matchmaking Flow

The typical flow for matchmaking is:

1. Player joins matchmaking by calling `/matchmaking/join`
2. Player begins polling `/matchmaking/ping` to maintain presence and check status
3. When a match is found, both players receive the opponent's name
4. Both players must continually ping to accept the match
5. Once both players have pinged (accepted), they receive the game ID
6. Players can view the game details via `/games/{game_id}`

## Timeout Handling

1. If a player stops pinging (disconnects), they are removed from matchmaking after 30 seconds
2. If either player in a matched game stops pinging, the match is abandoned after 30 seconds
3. Players should ping every 5-10 seconds to ensure they aren't removed from the system