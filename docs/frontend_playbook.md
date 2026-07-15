# Client Gameplay Playbook

This document defines the expected behavior of a four-player tavern auto-battler client. The engine and server remain authoritative; the client renders state, collects commands, and plays ordered combat events.

## Game phases

### Lobby

- Display four player slots and hero selections.
- Prevent duplicate readiness commands.
- Transition only after a server `recruit_state` message.

### Recruit

- Players start with three gold. The allowance increases by one each turn to a maximum of ten.
- Buying a minion costs three gold and requires hand capacity.
- Selling returns one gold.
- Refresh costs one gold; Freeze is free.
- The board holds seven minions and the hand holds ten cards.
- Playing a minion from hand is free and resolves its Battlecry immediately.
- A third matching copy creates a Golden minion and opens a Discover offer.

### Combat

1. Snapshot each board from left to right.
2. The player with more minions attacks first; ties use the supplied combat seed.
3. Players alternate attacks while both boards contain living minions.
4. Taunt minions must be targeted before non-Taunt minions.
5. Damage is simultaneous; Divine Shield absorbs the first positive hit.
6. Resolve deaths from left to right, then Deathrattles, summons, and Reborn.
7. Hero damage equals the winner's tavern tier plus surviving minion tiers.
8. Render events exactly in server order so replay output remains deterministic.

## Hero requirements

| Hero | Power | Cost and limit |
|---|---|---|
| Sylvanas Windrunner | Buff friendly minions that died in the previous combat | 1 gold, once per turn |
| The Lich King | Give a friendly minion Reborn for the next combat | 1 gold, once per turn |
| Millhouse Manastorm | Minions cost 2; refresh costs 2; upgrades cost 1 more | Passive |
| Yogg-Saron | Add a random minion from the current tavern tier to hand | 2 gold, once per turn |

## Client architecture

```text
client/
  app.py                  # lifecycle and frame loop
  event_bus.py            # bounded inbound and outbound queues
  state_store.py          # validated immutable snapshots
  command_dispatcher.py   # idempotent player commands
  screens/
    lobby_screen.py
    recruit_screen.py
    combat_screen.py
  components/
    minion_card.py
    shop_panel.py
    hand_panel.py
    board_panel.py
    leaderboard.py
    event_log.py
    choice_dialog.py
  animation/
    timeline.py
    easing.py
```

UI components expose `handle_event`, `update(delta_seconds)`, and `render(surface)`. They never mutate authoritative game state directly.

## Interaction rules

- Dragging must display valid and invalid destination states.
- Invalid drops snap back and create a visible rule message.
- Discover and Choose One dialogs pause ordinary input until resolved.
- The event log shows sequence, step, event kind, and readable message.
- Missing entity references produce a recoverable client warning and do not stop later events.
- Space toggles double-speed combat playback; Shift advances one event in debug mode.

## Animation timing

| Event | Duration | Easing |
|---|---:|---|
| Attack movement | 220 ms | quadratic out |
| Damage response | 120 ms | linear with shake |
| Deathrattle | 300 ms | fade out |
| Summon delay | 80 ms | linear |
| Reborn | 260 ms | ease-out-back |

Animations are presentation only. Their completion must not change gameplay results.

## Acceptance scenarios

1. Reject purchases and refreshes when gold is insufficient.
2. Reject play and summon operations when the board is full.
3. Preserve a frozen shop across the next turn transition.
4. Create a Golden minion and block on a Discover offer after a triple.
5. Replay the same combat seed into the same ordered event sequence.
6. Resolve Taunt, Divine Shield, Deathrattle, summon, and Reborn ordering.
7. Continue processing after a recoverable event references a missing entity.
8. Update all four leaderboard entries after two simultaneous battles.

## Asset handling

Reference art is stored under `bgknowhow-main/images`. Runtime code should load assets through a manifest, provide placeholders for missing files, and avoid hard-coded absolute paths.
