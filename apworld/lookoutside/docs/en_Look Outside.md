# Look Outside (development playtest)

This APWorld supports Survivor Mode (Normal difficulty). Explorer Mode and Cursed Mode sessions are rejected.

<!-- BEGIN GENERATED REGISTRY SUMMARY -->
Registry **74** provides **273 checks**: 167 equipment copies, 103 physical items and 3 access unlocks.
All checks have access rules across **74 regions and 81 entrances**,
with **36 quest-resolution groups**.
The solver also uses **19 generation-only calendar events**, outside the item pool.
<!-- END GENERATED REGISTRY SUMMARY -->

New seeds use `chronological_access_v1`, with generation-only calendar events
for fixed openings and audited deadlines. These reserve a prompt progression
path without enforcing the runtime clock or the player's choices. Generate a
new seed to apply the rules; registry74's plugin remains compatible.

Fixed equipment and the reviewed key/collectible sources are randomized.
Household valuables, crafting materials, consumables, purchases, random loot,
the reviewed companion rewards, Morton donations and the Gauntlet stay vanilla.
The approved fixed Simple Key sources provide bundles sufficient for ordinary
locks. Access logic checks routes and required objects; combat preparation is
left to the player. Quest choices reconcile their reviewed reward groups.

Optional `activity_checks` (off by default) adds three filler-only checks:
cooking your first and third meal, and crafting your first item. You keep the
food and crafted item. Each adds one Supply Cache (three random consumables) to
the pool.

Optional `daily_life_checks` (off by default) adds three filler-only checks for
your first shower, first night's sleep and first videogame.

Optional `death_link` shares deaths with the room: a received death takes one
random party member (Game Over if none remain), and your own Game Overs are sent,
except ones a received death caused. The world also supports Universal Tracker.

Optional `companion_upgrades` (off by default) adds 17 useful upgrade items, one
per recruitable companion, and a filler-only check when each first joins. Each
upgrade is a passive fitting that companion: for example, Sophie starts every
battle Hidden and can slip back into hiding, Rat Child starts battles copying
Sam and catches up in level, Ernest opens battles
with Song of Speed, and Phillippe's attacks spread the spores Assume Control
needs. Upgrades received before recruitment apply once that companion joins.

Power Restored waits for the native outage if received early, then restores
electricity with a notice. The fuse-box check remains available independently.
Native quest dates and new-day waits remain in place. Any real ending completes
the goal on any day; the Day15 home-door ending is the fallback for unfinished
quests. Ending release requires host support. Cheat-mode Credits do not count.

The complete access graph and acquisition inventory are reviewed. A full Normal
playthrough remains the release gate. Use a fresh save/seed and a matching
APWorld/plugin pair; save schema7 rejects incompatible AP saves. Follow the
[setup guide](setup_en.md) for installation and compatibility details.
