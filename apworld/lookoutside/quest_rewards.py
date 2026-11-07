"""Character-quest checks: never progression, always a useful item.

These quests can take many days, close early or depend on choices, so nobody's
progression may wait behind them. Excluded locations would only take filler,
which feels like no reward, so the world places a useful item there instead.
"""

# Quest families that are bosses, salvage or plain pickups rather than characters.
NON_CHARACTER_FAMILIES = ("boss_salvage_", "map006_event013", "map092_event045", "map430_event016")
EXTRA_KEYS = ("map339_event012",)  # Charan's Azure Greatsword has no quest family.


def quest_reward_names(registry):
    """Names of the character-quest locations; missable ones stay filler-only."""
    return frozenset(
        entry["name"] for entry in registry["locations"]
        if not entry.get("missable") and (
            (entry.get("quest_family") and not entry["quest_family"].startswith(NON_CHARACTER_FAMILIES)) or
            entry["key"] in EXTRA_KEYS)
    )
