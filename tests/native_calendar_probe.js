"use strict";

// Serialized into the staged NW.js process by probe_staged_game.js.
module.exports = function nativeCalendarProbe() {
    const assert = require("assert").strict;
    const fs = require("fs");
    const ap = LookOutsideArchipelago;
    function setup(active, day = 15) {
        DataManager.setupNewGame();
        $gameMessage.clear();
        $gameVariables.setValue(15, day);
        $gameVariables.setValue(13, 3);
        $dataMap = JSON.parse(fs.readFileSync("data/Map003.json", "utf8"));
        DataManager.onLoad($dataMap);
        $gameMap.setup(3);
        $gamePlayer.clearTransferInfo();
        $gameMap._interpreter.clear();
        $gameMap.events().forEach(event => event.clearStartingFlag());
        while ($gameTemp.isCommonEventReserved()) $gameTemp.retrieveCommonEvent();
        if (active) {
            ap.bindIdentityForDevelopment("native-calendar", 0, 1);
            ap.activateForDevelopment();
        }
    }
    const doorResults = [];
    for (const active of [false, true]) for (const choice of [0, 1, 2]) {
        if (!active && choice === 2) continue;
        for (const visitor of [false, true]) {
            setup(active);
            $gameSwitches.setValue(24, visitor);
            const pages = $dataMap.events[9].pages;
            const original = JSON.stringify(pages);
            const parent = new Game_Interpreter();
            parent.setup(pages[2].list, 9);
            parent.executeCommand(); // Show Text also sets up the following choices.
            assert.deepEqual($gameMessage.choices(), active
                ? ["Leave (begin ending).", "Not yet.", "Keep exploring."]
                : ["Let's go.", "Not yet."]);
            assert.equal($gameMessage.choiceDefaultType(), active ? 2 : 0);
            assert.equal($gameMessage.choiceCancelType(), 1);
            $gameMessage.onChoice(choice);
            $gameMessage.clear();
            parent.executeCommand(); // First choice branch: enter ending or skip it.
            if (choice === 0) {
                assert.equal(parent._index, 5);
                parent._index = 10;
                parent.executeCommand();
                assert.equal($gamePlayer._newMapId, 172);
                assert.equal(parent._childInterpreter, null);
            } else if (choice === 1) {
                assert.equal(parent._childInterpreter, null);
                assert.equal($gamePlayer.isTransferring(), false);
            } else {
                const child = parent._childInterpreter;
                assert.equal(child._list, pages[visitor ? 1 : 0].list);
                assert.equal(child._eventId, 9);
                if (!visitor) {
                    child.executeCommand(); // Nighttime apartment restriction is bypassed.
                    assert.equal(child._index, 5);
                    child._index = 40;
                    child.executeCommand();
                    assert.equal($gamePlayer._newMapId, 6);
                }
            }
            assert.equal(JSON.stringify(pages), original);
            assert.equal(ap.goalCompleted, false);
            doorResults.push({ active, choice, visitor });
        }
    }
    // A copied list, an unbound session, and another game build remain native.
    for (const guard of ["copied-list", "unbound", "build"]) {
        setup(guard !== "unbound");
        if (guard === "unbound") ap.activateForDevelopment();
        const originalVersion = $dataSystem.versionId;
        if (guard === "build") $dataSystem.versionId++;
        try {
            const list = $dataMap.events[9].pages[2].list;
            const parent = new Game_Interpreter();
            parent.setup(guard === "copied-list" ? JSON.parse(JSON.stringify(list)) : list, 9);
            parent.executeCommand();
            assert.deepEqual($gameMessage.choices(), ["Let's go.", "Not yet."]);
        } finally {
            $dataSystem.versionId = originalVersion;
        }
    }

    // Execute the actual clock loop and its HourPassed day-boundary branch.
    // Other hourly story events are outside this focused calendar probe.
    function passTime(minutes) {
        $gameVariables.setValue(19, minutes);
        const caller = new Game_Interpreter();
        caller.setup([{ code: 117, indent: 0, parameters: [4] }], 66);
        caller.executeCommand();
        const clock = caller._childInterpreter;
        let newDays = 0;
        if (!clock) return newDays;
        clock.executeCommand();
        clock.executeCommand(); // Clear the previous HourPassed newDay request.
        clock._index = 52;
        let steps = 0;
        while (clock._index < 138) {
            assert.ok(steps++ < 2000, "Clock loop failed to finish");
            const command = clock.currentCommand();
            if (command.code === 117 && command.parameters[0] === 228) {
                clock._index++; // TV schedule does not write clock variables.
                continue;
            }
            clock.executeCommand();
            if ($gameMessage.isBusy()) $gameMessage.clear();
            const child = clock._childInterpreter;
            if (child && child._list === $dataCommonEvents[6].list) {
                newDays++; // Vanilla newDay is requested; its story effects are outside this probe.
                clock._childInterpreter = null;
            } else if (child) {
                assert.equal(child._list, $dataCommonEvents[5].list);
                child._index = 291;
                while (child._index < 295) child.executeCommand();
                clock._childInterpreter = null;
            }
        }
        return newDays;
    }
    // Time runs naturally: midnight counts the day and 04:00 requests vanilla newDay,
    // on Day 15 as on any other day. Queued action time is never discarded.
    const clockResults = [];
    for (const day of [7, 15]) {
        setup(true, day);
        $gameVariables.setValue(16, 23);
        $gameVariables.setValue(17, 40);
        const newDays = passTime(480);
        assert.equal($gameVariables.value(15), day + 1);
        assert.equal(newDays, 1);
        assert.equal($gameVariables.value(16), 7);
        assert.equal($gameVariables.value(17), 40);
        const saved = DataManager.makeSaveContents().lookOutsideArchipelago;
        assert.deepEqual([saved.dayHold, saved.pendingDayRollover], [false, false]);
        clockResults.push({ day });
    }
    // Preserve Leigh's real Day15 dialogue cutoff, even with a late quest stage.
    for (const day of [14, 15]) {
        setup(true, day);
        $gameVariables.setValue(900, 9);
        const talk = new Game_Interpreter();
        talk.setup($dataCommonEvents[125].list);
        talk.executeCommand();
        if (day === 15) {
            talk.executeCommand();
            assert.ok(talk._index >= talk._list.length, "native Exit Event Processing skips all dialogue");
            talk.executeCommand(); // The interpreter clears its list on the next update.
            assert.equal(talk.isRunning(), false);
            assert.equal($gameVariables.value(900), 9);
        } else assert.ok(talk._index > 1 && talk.isRunning());
    }
    // Follow the native generic ending transfers with no AP inventory/checks.
    setup(true, 15);
    $gameVariables.setValue(899, 2);
    $gameVariables.setValue(900, 7);
    const door = new Game_Interpreter();
    door.setup($dataMap.events[9].pages[2].list, 9);
    door.executeCommand();
    $gameMessage.onChoice(0);
    $gameMessage.clear();
    door.executeCommand();
    door._index = 10;
    door.executeCommand();
    assert.equal($gamePlayer._newMapId, 172);
    function loadMap(id) {
        $dataMap = JSON.parse(fs.readFileSync(`data/Map${String(id).padStart(3, "0")}.json`, "utf8"));
        DataManager.onLoad($dataMap);
        $gameMap.setup(id);
        $gamePlayer.clearTransferInfo();
    }
    loadMap(172);
    assert.equal(ap.goalCompleted, false);
    const ending = new Game_Interpreter();
    ending.setup($dataMap.events[1].pages[0].list, 1);
    // Execute metadata and transfer; skip audiovisual waits and Steam achievement.
    for (const index of [5, 6, 154]) { ending._index = index; ending.executeCommand(); }
    assert.equal($gameVariables.value(567), "No Going Back");
    assert.equal($gamePlayer._newMapId, 168);
    loadMap(168);
    assert.equal(ap.goalCompleted, true);
    assert.deepEqual(ap.checkedKeys(), [], "offline completion does not invent checks");
    assert.deepEqual([899, 900].map(id => $gameVariables.value(id)), [2, 7]);
    return { doorScenarios: doorResults.length, sourceGuards: 3, clockScenarios: clockResults.length,
        vanillaQuestCutoffs: 2, genericEndingWithUnfinishedQuests: true };
};
