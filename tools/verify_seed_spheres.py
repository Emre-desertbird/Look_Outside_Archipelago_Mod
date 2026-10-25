"""Independently verify every location in generated Look Outside test seeds.

The no-item ending is intentionally insufficient for this check. Starting with
an empty inventory, collect only reachable locations, then deliver their items.
This uses the actual generator's spoiler placements and rejects deadlock or
progression or useful items on explicitly excluded locations. Each sweep includes
generation-only calendar reservations. It does not simulate the runtime clock,
choices, movement, or combat.
"""

import argparse
from collections import Counter
import json
import re
from pathlib import Path
from zipfile import ZipFile

from audit_access import PROJECT, load_access


def verify(path):
    registry = json.loads((PROJECT / "apworld/lookoutside/vertical_slice.json").read_text(encoding="utf-8"))
    activities = json.loads((PROJECT / "apworld/lookoutside/activities.json").read_text(encoding="utf-8"))
    companions = json.loads((PROJECT / "apworld/lookoutside/companions.json").read_text(encoding="utf-8"))
    supply_cache = json.loads((PROJECT / "apworld/lookoutside/supplies.json").read_text(encoding="utf-8"))["item"]
    # Companion joins behave like free, excluded activity checks at home.
    companion_items = [{**row["item"], "quantity": 1} for row in companions["companions"]]
    companion_rows = {row["location"]["name"]: {**row["location"], "region": "Apartment 33", "missable": True}
                      for row in companions["companions"]}
    graph = load_access()
    graph.validate(registry)
    definitions = {row["name"]: row for row in registry["items"] + companion_items + [supply_cache]}
    # Optional activity checks are excluded (filler only) and gated by regions alone.
    daily_life = json.loads((PROJECT / "apworld/lookoutside/daily_life.json").read_text(encoding="utf-8"))
    activity_rows = {row["name"]: {**row, "missable": True, "group": "activity"} for row in activities["locations"]}
    activity_rows |= {row["name"]: {**row, "missable": True, "group": "daily"} for row in daily_life["locations"]}
    locations = {row["name"]: row for row in registry["locations"]} | activity_rows | companion_rows
    with ZipFile(path) as archive:
        spoiler = next(name for name in archive.namelist() if name.endswith("_Spoiler.txt"))
        lines = archive.read(spoiler).decode("utf-8-sig").splitlines()
    players = [match.group(1) for line in lines if (match := re.fullmatch(r"Player \d+: (.+)", line))]
    if not players and any(re.fullmatch(r"Players:\s+1", line) for line in lines):
        players = ["Player 1"]  # Single-player spoilers omit the slot name.
    if not players or len(set(players)) != len(players):
        raise ValueError("Missing or duplicate player names")
    if sum(line.startswith("Game:") and line.split(":", 1)[1].strip() == "Look Outside" for line in lines) != len(players):
        raise ValueError("This verifier supports Look Outside-only test worlds")
    multiple = len(players) > 1
    source_names = {name + (f" ({player})" if multiple else ""): (player, location)
                    for player in players for name, location in locations.items()}
    reward_names = {name + (f" ({player})" if multiple else ""): (player, name)
                    for player in players for name in definitions}
    placements = {}
    in_locations = False
    for line in lines:
        if line == "Locations:":
            in_locations = True
            continue
        if line == "Playthrough:":
            break
        if not in_locations:
            continue
        for name, (owner, location) in source_names.items():
            prefix = name + ": "
            if line.startswith(prefix):
                reward = reward_names.get(line[len(prefix):])
                if reward is None:
                    raise ValueError(f"Unknown reward: {line}")
                source = (owner, location["key"])
                if source in placements:
                    raise ValueError(f"Duplicate placement: {name}")
                if location.get("missable") and definitions[reward[1]]["classification"] != "filler":
                    raise ValueError(f"Non-filler item on excluded location: {line}")
                placements[source] = reward
                break
    activity_keys = {row["key"]: row for row in activity_rows.values()}
    companion_keys = {row["key"]: row for row in companion_rows.values()}
    groups = {}
    for owner, key in placements:
        if key in activity_keys:
            groups.setdefault(owner, set()).add(activity_keys[key]["group"])
    enabled = set(groups)
    companion_players = {owner for owner, key in placements if key in companion_keys}
    group_size = {name: sum(row["group"] == name for row in activity_keys.values()) for name in ("activity", "daily")}
    for player, names in groups.items():
        for name in names:
            found = sum(owner == player and key in activity_keys and activity_keys[key]["group"] == name
                        for owner, key in placements)
            if found != group_size[name]:
                raise ValueError(f"Partial {name} checks for {player}")
    for player in companion_players:
        if sum(owner == player and key in companion_keys for owner, key in placements) != len(companion_keys):
            raise ValueError(f"Partial companion checks for {player}")
    total = (len(registry["locations"]) * len(players) +
             sum(group_size[name] for names in groups.values() for name in names) +
             len(companion_keys) * len(companion_players))
    if len(placements) != total:
        raise ValueError(f"Expected {total} placements, got {len(placements)}")
    expected = Counter({(player, row["name"]): row["quantity"]
                        for player in players for row in registry["items"]})
    for player, names in groups.items():
        for name in names:
            for row in (activities if name == "activity" else daily_life)["items"]:
                expected[(player, row["name"])] += row["quantity"]
    expected.update({(player, row["name"]): 1 for player in companion_players for row in companion_items})
    if Counter(placements.values()) != expected:
        raise ValueError("Generated item quantities differ from the registry")
    inventory, checked, spheres = {player: Counter() for player in players}, set(), []
    while len(checked) < total:
        reachable = set()
        for player in players:
            regions, checks = graph.reachable(inventory[player])
            reachable |= {(player, key) for key in checks}
            if player in enabled:
                reachable |= {(player, key) for key, row in activity_keys.items()
                              if row["group"] in groups[player] and row["region"] in regions and
                              row.get("requires_region", row["region"]) in regions and
                              inventory[player][row.get("requires_item")] >= (1 if "requires_item" in row else 0)}
            if player in companion_players:
                reachable |= {(player, key) for key in companion_keys if "Apartment 33" in regions}
        sphere = sorted(reachable - checked)
        if not sphere:
            missing = sorted(placements.keys() - checked)
            raise ValueError(f"Seed deadlocked with {len(missing)} inaccessible checks: {missing}")
        for key in sphere:
            recipient, reward = placements[key]
            inventory[recipient][reward] += 1
        checked.update(sphere)
        spheres.append(len(sphere))
    for player in players:
        _, _, events = graph.sweep(inventory[player])
        if events != {entry.name for entry in graph.events}:
            raise ValueError(f"Seed fails calendar reservations for {player}")
    return {"archive": str(path), "players": len(players), "checked": len(checked), "sphere_sizes": spheres,
            "generation_events_per_player": len(graph.events),
            "excluded_locations": len(players) * sum(bool(row.get("missable")) for row in registry["locations"]) +
                                  sum(group_size[name] for names in groups.values() for name in names) +
                                  len(companion_players) * len(companion_keys),
            "activity_players": len(enabled),
            "companion_players": len(companion_players),
            "cross_player_items": sum(owner != recipient for (owner, _), (recipient, _) in placements.items()),
            "goal_release_used": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, nargs="+")
    args = parser.parse_args()
    for path in args.archive:
        print(json.dumps(verify(path)))


if __name__ == "__main__":
    main()
