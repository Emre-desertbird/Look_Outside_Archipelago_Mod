# Look Outside Archipelago Mod

An [Archipelago](https://archipelago.gg) integration for **Look Outside**, for solo
randomizer seeds and multiworld games. Explore the building and resolve quests to
send checks; the items at those locations can belong to you or to another player.

> **About this fork.** This is a **vibe-coded extension** of
> [wyldek's original Look Outside Archipelago Mod](https://github.com/wyldek/Look_Outside_Archipelago_Mod),
> written with Claude Code and tested with real seed generation and in-game probes,
> but **not yet with a complete playthrough**. Treat it as an experimental playtest build.
>
> **Huge thanks to wyldek**, who built the actual mod: the 273 audited checks, the
> access and calendar logic, the game plugin and the save handling.

## What the mod changes

| Change | What it means in play |
| --- | --- |
| **273 checks** | Pickups, keys, quest rewards, boss drops and collectibles send a check instead of giving their usual item. [Details](#what-becomes-a-check) |
| **Shuffled items** | Those items (keys, discs, sea valves, the Rose, the Phone, …) are shuffled across your world and other players' worlds and delivered when found. |
| **Virtual unlocks** | **Elevator Access**, **Planetarium Door Access** and **Power Restored** arrive as items instead of being earned in place. |
| **Calendar-aware logic** | Generation respects routes, key counts and quest deadlines (Rose by Day 5, Phone by Day 10, crossword by Day 14), so every seed is completable. |
| **Quest choices still count** | Refusing, fighting or befriending a quest giver completes its whole reward group, so alternate outcomes never lose checks. |
| **Any ending wins** | Any real ending completes your goal and releases your remaining checks. |
| **Safe saves** | A save is bound to its seed and slot; offline checks are sent when you reconnect, and repeated packets never duplicate items. |

Combat, shops, crafting, recruitment, quest dates, the day cycle and story events
stay vanilla. See [What stays vanilla](#what-stays-vanilla).

## What this fork adds

| Addition | Summary |
| --- | --- |
| [Archipelago window and overlay](#the-archipelago-window-and-overlay) | One **Archipelago** menu entry with status, log, items, locations, deadlines and settings, plus a map overlay and a room/quest tracker. |
| Deadline warnings | The overlay and the Deadlines tab warn about the teeth apartment, Charan's Rose and cave, Leigh's Phone quest and the crossword. |
| [Rewarding character quests](#character-quests-always-give-a-useful-item) | Character-quest checks never hold progression, and always hold a useful item. |
| Natural day cycle | The original mod stopped time at 4 a.m. until you chose "Go to Next Day"; days now change as in vanilla. |
| [Optional checks](#yaml-options) | Cooking/crafting, daily-life moments and companion upgrades, each off by default. |
| [DeathLink](#deathlink) | A death in the room takes one random member of your party. |
| [Universal Tracker](#universal-tracker) | Supported, so UT can show your checks in logic. |
| Supply Cache | Filler that grants three random consumables, replacing extra Mops. |
| Rebreather logic | Sea valve areas now logically require the Rebreather, as in vanilla. |
| Small fixes | Item chime, reconnect after loading a save, checks kept after battles, a pasted `/connect host:port` line connects. |

## Quick start

1. **Get the package.** Download [LookOutsideAP-0.0.7-dev74.zip](releases/LookOutsideAP-0.0.7-dev74.zip)
   and follow [Installation](#installation). It builds a **separate modded copy**
   of the game; your Steam installation stays vanilla.
2. **Add the world.** Put `lookoutside.apworld` into Archipelago's `custom_worlds`
   folder and restart Archipelago.
3. **Write your YAML** (see [YAML options](#yaml-options)).
4. **Generate and host.** Generate the seed with Archipelago, then host it on your
   PC (`ArchipelagoServer`) or upload it on [archipelago.gg](https://archipelago.gg)
   under **Host Game**. The website can host this custom world but not generate it.
   Allow release (for example release mode `goal`) so finishing sends your remaining checks.
5. **Play.** Start the modded copy with `LOA_DEV_MODE=1`, begin a **new Survivor
   Mode** game, open **Archipelago** in the pause menu and connect **before picking
   anything up**. Enter the address (for example `archipelago.gg:49170`) and your
   YAML name. No separate client is needed: the game connects to the server itself.

Read [What can play out differently](#what-can-play-out-differently) before your first run.

## Requirements

- Windows Look Outside, build `74642914`, played on **Survivor Mode** (Explorer and
  Cursed Mode are not supported).
- Archipelago `0.6.7` or newer (tested with 0.6.7 and 0.6.8).
- Python 3.10 or newer, only for preparing the mod files once.

## YAML options

```yaml
name: YourName
game: Look Outside
Look Outside:
  activity_checks: false     # cooking/crafting checks (filler only)
  companion_upgrades: false  # companion passives + join checks
  daily_life_checks: false   # first shower/sleep/videogame (filler only)
  death_link: false          # share deaths with the room
```

All options are off by default; a default YAML gives the original 273 checks.

### Activity checks

Adds **Cooking - First Meal**, **Cooking - Third Meal** (meals cooked at the home
oven) and **Crafting - First Item** (needs the Crafting Kit from Apartment 37). You
keep the food and item. Meals and crafts before you connect don't count. These
checks only hold filler, and each adds a **Supply Cache** to the pool.

A **Supply Cache** gives three random consumables: mostly snacks, drinks, basic
medicine and cooking ingredients, sometimes better medicine, meals, alcohol or
throwables. A full stack skips that roll. Reloading never changes what a cache gave.

### Daily-life checks

Adds **First Shower**, **First Night's Sleep** and **First Videogame** at home, using
the game's own "first time" moments after you connect. The videogame check needs
power. They only hold filler, and each adds a Supply Cache.

### Companion upgrades

Adds one **useful** upgrade item per recruitable companion (17), plus a filler-only
**Companion - <Name> Joins** check when each first joins. Upgrades are passives on
top of their normal abilities; one received early applies once they join, and
reloading never stacks them.

| Companion | Passive |
| --- | --- |
| Lyle | **Flash Photography**: Normal attacks may Blind (20%) |
| Aster | **Safety First**: Targeted half as often; +10% evasion |
| Joel | **Gum Regrowth**: Regenerates 5% HP each turn, offsetting his HP-cost teeth skills |
| Leigh | **Unsettling Smile**: Normal attacks may Stun (12%), setting up Devour |
| Dan | **Loyal Fans**: Video intros start with 5 extra viewers |
| Hellen | **Killer Instinct**: +10% critical hit rate |
| Rat Child | **Daddy's Shadow**: Starts battles copying Sam; catches up to two levels below Sam |
| Roaches | **Endless Swarm**: Regenerates 6% HP each turn, fueling HP-cost roach attacks |
| Ernest | **Warm-Up Act**: The party starts battles with Song of Speed |
| Sophie | **Slippery**: Starts battles Hidden and may slip back into hiding |
| Papineau | **Big Guy**: +20% Max HP, which also strengthens Bear Hug |
| Montgomery | **Iron Stomach**: Immune to Poison; half Fire damage |
| Xaria | **Talks Back**: 20% counterattack chance; immune to Panic |
| Morton | **Scavenger**: Enemies drop items twice as often |
| Spider | **Venomous**: Normal attacks may Poison (25%) |
| Audrey | **Coin Return**: Regenerates 10% STM each turn, fueling Keep the Change |
| Phillippe | **Spore Cloud**: Normal attacks may cause Spore Poison (30%), which Assume Control needs |

Wretch, Jacob and Melt never join the party in this game build, so they have no upgrade.

### DeathLink

- **When someone else dies**, one random living member of your party falls. If
  that was your last one, it's a Game Over. While exploring it waits until no
  cutscene or dialogue is running; in a fight it happens at the start of the next turn.
- **Your own Game Overs** are sent to the room, except ones caused by a received death.
- Deaths that arrive while you are offline are lost, as in other Archipelago games.

The Archipelago window shows when DeathLink is on.

### Universal Tracker

[Universal Tracker](https://github.com/FarisTheAncient/Archipelago/releases) can show
which of your checks are in logic. It can't see the in-game day, so day-locked checks
may show early; use the **Deadlines** tab for those.

## What becomes a check

| Source | Examples |
| --- | --- |
| Fixed equipment | Weapon, armor and accessory pickups, including those in safes and locked rooms. |
| Keys and quest objects | Fixed keys, discs, sea valves, the Phone, the Rose, Telescope Pieces, ritual and manuscript items. |
| Collectibles | Playable videogames and the six Kingdoms of the Dump figures. |
| Enemy rewards | Guaranteed boss and enemy drops, and boss salvage (no Audrey needed). |
| Quest rewards | Gifts and quest outcomes; one outcome can complete several checks. |
| Simple Keys | Eight fixed pickups plus Kaeley's and Nestor's keys; the pool has ten **Simple Keys (3)** bundles. |
| Reusable gifts | Scout's **Radio** and Bright Frederic's **Medic-in-a-jar**, which keep recharging as usual. |

A check's name tells you **where** it is (for example **Garage Car Trunk - Shotgun**),
not what it holds. Other sources of the same item, such as shops, random drops or
crafting, stay vanilla, and mixed rewards are split: the car trunk's Shotgun is a
check, its 12 shells are not.

## Quests and checks

### Quest choices count

A quest's final outcome (peaceful, recruited or hostile) completes **all** checks in
its group, including rewards that branch would normally lock out. For example, Joel's
resolution sends both the Door Knob and the Toothy Whip checks, Wilhelmina's sends all
five of her rewards, and closing the fungus illusion sends the remaining rescue checks.
The same applies to Frederic, Jasper, Pierre, Benjamin, Clint, Madison, the Masked
Shadow, Mutt, Tickle, Sybil, Hellen, Dan and others. Starting a quest, fleeing a fight
or getting a Game Over doesn't count as an outcome. Details:
[choice handling](docs/quest_resolution_policy.md).

### Character quests always give a useful item

Character quests can take many days or close on a fixed date, so their **43 checks
never hold progression**: nobody waits behind Roach Leadership or Charan's cave. They
always hold a **useful** item instead, preferably for another player, so finishing one
still feels rewarding. The quest rewards themselves (Papier-Maché Crown, Azure
Greatsword, …) are still in the item pool. This applies to all new seeds.

### Checks that only hold filler

These can be missed, so they never hold progression or useful items:

- Original teeth apartment (closes at **noon on Day 4**): Frying Pan, Hoodie, Mop,
  Baseball Cap, Army Guy Figure, Tank Top, Old Rifle and Baby Teeth's Jawbone Club.
- **Pierre - Old Mail Visit**.
- **Floor 4 Void - Voidblade** (after the Gauntlet, which isn't in logic).

## What stays vanilla

- **Combat**, levels and equipment. Logic never judges whether your party can win a fight.
- **Consumables, ammo, crafting materials and money**: gather, buy or craft them as usual.
- **Shops, random loot, crafting recipes and item transformations** (you repair the
  Telescope and turn the Void Disc into the Negative Disc yourself).
- **Household valuables**, Morton's donation rewards and the whole **Gauntlet**.
- **Time**: days change at 4 a.m.; fixed dates, new-day waits, visitors and dialogue
  cutoffs are untouched.
- Some companion rewards (Ernest's Metal Bat, Hellen's Mask/Cleaver, Juicebox's gifts).

**Electricity:** the building still has its normal blackout. The fuse box is a check;
power only returns when you receive **Power Restored**. If it arrives before the
blackout, the blackout still happens and is fixed at once.

## How the logic works

Generation considers routes, keys, quest items and deadlines, never combat strength.
Routes often have alternatives: the Padlock Key or Apartment 21 lead down, the
powered elevator is another way, and the Basement Key and boiler maze reach the
western basement without power.

Key counts cover every lock, including wrong turns in mazes:

| Resource | In the pool |
| --- | --- |
| Simple Keys | Ten **Simple Keys (3)** bundles for 26 ordinary locks |
| Iris Keys | Seven for six locks |
| Colored keys (Unlabeled Game) | Green, red, blue, white, three yellow and **Black Keys (2)** for nine locks |
| Sea valves | One of each; the sea areas also need the **Rebreather** |

You can use a key as soon as it arrives. Doors that need discs at the same time get
different discs, and the four Astronomer offerings need four different categories
(one Guinea Pig can stand in for one).

**Days:** the calendar starts on Day 0. Generation keeps timed inputs early enough:
the Rose by Day 5, the Phone by Day 10, the crossword book by Day 14. Rooms with a
fixed opening day still open on that day (original teeth Day 1, Apartment 31 Day 2,
Kaeley Day 3, taxidermy Day 4, late teeth Day 8).

## What can play out differently

Story events, quest dates and endings stay vanilla; what changes is **when you get
keys and quest items**.

| Item | What can change |
| --- | --- |
| **Roof Access Key** | Can arrive early. The roof leads to the final fight and an **ending**, so only go up when you are ready to finish. |
| **Elevator Access** | Unlocks the elevator without beating the Elevator Freak (power is still needed). The Freak stays an optional check. |
| **Power Restored** | If received early, the blackout still happens and is fixed at once. |
| **Keys, valves, discs** | Areas can open earlier or later than in vanilla. |
| **Quest items** | Quests can start earlier; carrying the Phone home starts Leigh's quest right away. |
| **Basement Key** | Dan only offers his quest while you hold it. |
| **Apt. 33 Key** | Does nothing; you can't be locked out of your apartment. |

**Timed quests:** in a multiworld, an item you need may be in someone else's world
and arrive late, and days don't wait. A missed timed quest never blocks anyone: those
checks hold no progression, and finishing the game releases them. The **Deadlines**
tab shows what is still open.

**Nothing can lock you out of finishing.** The Day 15 home-door ending is always
available. Nine progression items have no logic rule at all (Child Barrier Key, Door
Knob, Love Letter, Laundry, Small Red Key, Vending Machine Key, Clown Drawing, Roof
Access Key, Apt. 33 Key); they only affect optional vanilla content.

## Winning and release

**Any real ending on any day completes your goal.** From Day 15 the home door offers
the **No Going Back** ending, which works even with unfinished quests. Opening the
credits through cheat mode doesn't count.

When you finish, the game reports the goal and releases your remaining checks: the
items **in your world** go to their owners. It doesn't collect your own items from
other worlds. The host must allow release (`goal`, `enabled`, `auto` or
`auto-enabled`). Finishing offline is saved and reported when you reconnect.

## The Archipelago window and overlay

The pause menu has one **Archipelago** entry. It shows the connection status, your
seed and slot, a progress bar and these tabs:

| Tab | Shows |
| --- | --- |
| **Overview** | Checks (and how many still wait to be sent), items received, goal, calendar, upgrades. Connection settings open while disconnected. |
| **Log** | Server messages, colored as in Archipelago. |
| **Items** | Everything you received, and from whom. |
| **Locations** | Missing checks by area (missing doesn't mean reachable yet). |
| **Deadlines** | The time limits and what each still needs. |
| **Settings** | Overlay and tracker on/off, side, number of log lines, item chime. |

On the map, a small **overlay** shows:

| Row | Shows |
| --- | --- |
| Clock | An analog clock, the day and time, and a connection dot. |
| Progress | **42 / 293 checks**, plus how many still wait to be sent while offline. |
| Deadline | The most urgent one, only when it's close or at risk. |
| Log | The latest messages (0, 3, 6 or 10 lines; 3 by default). |

The **tracker** on the other side shows how many checks are left in the room you're
standing in (with up to three names), the timed quests you have **started**, and items
waiting for bag space. Both hide during dialogue, menus and battles, and can be
switched off in Settings or the game's Options, as can the item chime.

**Connecting:** enter `host:port` (a pasted `/connect host:port` line works too;
`ws://` and `wss://` addresses are accepted), your slot name and the room password if
any. The server and slot are remembered; the password is never saved. If your
inventory is full, received items wait until you make room (a three-key bundle needs
room for all three).

## Installation

The ZIP in [releases](releases/README.md) contains the APWorld, the game plugin, a
preparation script and a sample YAML. No game assets are included.

1. Extract the ZIP into a new folder.
2. Open PowerShell in that folder and run:

   ```powershell
   $gameSource = Read-Host 'Path to your Look Outside installation'
   python .\prepare_mod.py --game-dir "$gameSource"
   ```

   It only reads your game and writes the mod files into `prepared`.
3. Make a **separate copy** of the game (without its `save` folder) and back up that
   copy's `js/plugins.js`.
4. Copy the contents of `prepared/js` into that copy's `js` folder.
5. Put `lookoutside.apworld` into Archipelago's `custom_worlds` folder and restart Archipelago.
6. Launch the copy with `LOA_DEV_MODE=1` and start a new Survivor Mode game.

To remove the mod, restore the copy's original `js/plugins.js` and delete
`js/plugins/LookOutsideArchipelago.js`. More detail: [package setup guide](docs/package_setup.md).

## Troubleshooting

| Situation | What to do |
| --- | --- |
| No Archipelago menu entry | Launch the modded copy with `LOA_DEV_MODE=1`. |
| No Archipelago pop-up after launching | None is expected: open the pause menu and choose **Archipelago**. |
| Connection refused for difficulty or build | Use Survivor Mode and the supported game build. |
| "Save is ineligible" on first connect | Start a fresh save and connect before picking anything up or advancing a day. |
| Wrong seed or slot | Load that slot's own save, or start a fresh one. A save can't be moved to another slot. |
| Items haven't appeared | Check the Overview and Items tabs, and make inventory space. |
| Can't connect to a hosted room | Enter only `host:port`. archipelago.gg rooms change port after sleeping; check the room page. |
| Goal counted but checks weren't released | Reconnect, or ask the host to allow release. |
| Save error after updating | Keep the old package for unfinished runs, or start a new seed. New logic only applies to new seeds. |

## Credits and license

- **Original mod: [wyldek](https://github.com/wyldek)** —
  [Look_Outside_Archipelago_Mod](https://github.com/wyldek/Look_Outside_Archipelago_Mod).
  The checks, logic, game plugin and save handling are wyldek's work. Thank you!
- **This fork: [Emre-desertbird](https://github.com/Emre-desertbird/Look_Outside_Archipelago_Mod)** —
  a vibe-coded extension written with Claude Code.
- **Look Outside** belongs to its developers; no game assets are included.
  [Archipelago](https://github.com/ArchipelagoMW/Archipelago) is the multiworld
  framework this mod plugs into.

Released under the [MIT License](LICENSE).
