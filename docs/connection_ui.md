# Connection and item feedback

The development game menu has one **Archipelago** entry. Its window has
Overview, Log, Items, Locations, Deadlines and Settings tabs; connection settings
are on Overview and open automatically while disconnected. It accepts a server address with or without `ws://` or `wss://`, a slot
name, and an optional masked password. Server and slot are remembered in the local NW.js
profile. The password is never written to preferences or the AP save field.

Bare addresses initially use `ws://`. If that transport fails before opening
or receiving a message, the plugin tries `wss://` on the same host/port. This
supports hosted rooms requiring TLS, as in
[Archipelago's standard client](https://github.com/ArchipelagoMW/Archipelago/blob/0.6.7/CommonClient.py#L801-L805).
An explicit `wss://` address and an opened secure connection never retry in
plaintext. AP authentication/protocol errors also never trigger transport changes.
If both opening attempts fail, normal reconnect backoff restarts the original
request, allowing a temporarily offline plain server to recover.

The successful address, including the secure scheme after fallback, is remembered
for later connections. Status displays the current address; failed connections
identify the attempted host/port. In the original `0.0.2-dev74` tagged package,
automatic secure retry is absent: enter `wss://host:port` explicitly for TLS rooms.

Connection state, errors, seed binding, check count, queued items, and calendar
hold are shown in the dialog. Disconnect cancels automatic retries while
preserving the bound save, its offline checks, and pending deliveries. Invalid
settings or a failed socket constructor leave an existing connection intact.
Save/build/difficulty guards apply to connections started from the menu as well
as the development API.

Delivered items produce a nonblocking six-second notice when the map is idle.
Large batches show three names and the number of additional items. The latest
received items are listed on the Items tab with sender and location, for the
current game session. While the log overlay is on, it replaces this notice.

The map overlay has four compact rows: an analog clock with the day and time
(and *(held)* at the 4 a.m. stop) plus a connection dot; a check progress bar
with the server's count; the single most urgent deadline, only when one closes
within two days or is at risk; and the latest log lines (0, 3, 6 or 10; default
3). It refreshes at most four times a second.

The tracker sits on the opposite side, below the game's menu button. It shows the
checks left in the current map (registry sources with a map; battle and common-event
checks have no room), up to three of their names once the data package is known,
timed quests the player has started (Charan's cave after the Rose is given, Leigh's
Phone once charging, the crossword after the first puzzle), and items waiting for bag
space. It has its own switch (*Archipelago Tracker* in Options, saved in the config).

The Log tab and overlay show the server's messages (item sends, hints, goals,
chat) with names from the room's data package, plus local lines for connecting,
offline checks, Supply Cache contents and companion upgrades. Other players'
item sends stay in the Log tab. The overlay is a small transparent box on the
left or right edge of the game area; older log lines fade. It is pointer-transparent, hidden during dialogue, menus and battles,
and switched in Settings or the game's Options (*Archipelago Log*, saved in the
game config). Nothing it shows changes checks, items or game time. Replayed packets and inventory-full queues do not announce an item
until it has actually been delivered. Power Restored retains its dedicated
outage/restoration messages.

Go to Next Day asks for confirmation, with Keep exploring focused by default.
Confirming advances exactly once through the existing native calendar hook.
Eight expiring teeth-apartment checks are listed on the Deadlines tab and in the day
confirmation before their Day 4 noon deadline. Checked entries disappear from
the list. The broader expiry audit remains unfinished; see `calendar_deadlines.md`.

Three audited quest cutoffs are also listed, read from native state:
- **Charan's Rose** (switch680) closes on Day6; then **Charan's Cave** on Day7 or once
  the earthquake (switch1097) starts. It says if the Rose (item360) is not in the inventory.
- **Leigh's Phone**: carry the Phone (item389) home by Day10. Once started
  (variable900), it shows the remaining new days, an unread message, and that
  the fourth message needs Leigh living with you (switch34). It flags the quest
  once the remaining days no longer fit before Day15.
- **Crossword book**: 100 puzzles (variable491) before Day15, with progress and a
  note if the book (switch237) is not picked up yet. It is hidden once any
  Wilhelmina reward is checked.

Status lists every open quest cutoff. Go to Next Day lists one when its day
is next, or from Day4 (Rose), Day8 (Phone), Day11 (crossword), or the last day
on which Leigh's remaining steps still fit. Warnings never block advancing.

The dialog uses keyboard and pointer input. It isolates text entry from RPG
Maker's game key handlers and clears held input on open/close. Scene changes or
a new game remove the dialog and its status timer. The layout is sized for the
game's 816 x 624 window; long status content scrolls with the buttons retained.

`tests/native_menu_probe.js` exercises 12 scenarios in the staged NW.js runtime:
focus/input isolation, bad settings, connection/status/password persistence,
delivery/replay, full inventory, constructor failure with a live connection,
offline disconnect, Escape, day cancellation/confirmation with a deadline list,
the deadline's noon warning, and new-game cleanup.
These are simulated server interactions; the separate protocol smoke test uses
a real local Archipelago server.

The plugin regression suite also verifies secure retry, identity/item replay,
secure reconnects, recovery of offline plain servers, cancellation, and rejection
paths. A live transport probe confirmed ws failure followed by wss RoomInfo on
a hosted room, suppressing Connect so no slot, checks, or chat were affected.
