# Look Outside Archipelago Mod

An [Archipelago](https://archipelago.gg) integration for **Look Outside**, for solo
randomizer seeds and multiworld games. Explore the building and resolve quests to
send checks; the items at those locations can belong to you or to another player.

> **About this fork.** This repository is a **vibe-coded extension and improvement
> attempt** of [wyldek's original Look Outside Archipelago Mod](https://github.com/wyldek/Look_Outside_Archipelago_Mod).
> The additions here were written with an AI coding assistant (Claude Code) and
> reviewed by running the project's tests, real seed generation and in-game probes,
> but **not yet by a complete playthrough**. Treat it as an experimental playtest build.
>
> **Huge thanks to wyldek**, who built the actual mod: the audited registry of
> 273 checks, the access and calendar logic, the game plugin, the save handling and
> the extensive native test suite. This fork stands entirely on that work.

**This is a development playtest build.** New AP sessions require `LOA_DEV_MODE=1`;
the launchers and commands below set it for you.

## What the mod changes in Look Outside

The original mod by wyldek turns Look Outside into an Archipelago game. In short:

| Change | What it means in play |
| --- | --- |
| **273 checks** | Reviewed pickups, keys, quest rewards, guaranteed boss/enemy drops and collectibles send a check instead of giving their usual item. [Details](#what-becomes-an-ap-check-or-item) |
| **Shuffled items** | Those items, including keys, discs, sea valves and quest objects such as the Rose and the Phone, are shuffled across your world and other players' worlds and delivered when found. |
| **Virtual unlocks** | **Elevator Access**, **Planetarium Door Access** and **Power Restored** arrive as items instead of being earned in place. [Electricity](#electricity) |
| **Logic that respects the calendar** | Generation knows routes, key budgets and audited quest deadlines (Rose by Day 5, Phone by Day 10, crossword by Day 14), so every seed is completable. [How it works](#how-progression-logic-works) |
| **Quest choices still count** | Refusing, fighting or befriending a quest giver resolves its whole reward group, so alternate outcomes never lose checks. [Resolutions](#quest-choices-and-shared-resolutions) |
| **Day hold** | Time stops at 4 a.m.; you choose when to start the next day with **Go to Next Day**, so another player can send you something first. |
| **Any ending wins** | Any real ending completes your goal and releases your remaining checks. The Day 15 home door is always available as a fallback. [Winning](#winning-missed-checks-and-release) |
| **Safe saves** | A save is bound to its seed and slot; checks found offline are sent when you reconnect, and repeated packets never duplicate items. |

Everything else stays vanilla: combat, shops, crafting, recruitment, quest dates
and story events. See [What stays vanilla](#what-stays-vanilla).

## What this fork adds

| Addition | Summary |
| --- | --- |
| [Archipelago window and overlay](#playing-the-archipelago-window-and-overlay) | One **Archipelago** menu entry (Connect and Status merged) with Overview, Log, Items, Locations, Deadlines and Settings tabs, plus a small map overlay with a clock, the day, your check progress, the nearest deadline and recent messages, and a tracker with the checks left in the current room and your started timed quests. |
| [Quest deadline warnings](#days-and-chronological-safety) | Status and Go to Next Day warn about Charan's Rose and cave, Leigh's Phone quest and the crossword book, with the missing item and progress. |
| [Optional activity checks](#optional-activity-checks) | `activity_checks`: cooking your first and third meal and crafting your first item. Filler only; you keep the food and item. |
| [Optional companion upgrades](#optional-companion-upgrades) | `companion_upgrades`: one passive per recruitable companion (17) plus a filler-only check when each first joins. |
| [Supply Cache](#optional-activity-checks) | Filler that grants three random consumables, replacing extra Mops. |
| [Rebreather logic](#access-supplies-and-alternatives) | Sea valve areas now logically require the Rebreather, matching vanilla. |
| Small fixes | Difficulty is named **Survivor Mode** as in the game, and a pasted `/connect host:port` line connects. |

Both options are **off by default**, so a default YAML produces the same 273
checks as the original mod.

## Quick start

1. **Get the package.** Download [LookOutsideAP-0.0.5-dev74.zip](releases/LookOutsideAP-0.0.5-dev74.zip)
   and follow [Install the extracted package](#install-the-extracted-package). It
   builds a **separate modded copy** of the game; your Steam installation stays vanilla.
2. **Add the world.** Put `lookoutside.apworld` into Archipelago's `custom_worlds`
   folder and restart Archipelago.
3. **Write your YAML.** Pick your player name and options:

   ```yaml
   name: YourName
   game: Look Outside
   Look Outside:
     activity_checks: false     # cooking/crafting checks (filler only)
     companion_upgrades: false  # companion passives + join checks (filler only)
   ```

4. **Generate and host.** Generate the seed with Archipelago, then host it on your
   PC (`ArchipelagoServer`) or upload the generated ZIP on
   [archipelago.gg](https://archipelago.gg) under **Host Game**. The website
   cannot *generate* this custom world, but it can host a seed you generated.
5. **Play.** Start the modded copy with `LOA_DEV_MODE=1`, begin a **new Survivor
   Mode** game, open **Archipelago** in the pause menu and connect before picking
   anything up. Enter just the address (for example `archipelago.gg:49170`) and
   your YAML name. No separate Archipelago client is needed: the game connects
   to the server itself.

Read [What can play out differently from vanilla](#what-can-play-out-differently-from-vanilla)
before your first run.

## Contents

- [Supported version and scope](#supported-version-and-scope)
- [What becomes an AP check or item](#what-becomes-an-ap-check-or-item)
- [What stays vanilla](#what-stays-vanilla)
- [How progression logic works](#how-progression-logic-works)
- [What can play out differently from vanilla](#what-can-play-out-differently-from-vanilla)
- [Winning, missed checks, and release](#winning-missed-checks-and-release)
- [Playing: the Archipelago window and overlay](#playing-the-archipelago-window-and-overlay)
- [Setup guide](#setup-guide)
- [Saves, updating, and troubleshooting](#saves-updating-and-troubleshooting)
- [Verification and developer references](#verification-and-developer-references)
- [Credits and license](#credits-and-license)

## Supported version and scope

| Component | Current target |
| --- | --- |
| Game | Windows Look Outside, game ID `51778622`, build `74642914` |
| Difficulty | **Survivor Mode** (Normal); Explorer Mode and Cursed Mode cannot activate this APWorld |
| Archipelago | Minimum client version `0.6.7`; tested with Archipelago `0.6.7` and `0.6.8` |
| Registry / save format | Registry **74**, AP save schema **7**, mod version `0.0.5` (APWorld and plugin) |
| Generation logic | `chronological_access_v1` |
| Randomized pool | **273 locations and items** by default; 276 with `activity_checks`, 290 with `companion_upgrades`, 293 with both |
| Item classification | Default pool: 81 progression, 122 useful, 70 filler **copies** |
| Access graph | 74 regions, 81 entrances, a rule for every randomized location |
| Quest handling | 35 shared resolution groups |

The 273 default item copies comprise **70 weapons, 97 armor/accessories, 103 other
physical items, and three virtual access unlocks**. There are 64 distinct items
classified as progression. That classification does not always mean the item
gates an AP location; see the [internal item reference](docs/internal_progression_item_limits.md).

Your installed Look Outside and Archipelago folders are treated as
**read-only sources**. Their locations are supplied during setup.
All working copies, saves, profiles, generated seeds, and build outputs belong
inside this project. Game assets are not distributed with the mod.

## What becomes an AP check or item

A **location/check** is an audited acquisition or quest milestone. Completing it
sends its location ID to Archipelago and suppresses the randomized vanilla reward
at that source. The server determines the replacement item and its recipient.
Checking a location does not guarantee receiving its original item or receiving
anything locally at that moment. Names such as **Garage Car Trunk - Shotgun**
identify the vanilla source, not the item a generated seed places there.

Interception is specific to the source. Another source of the same item can remain
vanilla, such as a purchase, random drop, or crafting recipe.

| Included source or item category | Scope |
| --- | --- |
| Fixed equipment | Reviewed weapon, armor, and accessory pickups, including equipment in safes and locked rooms. |
| Keys and quest objects | Reviewed fixed keys, discs, sea valves, manuscript/ritual inputs, Phone, Rose, Telescope Pieces, and other registered quest items. |
| Collectibles | Reviewed playable videogames, the six named Kingdoms of the Dump figures, and other explicitly registered collectibles. Ordinary household valuables are separate. |
| Persistent enemy rewards | Reviewed guaranteed drops and boss salvage. Alternate appearances of the same encounter share a check where registered. Boss salvage checks do not require Audrey. |
| Quest rewards | Audited gifts, intermediate rewards, and shared terminal resolutions. The exact membership of each group is fixed in the registry. |
| Simple Keys | Eight fixed pickups and the approved Kaeley/Nestor drops become ten checks; the pool contains ten **Simple Keys (3)** bundles. Purchases and random keys stay vanilla. |
| Reusable gifts | Scout's **Radio** and Bright Frederic's **Medic-in-a-jar** are useful AP items with their native recharge behavior. |
| Other reviewed acquisitions | The first Metal Detector, Comatus's Whisperblade, fungus rescue equipment, Darryl's Legs, Spider Husk's Beating Heart, and the shared bookshelf Screamatorium reward. |
| Virtual unlocks | **Elevator Access**, **Planetarium Door Access**, and **Power Restored** arrive as permanent access state instead of inventory objects. Their source checks remain separate. |

The eight fixed Simple Key pickups are in Apartment 36 Bedroom, Corner Store,
Ground Floor Janitor Closet, Floor 3 Janitor Closet, Eye Apartment, Garage Side
Room, Rat Lair North, and Basement Storage. Nestor's early, rooted, and mound
body victories resolve one shared key check. Kaeley's guaranteed key drop is the
explicitly approved exception to excluding standalone friendly-kill checks.

### Optional activity checks

Set `activity_checks: true` in the player YAML to add three checks:
**Cooking - First Meal**, **Cooking - Third Meal** and **Crafting - First Item**.
Cooking counts meals that finish at the home oven. Crafting counts the first
successful recipe at the crafting table, which needs the Crafting Kit from
Apartment 37. The food and crafted item stay yours; nothing vanilla is suppressed.

These locations are **excluded**: they only ever hold filler, for you or another
player, so skipping cooking or crafting never blocks anyone. Each adds one
**Supply Cache** to the pool.

A **Supply Cache** is filler that gives three random consumables when received:
snacks, drinks, basic medicine and cooking ingredients are common; better medicine,
meals, alcohol and throwables are rarer. Rolls depend on the seed and the item's
receive order, so a reload or replayed packet gives the same items. A full stack
skips that roll. Supply Caches also replace generic filler (formerly extra Mops). With the option off,
seeds keep the same 273 locations and items. The plugin enables these checks only
when the seed's slot data says so; meals and crafts before connecting do not count.
Activity checks use their own IDs (`5930000xx`) outside registry74, so existing
registry74 seeds and saves stay compatible.

### Optional companion upgrades

Set `companion_upgrades: true` to add one **useful** upgrade item per recruitable
companion (17 items), plus a **Companion - <Name> Joins** check the first time
each one enters your party. Join checks are excluded (filler only), because
recruitment depends on visitors and choices. Recruitment itself stays vanilla.

Each upgrade is a **passive** that fits that companion's playstyle and adds to
their normal abilities; nothing is removed. An upgrade received before that
companion joins is kept and applies once they do. Effects are recalculated from
saved ownership, so reconnecting, reloading or a replayed item packet never stacks
them. They only apply in a bound AP save.

| Companion | Passive |
| --- | --- |
| Lyle | **Flash Photography**: Normal attacks may Blind (20%) |
| Aster | **Safety First**: Enemies target him half as often; +10% evasion |
| Joel | **Gum Regrowth**: Regenerates 5% HP each turn, offsetting his HP-cost teeth skills |
| Leigh | **Unsettling Smile**: Normal attacks may Stun (12%), setting up Devour |
| Dan | **Loyal Fans**: Each video intro starts with 5 extra viewers |
| Hellen | **Killer Instinct**: +10% critical hit rate |
| Rat Child | **Daddy's Shadow**: Starts every battle already copying Sam (Copy Dad), and catches up to two levels below Sam |
| Roaches | **Endless Swarm**: Regenerates 6% HP each turn, fueling HP-cost roach attacks |
| Ernest | **Warm-Up Act**: The party starts every battle with Song of Speed |
| Sophie | **Slippery**: Starts every battle Hidden; at the end of a turn when she is neither Hidden nor drawing attention, 50% chance to slip back into hiding |
| Papineau | **Big Guy**: +20% Max HP, which also strengthens Bear Hug |
| Montgomery | **Iron Stomach**: Immune to Poison; takes half Fire damage |
| Xaria | **Talks Back**: 20% counterattack chance; immune to Panic |
| Morton | **Scavenger**: Enemies drop items twice as often while Morton is in the party |
| Spider | **Venomous**: Normal attacks may Poison (25%) |
| Audrey | **Coin Return**: Regenerates 10% STM each turn, fueling Keep the Change |
| Phillippe | **Spore Cloud**: Normal attacks may infect with Spore Poison (30%), which Assume Control needs |

Chances and percentages are deliberately modest. "Normal attacks" includes any
skill that applies the attacker's on-hit states, as the game's own attack does.

Wretch, Jacob and Melt are not included: build 74642914 never adds them to the
party. These locations use IDs
`5940000xx`; upgrade items use `5404000xx`.

### Quest choices and shared resolutions

An audited terminal outcome completes the qualifying checks in its resolution
group, including rewards that the chosen branch makes unavailable. Native story
consequences still happen. Starting a quest, postponing an available offer,
escaping an unfinished fight, or getting a game over does not generally resolve it.

For example, **Joel Resolution** sends both the Door Knob and Toothy Whip checks
through his audited peaceful, recruitment, or hostile outcomes. Those remain two
AP locations and two item copies, collected by one resolution. Wilhelmina's
resolution reconciles her five mutually exclusive reward checks. Closing the
fungus illusion resolves the remaining rescue checks; an individual rescue
checks only that person's reward.

The 35 groups also cover reviewed branches of Frederic, Jasper, Pierre, Benjamin,
Clint, Madison, the Masked Shadow, Mutt, Tickle, Juicebox's card trick, Rat Freak,
Sybil, Hellen, Dan, High Five, and other registered resolutions. This does not
preserve every quest indefinitely or change its native dates. See
[choice handling](docs/quest_resolution_policy.md) for the audited outcomes.

### Nine locations can contain only filler

These missable checks cannot hold progression or useful items:

- Original teeth apartment: Frying Pan, Hoodie, bathroom Mop, west-bedroom
  Baseball Cap, east-bedroom Army Guy Figure and Tank Top, safe Old Rifle,
  and Baby Teeth's Jawbone Club.
- **Pierre - Old Mail Visit**.

The original teeth entrance closes at **noon on Day 4**. Its location labels use
Apartment 32; the access graph calls this region **Original Teeth Apartment**.
Other timed quests are not automatically restricted to filler.

## What stays vanilla

| System or source | Preserved behavior |
| --- | --- |
| Combat | Enemy behavior, battles, levels, party preparation, and equipment use. AP does not judge whether your party can win. |
| Local supplies | Food, healing, ammunition, other consumables, crafting materials such as Junk/Duct Tape, and local currency. Gather, buy, or craft them normally. |
| Shops and random loot | Stock, purchases, repeat purchases, random loot, and random key grants. Metal Detector replacement purchases also stay vanilla. |
| Household valuables | Jewelry boxes, comic books, old consoles, Spirit Board, and the excluded taxidermy valuables used for selling/gifts. Wearable equipment jewelry can still be randomized. |
| Crafting and transformations | Original recipes, inputs, consumption, and outputs. AP inputs are used normally: Telescope Pieces are repaired locally, and Void Disc becomes Negative Disc locally. Conversions add no AP checks. |
| Selected companion rewards | Ernest's Metal Bat; Hellen's Paper Mask/Cleaver; Juicebox's battle-assistance gifts; Marc-Andre's recruitment item and cooldown forms. This exemption does not include every reward involving those characters. |
| Morton donations | Junk donation rewards, including the fixed equipment milestones. |
| Gauntlet | The entire area, its entrance key, and all rewards. |
| Excluded friendly-kill routes | Eugene's locked rooms, Lyle's Dark Room, and their keys/interior rewards; other unapproved standalone friendly-kill rewards. Audited shared quest resolutions and approved key drops are the stated exceptions. |
| Quest and visitor timing | Fixed dates, real new-day waits, hourly stages, visitor behavior, and dialogue cutoffs. AP does not rewrite quest stages to recover a missed deadline. |
| Recharges | Radio recharges after eight native hours; Medic-in-a-jar rests until a real new day. Recharging creates no extra check or AP copy. |

Mixed rewards are split at the audited grant: the car trunk's Shotgun is an AP
check, while its **12 shells remain vanilla**. Unregistered sources retain their
native behavior even when they grant an item also found in the AP pool.

### Electricity

The building starts with electricity and undergoes its normal outage. The main
fuse box is a check; restoration is the separate **Power Restored** item.

- Received before the outage: ownership is saved, then the native power-loss
  event runs before immediate restoration. An explicit loss/restoration message
  and native sounds make both events visible.
- Received after the outage: power returns when the item is delivered.
- Fuse box checked first: it sends its check, but power waits for the item.
- Power restored first: the fuse-box check is still available.

See [power progression](docs/power_progression.md) for the exact hooks.

## How progression logic works

### Access, supplies, and alternatives

Generation considers **routes, keys, quest inputs, finite item counts, and audited
calendar ordering**. It does not require weapon tiers, armor strength, levels, or
combat party composition. A fight can still be mandatory in the game. Cowboy
Hat (Lucky) is progression because it is a quest input, not because of its stats.

Vanilla supplies such as herbicide, salt/ice-melting items, and rent money are
assumed obtainable locally. The solver does not require a particular fixed supply
pickup. This assumption does not replace the AP key budgets.

Routes can have alternatives. Padlock Key reaches the stairwell and Floor 2;
Apartment 21 provides a route to Floor 1. The powered elevator is another way
down. Basement Key and the boiler maze can reach the western basement without
restored power, so the fuse box and elevator encounter are reachable independently
of their own randomized rewards.

| Finite resource | Generation requirement |
| --- | --- |
| Ordinary locks | Nine Simple Keys (3) receipts, or 27 keys, for any reviewed ordinary lock. The pool supplies ten bundles/30 keys for all 26 locks, including vanilla-only safes and every maze turn. |
| Iris locks | Six Iris Key receipts cover six spends in any order; seven copies are in the pool. |
| Unlabeled Game | Cartridge plus all colored-key supplies: one each green/red/blue/white, three yellow, and one Black Keys (2) receipt. Together they cover nine locks. |
| Sea valves | One copy of each of the four playable valves, each for its own lock. The West, East and Lower areas (and the Depths) also require the **Rebreather**, which vanilla hands out before any valve door; without it each air bubble refills about half as much oxygen. |

These are conservative **placement rules**. The game lets you use a key as soon
as it arrives; it does not make you wait for nine bundles before opening a door.
AP tracks received-item history, so the budgets prevent logical reuse of a key
that the game has consumed.

Disc logic assigns **distinct physical discs** to doors that must remain open
together. It includes powered doors, the elevator alternative, the four-socket
balance gate, and the nine-disc astrolabe. Void Disc's Negative form requires
Apartment 31 access; logic does not depend on retaining the original form after
that irreversible conversion. Astronomer offerings likewise need four categories;
one Guinea Pig substitutes for only one category.

### Days and chronological safety

The native calendar starts on **Day 0**. At the native **4 a.m. boundary**, time
holds until you choose **Go to Next Day**. The calendar caps at Day 15; it never
runs extra new-day cycles while pretending to remain on Day 15. Local hourly
actions do not substitute for a quest's required real new day.

Generation uses 15 day milestones and four action events to reserve a feasible
ordering. These **19 events are internal to the solver**: they are not randomized
items, client checks, or runtime requirements for advancing the day.

| Required action | Reserved timing |
| --- | --- |
| Reach/open the original teeth safe | Nine Simple Key bundles and its route by Day 4, with a prompt visit before noon. This constrains logical Day 5. |
| Deliver Rose to Charan | By Day 5, leaving the next real day for his cave on Day 6 before the Day 7 closure. This constrains logical Day 6. |
| Start Leigh's Phone quest | Phone and Floor 2 access by Day 10; read messages and progress over four real new days, finishing the conversation by Day 14. This constrains logical Day 11. |
| Finish Wilhelmina's crossword | Apartment 21's vanilla book and home crossword work by Day 14. Work is disabled on Day 15. This constrains logical Day 15; Pluto access can come later. |

Fixed openings are modeled: original teeth Day 1, Apartment 31 Day 2, Kaeley's
apartment Day 3, taxidermy Day 4, and late teeth Day 8 after 06:00. Logical rewards
reserve enough time: Louis's body drops Day 5, Charan's cave Day 6, shared Shadow
rewards Day 8, Leigh's reward Day 14, and Juicebox's card trick Day 15. Some can
be collected earlier in native play.

These dependencies work through item chains and across players. Rose cannot be
placed behind a late opening, or behind a key that itself requires that late
opening. Merely calling its immediate location an early room does not bypass
the rule. New generation is necessary to apply these rules to an older seed.

**Limits:** this is a targeted calendar model, not a simulation of every action
or visitor schedule. You can still advance too soon, miss a visitor, or spend
too long near an intraday cutoff. The Deadlines tab lists only the audited deadlines.
Visitor-order variation, repeated Shadow encounters, and travel time near
deadlines need full chronological playtesting. See
[calendar evidence](docs/calendar_deadlines.md) and
[per-item limitations](docs/internal_progression_item_limits.md).

## What can play out differently from vanilla

Story events, quest dates, recruitment and endings stay vanilla. What changes is
**when you get keys and quest items**, so some parts of the game can open earlier
(or later) than in a normal run. Generation guarantees every check stays reachable;
these are the effects worth knowing:

| Item | What can change | What to know |
| --- | --- | --- |
| **Roof Access Key** | Normally a late ritual reward; it can arrive at any time and open the roof door early. | The roof leads to the final fight and an **ending**; the game warns *"There is no going back after this."* Losing that fight is a vanilla Game Over (reload your save). Winning ends your run: goal complete, remaining checks released. **Only go up when you are ready to finish.** |
| **Elevator Access** | Unlocks the elevator without beating the Elevator Freak (power is still needed). | The Freak stays as a separate optional check and only fights when you talk to it. |
| **Power Restored** | If received early, the blackout still happens and is fixed at once. | The two dark-basement encounters stay available even though the blackout scene is skipped. |
| **Keys, valves, discs** | Areas can open earlier or later than in vanilla. | Rooms with a fixed opening day still open on that day: original teeth Day 1, Apartment 31 Day 2, Kaeley Day 3, taxidermy Day 4, late teeth Day 8. Key budgets cover every lock, including wrong turns. |
| **Quest items** (Rose, Phone, Telescope Pieces, Canvas Carry Bag, Stationery, Fountain Pen, Radio, Medic-in-a-jar) | Quests can be done earlier, for example carrying the Phone home starts Leigh's quest right away. | Early delivery is covered by the native probes, including items that arrive before you meet the giver. |
| **Basement Key** | Dan only offers his quest while you hold it. | Dan's check already requires it in logic; a late key just delays that quest. |
| **Apt. 33 Key** (your home key) | Nothing: the game never checks for it. | You cannot be locked out of your apartment. |

**Timed quests.** Generation keeps the inputs early enough: Rose reachable by Day 5,
Phone by Day 10, nine key bundles by Day 4, the crossword book by Day 14. In a
multiworld a needed item may sit in a friend's world, so check the **Deadlines**
tab before using Go to Next Day.

**Nothing can lock you out of finishing.** The Day 15 home door ending is always
available and completes the goal. Nine progression items have no logic rule at
all (Child Barrier Key, Door Knob, Love Letter, Laundry, Small Red Key, Vending
Machine Key, Clown Drawing, Roof Access Key, Apt. 33 Key); they only affect
optional vanilla content.

## Winning, missed checks, and release

**Any real ending on any day completes the AP goal.** There is no Day 15 minimum
for actual play. Opening Credits through cheat mode does not count.

At Day 15, the home door offers **Keep exploring** or the original generic
**No Going Back** ending. That ending works with unfinished quests. Generation
proves access to this Day 15 fallback through its calendar reservations; this
does not change which earlier endings the client accepts.

On completion, the client reports the goal and requests `!release` for remaining
unchecked locations. The host must permit release with `goal`, `enabled`, `auto`,
or `auto-enabled`. Release sends the items **located in your world** to their
recipients. It does not collect your items still in other players' worlds or
complete native quests. Offline completion is saved and reported on reconnect.

Ending release recovers checks missed during play; generation does not use it
to justify the audited impossible deadline chains. If release is disabled, the
goal still counts, but remaining checks need a host permission change. See
[ending behavior](docs/ending_release.md).

## Playing: the Archipelago window and overlay

The pause menu has one **Archipelago** entry. Its window shows a status pill
(Connected, Connecting, Offline, Error), your seed, slot and server, a progress
bar and these tabs:

| Tab | Shows |
| --- | --- |
| **Overview** | Cards for checks (and how many are waiting to be sent), items received, goal, calendar and companion upgrades. Connection settings open automatically while disconnected. |
| **Log** | Server messages in Archipelago's usual colours for players, items and locations. |
| **Items** | Everything you received: "found at" a location, or "from" another player. |
| **Locations** | Missing checks grouped by area. Missing does not mean reachable yet. |
| **Deadlines** | The audited time limits and what each still needs. |
| **Settings** | The log overlay: on/off, left or right side, 3, 6 or 10 lines. |

The **overlay** is a small transparent box in a corner of the game area:

| Row | Shows |
| --- | --- |
| Clock | An analog clock (warm by day, blue at night), **Day 3 · 10:30**, *(held)* at the 4 a.m. stop, and a connection dot. |
| Progress | A thin bar and **42 / 293 checks**, plus how many are still waiting to be sent while offline. |
| Deadline | Only when one is close (within two days) or at risk: the single most urgent one, e.g. **⚠ Original teeth apartment · closes Day 4, 12:00**. Optional timed quests count only once you have started them. |
| Log | The latest 3 messages by default (0, 3, 6 or 10 in Settings): items found and sent, Supply Cache contents, upgrades, offline checks. Older lines fade. |

The **tracker** sits on the opposite side, below the game's menu button:

| Section | Shows |
| --- | --- |
| This room | How many checks in the room you are standing in are still left, with up to three of their names; "All found ✓" when done. Checks earned only in battles or common events have no room and count only in the progress bar. |
| Quests | Timed quests you have **started**, with progress: Leigh's Phone (new days or the next step), Charan's cave after giving him the Rose, the crossword once you have solved a puzzle. Unstarted optional quests stay hidden; the Deadlines tab lists them all. |
| Waiting | Only when received items need bag space. |

Both panels hide during dialogue, menus and battles, let clicks through, and can be
switched off in Settings or the game's **Options** (*Archipelago Log*,
*Archipelago Tracker*). Other players' item sends appear only in the Log tab. The
window footer shows the mod version.

## Setup guide

For installation from a ZIP, download
[LookOutsideAP-0.0.5-dev74.zip](releases/LookOutsideAP-0.0.5-dev74.zip) from the
repository's **`releases/` folder** and follow
[Install the extracted package](#install-the-extracted-package). It includes the
built APWorld and everything needed to prepare the game-side mod files; a source
checkout is not required for that workflow. Look Outside, Archipelago, and Python
are separate prerequisites.

The numbered steps below are the alternative development workflow, using a
source checkout and project-local copies of both installations.

### 1. Requirements

- A matching Windows game installation and Archipelago installation. You will
  enter their folder paths during setup; the originals remain read-only.
- Python **3.10 or newer**, available as `python` in PowerShell.
- A local checkout of this repository in a writable folder, with space for
  copies of both installations.
- A fresh **Survivor Mode** game and a seed generated with the current APWorld.

This mod adds `js/plugins/LookOutsideArchipelago.js` and registers it in a
replacement `js/plugins.js`. There is no separate general-purpose mod loader or
external AP bridge client to launch; the game plugin connects to the AP server.

### 2. Stage the game and APWorld inside the project

Open PowerShell in the repository root (the folder containing this README),
then run the following. At each prompt, enter the full folder path without
surrounding quotes. The game folder must contain `Game.exe`; the Archipelago
folder must contain `ArchipelagoGenerate.exe`.

```powershell
$projectRoot = (Get-Location).Path
$gameSource = Read-Host 'Path to your Look Outside installation'
$apSource = Read-Host 'Path to your Archipelago installation'
python -B tools/validate_registry.py --game-dir "$gameSource"
python -B tools/sync_plugin_registry.py --check
python -B tools/stage_game.py --game-dir "$gameSource"
python -B tools/stage_archipelago.py --ap-dir "$apSource"
```

This creates `.local/game-smoke` and `.local/archipelago-smoke`. The game copy
omits the original save folder. The AP copy receives the current
`custom_worlds/lookoutside.apworld`. Neither source installation is modified.
The development game copy suppresses Steam achievement/stat writes during
testing; that instrumentation is absent from the distributable plugin.

If these staged directories already exist, close their game/generator processes
and use the matching refresh flag instead of the initial staging command.
Run from the repository root with `$gameSource` and `$apSource` set as above:

```powershell
python -B tools/stage_game.py --game-dir "$gameSource" --refresh-plugin
python -B tools/stage_archipelago.py --ap-dir "$apSource" --refresh-world
```

Refresh updates the mod component, not the underlying installation. After an
underlying installation changes, use a new project-local `--out-dir`.

### 3. Create the player YAML and generate a seed

For an initial solo test, create `.local/players/LookOutside.yaml` using this
sample, and change `name` to the name you want to appear as in the room. Use a
different file for each player in a multiworld and unique player names. Keep unrelated YAMLs out of this player directory.

```yaml
name: LookOutside_Test
game: Look Outside
Look Outside:
  # Optional cooking/crafting checks that only hold filler. Off by default.
  activity_checks: false
  # Optional companion upgrade items plus filler-only "joins the party" checks.
  companion_upgrades: false
```

The supplied fixture contains this configuration. On first setup, copy it and
generate with the staged executable:

```powershell
New-Item -ItemType Directory -Path "$projectRoot\.local\players" -Force
Copy-Item -LiteralPath "$projectRoot\tests\fixtures\lookoutside.yaml" -Destination "$projectRoot\.local\players\LookOutside.yaml"
Push-Location "$projectRoot\.local\archipelago-smoke"
.\ArchipelagoGenerate.exe --multi 1 --spoiler 2 --player_files_path "$projectRoot\.local\players" --outputpath "$projectRoot\.local\playtest-output"
Pop-Location
```

Keep your edited YAML for subsequent seeds; do not recopy the sample over it.
For a multiworld, change `--multi` to the player count and install the other games'
required APWorlds into this staged AP copy. Look Outside is hidden from normal
world listings during development, but its YAML works.

### 4. Host the generated game

Extract the generated ZIP from `.local/playtest-output` into a new project-local
folder, for example `.local/hosted-seed`. Find its `.archipelago` multidata file.
Open a separate PowerShell terminal in the repository root and run the following,
replacing `AP_<seed>` with the actual filename:

```powershell
$projectRoot = (Get-Location).Path
Set-Location "$projectRoot\.local\archipelago-smoke"
.\ArchipelagoServer.exe "$projectRoot\.local\hosted-seed\AP_<seed>.archipelago" --host 127.0.0.1 --port 38281 --release_mode goal --collect_mode disabled
```

Keep that terminal open. This example hosts on this PC only and enables release
after the goal. `collect_mode disabled` keeps completion from automatically
collecting your items in other worlds; it does not prevent releasing this world.
For a room hosted elsewhere, use its supplied address, port, and password and
ensure its host permits release. The generator needs the custom APWorld.

### 5. Launch and connect

Open another PowerShell terminal in the repository root:

```powershell
$projectRoot = (Get-Location).Path
$env:LOA_DEV_MODE = '1'
Set-Location "$projectRoot\.local\game-smoke"
.\Game.exe --user-data-dir="$projectRoot\.local\nw-profile"
```

1. Start a **new Survivor Mode game**.
2. Open **Archipelago** from the in-game menu before taking any audited
   reward, resolving a tracked quest, or advancing a day. Connection settings are
   on its Overview tab.
3. Enter `localhost:38281` for the local server, the exact YAML player name
   (`LookOutside_Test` in the sample), and a room password if required.
   Explicit `ws://` and `wss://` addresses are supported, and a pasted
   `/connect host:port` line from a room page is accepted.
   Hosted rooms requiring encryption can be entered as `wss://host:port`.
   Current source also retries a failed opening `ws://` connection securely;
   the original `0.0.2-dev74` tagged package requires the explicit secure scheme.
4. Confirm the pill reads **Connected** and the seed/slot line, then play and save in
   the test copy. Server/slot settings are remembered; passwords are masked and
   are not saved.

Inventory-full items wait in a saved queue; make space for delivery. A three-key bundle needs room for all three.
After binding, offline checks are saved for reconnect, and already-received queued
items can deliver on a compatible offline reload. Items that have not reached
the client still require a server connection.

### Install the extracted package

The ZIP in [releases](releases/README.md) contains `lookoutside.apworld`,
`LookOutsideArchipelago.js`, `prepare_mod.py`, `LookOutside.yaml`, a setup README,
the license, manifest/checksums, and playtest documentation. The APWorld is
already built. The preparation script builds the replacement game files using
your original plugin list. No game assets are included.

1. Download the ZIP and extract it into a new writable folder. When working from
   this repository, use a project-local folder such as `.local/package-test`.
2. With Python 3.10 or newer installed, open PowerShell in that extracted folder
   and run the command below. It validates the manifest and game build, then
   writes `prepared` inside the extracted package.
3. Make a separate, unmodified game copy for testing, omitting `save`, and back
   up that copy's `js/plugins.js`. Keep it inside the project for repository work.
4. Copy `prepared/js` contents into the test game's `js` directory. This replaces
   `plugins.js` and adds `plugins/LookOutsideArchipelago.js`.
5. Put the package's `lookoutside.apworld` in your test Archipelago copy's
   `custom_worlds` folder and restart AP. Use the included `LookOutside.yaml`
   for generation, then follow the extracted README's **Generate and host** and
   **Play** sections. Launch the test game with `LOA_DEV_MODE=1`, start a fresh
   Survivor Mode save, and connect before collecting randomized rewards.

```powershell
$gameSource = Read-Host 'Path to your Look Outside installation'
python .\prepare_mod.py --game-dir "$gameSource"
```

Preparation reads an original plugin list and preserves its entries and order.
It refuses a source already containing this mod or an existing output directory.
For removal, close the test game, restore its original `js/plugins.js`, and remove
only `js/plugins/LookOutsideArchipelago.js`. Keep AP saves separate. See the
[package setup guide](docs/package_setup.md).

### Rebuild the release ZIP from source

Run from the repository root:

```powershell
$gameSource = Read-Host 'Path to your Look Outside installation'
python -B tools/build_package.py --game-dir "$gameSource"
```

The builder validates the registry, native chronology signatures, plugin, and
shipped guide summaries, then writes `releases/LookOutsideAP-<version>-dev<registry>.zip`.
This folder is included in Git. Rebuild after source changes and include the
updated ZIP with the release changes. Its manifest records component hashes;
the filename alone does not identify every source revision.

## Saves, updating, and troubleshooting

| Situation | Action |
| --- | --- |
| AP menu is missing | Launch the staged `Game.exe` with `LOA_DEV_MODE=1`; verify the plugin is registered in that copy. |
| Connection refuses difficulty/build | Use Survivor Mode and the audited build. Guards reject unsupported versions. |
| First connection says the save is ineligible | Start a fresh mod-created save and bind before an audited reward, terminal resolution, or day rollover. Existing vanilla saves cannot be converted reliably. |
| Wrong seed or slot | Load that seed/slot's matching save, or start a fresh one. A bound save cannot be reassigned. |
| Items have not appeared | Check the Archipelago window's Overview and Items tabs; clear inventory space. Repeat packets do not grant duplicate items. |
| Connection fails with a hosted room | Enter only `host:port` (a pasted `/connect host:port` also works). archipelago.gg rooms can change port after sleeping; check the room page. |
| No Archipelago pop-up after launching | None is expected: open the pause menu and choose **Archipelago**. |
| The day has stopped advancing | Use Go to Next Day at the 4 a.m. hold. Review deadlines first. Day 15 has no further quest-day transitions. |
| Goal counted but checks were not released | Reconnect if offline, or ask the host to permit release. Release-disabled rooms retain unchecked locations. |
| Save compatibility error after updating | Use the original matching mod/game version, or start a fresh compatible seed/save. Older AP schemas are not silently migrated. |

Registry/build changes require matching plugin/APWorld versions and may require
a new seed/save. The current chronology-only update preserves registry 74's
runtime/save format, but **existing seeds do not gain its placement rules**:
regenerate to use them. Keep old packages for unfinished runs. Schema 7 checks
compatibility before native AP save state is installed. See
[save compatibility](docs/save_compatibility.md).

## Verification and developer references

The current checkpoint has **64 Python tests and 51 Node tests passing**. All 22
native probe groups (922 scenarios) pass inside the staged game, including the
menu, log overlay, keys, discs, power, chronology, routes, quests and saves. A
batch of 30 seeds generated with Archipelago 0.6.8 (solo with both options, and
two-player) reached every check. Earlier checkpoints recorded the following. Chronology verification includes 77 native source
signatures, 15 native scenarios, and 10 real AP CollectionState cases. AP 0.6.7
seed 172 reaches all 273 locations; two-player seed 173 reaches all 546 locations
without ending release. Invalid direct and transitive late-Rose placements are
rejected. These results do not replace a full interactive playthrough.

Run from the project root:

```powershell
$gameSource = Read-Host 'Path to your Look Outside installation'
python -B -m unittest discover -s tests -p 'test_*.py'
node tests/plugin_interception.test.js
python -B tools/audit_access.py --require-complete
python -B tools/audit_chronology.py --game-dir "$gameSource"
python -B tools/sync_plugin_registry.py --check
python -B tools/sync_setup_guide.py --check
```

- [Current status and test evidence](docs/current_status.md)
- [Full playtest checklist](docs/playtest.md)
- [Internal progression item limitations: all 64 types](docs/internal_progression_item_limits.md)
- [Access rules and route evidence](docs/access_logic.md)
- [Calendar boundaries and remaining risks](docs/calendar_deadlines.md)
- [Registry: exact item, location, and resolution-group lists](apworld/lookoutside/vertical_slice.json)
- [Generation rules](apworld/lookoutside/access_data.py), [calendar events](apworld/lookoutside/chronology.py), and [disc allocations](apworld/lookoutside/disc_rules.py)

Older audit documents preserve historical counts; the current status and registry
supersede those checkpoints. The [initial workplan](docs/initial_codex_workplan.md)
records design intentions, not authoritative implementation instructions.

## Credits and license

- **Original mod: [wyldek](https://github.com/wyldek)** —
  [Look_Outside_Archipelago_Mod](https://github.com/wyldek/Look_Outside_Archipelago_Mod).
  The registry, access and calendar logic, game plugin, save handling, tools and
  native test suite are wyldek's work. Thank you!
- **This fork: [Emre-desertbird](https://github.com/Emre-desertbird/Look_Outside_Archipelago_Mod)** —
  a vibe-coded extension written with Claude Code: the Archipelago window and log
  overlay, deadline warnings, optional activity checks, companion upgrades, Supply
  Cache and the Rebreather logic change.
- **Look Outside** belongs to its developers; no game assets are included.
  [Archipelago](https://github.com/ArchipelagoMW/Archipelago) is the multiworld
  randomizer framework this mod plugs into.

Released under the [MIT License](LICENSE).
