"""Embed the active APWorld registry into the development RPG Maker plugin."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from ending_warning_scope import ENDING_CHOICES


PROJECT_DIR = Path(__file__).resolve().parents[1]
REGISTRY = PROJECT_DIR / "apworld" / "lookoutside" / "vertical_slice.json"
ACTIVITIES = PROJECT_DIR / "apworld" / "lookoutside" / "activities.json"
COMPANIONS = PROJECT_DIR / "apworld" / "lookoutside" / "companions.json"
SUPPLIES = PROJECT_DIR / "apworld" / "lookoutside" / "supplies.json"
DAILY_LIFE = PROJECT_DIR / "apworld" / "lookoutside" / "daily_life.json"
PLUGIN = PROJECT_DIR / "game_plugin" / "LookOutsideArchipelago.js"
BEGIN = "    // BEGIN GENERATED DEVELOPMENT REGISTRY\n"
END = "    // END GENERATED DEVELOPMENT REGISTRY\n"
BUILD_PATTERN = re.compile(r"(?m)^    const auditedBuild = Object\.freeze\(\{ gameId: \d+, versionId: \d+ \}\);$")
VERSION_PATTERN = re.compile(r"(?m)^    const developmentRegistryVersion = \d+;$")


def js_object(value: dict, indent: int = 0) -> str:
    source = json.dumps(value, ensure_ascii=False, indent=4)
    return "\n".join(" " * indent + line for line in source.splitlines())


def render(data: dict, activities: dict, companions: dict, supplies: dict, daily_life: dict) -> str:
    sources = []
    resolutions = {family["key"] for family in data.get("quest_families", [])
                   if family.get("resolve_on_acquisition")}
    for location in data["locations"]:
        for variant in (location, *location.get("source_variants", [])):
            source = {
                "key": location["key"],
                "mapId": variant["map_id"],
                "eventId": variant["event_id"],
                "pageIndex": variant["page"],
                "commandIndex": variant["command_index"],
                "commandCode": variant["command_code"],
                "databaseId": location["reward_database_id"],
                "apId": location["ap_id"],
            }
            if location.get("quest_family") in resolutions:
                source["resolutionFamily"] = location["quest_family"]
            if "troop_id" in variant:
                source["troopId"] = variant["troop_id"]
            if "common_event_id" in variant:
                source["commonEventId"] = variant["common_event_id"]
            if "required_variables" in variant:
                source["requiredVariables"] = variant["required_variables"]
            if "required_switches" in variant:
                source["requiredSwitches"] = variant["required_switches"]
            if "deferred_switches" in variant:
                source["deferredSwitches"] = [{"commandIndex": effect["command_index"], "id": effect["switch_id"]}
                                              for effect in variant["deferred_switches"]]
            if "message_index" in variant:
                source.update({
                    "messageIndex": variant["message_index"],
                    "originalMessage": variant["message_text"],
                    "apMessage": location.get("ap_message", "Archipelago location checked."),
                })
            if "battle_drop" in location:
                source["battleDrop"] = {
                    "enemyId": location["battle_drop"]["enemy_id"],
                    "dropIndex": location["battle_drop"]["drop_index"],
                    "kind": location["battle_drop"]["kind"],
                    "parameters": variant["battle_parameters"],
                }
            if "message_variants" in location:
                source["messageVariants"] = [{
                    "messageIndex": notice["message_index"],
                    "originalMessage": notice["message_text"],
                    "apMessage": notice["ap_message"],
                } for notice in location["message_variants"]]
            if "shared_consumed_page" in location:
                source["sharedConsumedPage"] = location["shared_consumed_page"]
            sources.append(source)
    definitions = {
        str(item["ap_id"]): {"kind": item["kind"], "id": item["database_id"], "name": item["name"],
                            **({"amount": item["delivery_amount"]} if "delivery_amount" in item else {}),
                            **({"deliverySwitches": item["delivery_switches"]} if "delivery_switches" in item else {})}
        for item in data["items"]
    }
    definitions[str(supplies["item"]["ap_id"])] = {"kind": "cache", "id": 1, "name": supplies["item"]["name"]}
    for companion in companions["companions"]:
        definitions[str(companion["item"]["ap_id"])] = {
            "kind": "upgrade", "id": companion["actor_id"], "name": companion["item"]["name"]}
    lines = [
        "    // Source data generated from the active APWorld registry.",
        "    const sourceSignatures = Object.freeze([",
    ]
    for source in sources:
        lines.append("        Object.freeze(" + js_object(source) + "),")
    lines.extend([
        "    ]);",
        "    const developmentLocationIds = Object.freeze(Object.fromEntries(",
        "        sourceSignatures.map(source => [source.key, source.apId])",
        "    ));",
        "    const developmentItemDefinitions = Object.freeze({",
    ])
    for item_id, definition in sorted(definitions.items(), key=lambda entry: int(entry[0])):
        lines.append(f"        {item_id}: Object.freeze({json.dumps(definition)}),")
    lines.append("    });")
    lines.append("    const locationDeadlines = Object.freeze([")
    for location in data["locations"]:
        if "expiry" in location:
            deadline = {"key": location["key"], "name": location["name"], **location["expiry"]}
            lines.append("        Object.freeze(" + json.dumps(deadline, ensure_ascii=False) + "),")
    lines.append("    ]);")
    lines.append("    const questTerminals = Object.freeze([")
    for family in data.get("quest_families", []):
        for terminal in family["terminals"]:
            definition = {
                "familyKey": family["key"],
                "familyName": family["name"], "locationKeys": terminal.get("location_keys", family["location_keys"]),
                "mapId": terminal["map_id"], "eventId": terminal["event_id"],
                "pageIndex": terminal["page"], "commandIndex": terminal["command_index"],
                "commandCode": terminal["command_code"], "parameters": terminal["parameters"],
            }
            message = terminal.get("completion_message", family.get("completion_message"))
            if message:
                definition["message"] = message
            if "troop_id" in terminal:
                definition["troopId"] = terminal["troop_id"]
            if "common_event_id" in terminal:
                definition["commonEventId"] = terminal["common_event_id"]
            if "required_variables" in terminal:
                definition["requiredVariables"] = terminal["required_variables"]
            lines.append("        Object.freeze(" + js_object(definition) + "),")
    lines.append("    ]);")
    lines.append("    const endingChoices = Object.freeze(" + js_object(ENDING_CHOICES) + ");")
    lines.append(f"    const activityVersion = {activities['feature_version']};")
    lines.append("    const activityLocations = Object.freeze([")
    for location in activities["locations"]:
        entry = {"key": location["key"], "name": location["name"], "apId": location["ap_id"],
                 "rooms": location.get("rooms", [])}
        if "meals" in location:
            entry["meals"] = location["meals"]
        else:
            entry["crafts"] = 1
        lines.append("        Object.freeze(" + json.dumps(entry, ensure_ascii=False) + "),")
    lines.append("    ]);")
    supply_table = [[row["id"], row["weight"]] for row in supplies["table"]]
    lines.append(f"    const supplyCache = Object.freeze({{ rolls: {supplies['rolls']}, table: {json.dumps(supply_table)} }});")
    lines.append(f"    const dailyLifeVersion = {daily_life['feature_version']};")
    lines.append("    const dailyLifeLocations = Object.freeze([")
    for location in daily_life["locations"]:
        entry = {"key": location["key"], "name": location["name"], "apId": location["ap_id"],
                 "trigger": location["trigger"], "rooms": location.get("rooms", [])}
        lines.append("        Object.freeze(" + json.dumps(entry, ensure_ascii=False) + "),")
    lines.append("    ]);")
    lines.append(f"    const companionVersion = {companions['feature_version']};")
    lines.append("    const companionUpgrades = Object.freeze([")
    for companion in companions["companions"]:
        entry = {"actorId": companion["actor_id"], "name": companion["name"],
                 "key": companion["location"]["key"], "apId": companion["location"]["ap_id"],
                 "passive": companion["passive"], "summary": companion["summary"], "effect": companion["effect"]}
        lines.append("        Object.freeze(" + json.dumps(entry, ensure_ascii=False) + "),")
    lines.append("    ]);")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="Fail if the plugin block differs from the active registry")
    args = parser.parse_args()
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    activities = json.loads(ACTIVITIES.read_text(encoding="utf-8"))
    companions = json.loads(COMPANIONS.read_text(encoding="utf-8"))
    supplies = json.loads(SUPPLIES.read_text(encoding="utf-8"))
    daily_life = json.loads(DAILY_LIFE.read_text(encoding="utf-8"))
    plugin = PLUGIN.read_text(encoding="utf-8")
    expected_build = ("    const auditedBuild = Object.freeze({ gameId: "
                      f"{data['audited_game_id']}, versionId: {data['audited_version_id']} }});")
    expected_version = f"    const developmentRegistryVersion = {data['registry_version']};"
    if len(BUILD_PATTERN.findall(plugin)) != 1 or len(VERSION_PATTERN.findall(plugin)) != 1:
        raise ValueError("Expected exactly one audited-build and registry-version declaration")
    if args.check and (BUILD_PATTERN.search(plugin).group() != expected_build or
                       VERSION_PATTERN.search(plugin).group() != expected_version):
        raise SystemExit("Plugin build or registry version differs from active APWorld")
    plugin = BUILD_PATTERN.sub(expected_build, plugin)
    plugin = VERSION_PATTERN.sub(expected_version, plugin)
    if plugin.count(BEGIN) != 1 or plugin.count(END) != 1:
        raise ValueError("Expected exactly one generated-registry block")
    start = plugin.index(BEGIN) + len(BEGIN)
    stop = plugin.index(END)
    if stop < start:
        raise ValueError("Generated-registry markers are reversed")
    expected = render(data, activities, companions, supplies, daily_life)
    if args.check:
        if plugin[start:stop] != expected:
            raise SystemExit("Plugin registry is out of sync; run sync_plugin_registry.py")
        print(f"Plugin registry matches {len(data['locations'])} locations")
        return
    PLUGIN.write_text(plugin[:start] + expected + plugin[stop:], encoding="utf-8")
    print(f"Embedded {len(data['locations'])} active locations in {PLUGIN}")


if __name__ == "__main__":
    main()
