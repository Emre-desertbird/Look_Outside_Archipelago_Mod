"use strict";

module.exports = async function nativeMenuProbe(slotData) {
    const assert = require("assert").strict;
    const ap = LookOutsideArchipelago;
    const originalSocket = globalThis.WebSocket;
    const preferencesKey = "lookOutsideArchipelagoConnection";
    const originalPreferences = localStorage.getItem(preferencesKey);
    const fs = require("fs");
    const sockets = [];
    const originalUpdateScene = SceneManager.updateScene;
    const originalHud = ConfigManager.loaHud;
    let scenarios = 0;
    class TestSocket {
        constructor(url) { this.url = url; this.readyState = 1; this.sent = []; sockets.push(this); }
        send(text) { this.sent.push(...JSON.parse(text)); }
        close() { this.readyState = 3; this.onclose?.(); }
        server(packet) { this.onmessage({ data: JSON.stringify([packet]) }); }
    }
    const waitForRefresh = () => new Promise(resolve => setTimeout(resolve, 450));
    function menu() {
        const scene = new Scene_Menu();
        scene.create();
        scene.popped = false;
        scene.popScene = () => { scene.popped = true; };
        return scene;
    }
    const dialog = () => document.querySelector("#loa-ap-dialog");
    const control = selector => dialog().querySelector(selector);
    function submit(url, name = "Menu Test", password = "") {
        control("#loa-ap-url").value = url;
        control("#loa-ap-name").value = name;
        control("#loa-ap-password").value = password;
        control("form").dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
    }
    try {
        // Isolate the menu fixture from the currently displayed title/map scene
        // while the dialog's asynchronous status refresh is being exercised.
        SceneManager.updateScene = () => {};
        // This fixture can run before Scene_Boot initializes UI resources.
        ColorManager.loadWindowskin();
        await new Promise((resolve, reject) => {
            const timeout = setTimeout(() => reject(new Error("Menu windowskin did not load")), 5000);
            ColorManager._windowskin.addLoadListener(() => { clearTimeout(timeout); resolve(); });
        });
        globalThis.WebSocket = TestSocket;
        localStorage.removeItem(preferencesKey);
        // The receipt toast is shown only while the log overlay is switched off.
        ConfigManager.loaHud = false;
        DataManager.setupNewGame();
        $gameMessage.clear();
        $dataMap = JSON.parse(fs.readFileSync("data/Map003.json", "utf8"));
        DataManager.onLoad($dataMap);
        $gameMap.setup(3);
        // The normal menu opens after the apartment's arrival events finish.
        for (const event of $gameMap.events()) event.clearStartingFlag();
        let scene = menu();
        scene._commandWindow.callHandler("loaArchipelago");
        assert.ok(dialog().open);
        assert.equal(scene._commandWindow.active, false);
        assert.ok(["loa-ap-name", "loa-ap-url"].includes(document.activeElement.id), "A connection field must receive focus");
        assert.equal(control("#loa-ap-password").type, "password");
        document.activeElement.dispatchEvent(new KeyboardEvent("keydown", {
            key: "x", keyCode: 88, bubbles: true,
        }));
        assert.ok(!Input._currentState.escape, "Typing in the dialog leaked into the game");
        scenarios++;

        submit("https://example.invalid:38281");
        assert.equal(sockets.length, 0);
        assert.match(control(".loa-error").textContent, /connection settings/);
        scenarios++;

        submit("localhost:38304", " Menu Test ", "local-probe-password");
        const socket = sockets.at(-1);
        assert.equal(socket.url, "ws://localhost:38304");
        socket.server({ cmd: "RoomInfo", seed_name: "native-menu-probe" });
        assert.equal(socket.sent[0].name, "Menu Test");
        assert.equal(socket.sent[0].password, "local-probe-password");
        socket.server({ cmd: "Connected", team: 0, slot: 1, checked_locations: [], slot_data: slotData });
        await waitForRefresh();
        assert.equal(ap.connectionState, "connected");
        assert.equal(control(".loa-pill").textContent, "Connected");
        assert.match(control(".loa-seed").textContent, /native-menu-probe/);
        assert.match(control(".loa-cards").textContent, /Checks0 \/ 0/);
        // Tabs switch panels; Log shows the connection line.
        control('[data-tab="log"]').click();
        assert.equal(control('[data-panel="log"]').hidden, false);
        assert.equal(control('[data-panel="overview"]').hidden, true);
        await waitForRefresh();
        assert.match(control(".loa-log").textContent, /Connected to localhost:38304/);
        control('[data-tab="overview"]').click();
        assert.equal(control("#loa-ap-password").value, "");
        assert.deepEqual(JSON.parse(localStorage.getItem(preferencesKey)), {
            url: "ws://localhost:38304", name: "Menu Test",
        });
        scenarios++;

        const items = [{ item: 540100015 }, { item: 540000301 }];
        socket.server({ cmd: "ReceivedItems", index: 0, items });
        ap.deliverPendingForDevelopment();
        ap.presentItemsForDevelopment();
        assert.match(document.querySelector("#loa-ap-receipt").textContent, /Baseball Bat\nPadlock Key/);
        await waitForRefresh();
        const itemRows = Array.from(control(".loa-items").children, row => row.textContent);
        assert.equal(itemRows.length, 2);
        assert.match(itemRows[0], /^Padlock Key (from|found at)/);
        assert.match(itemRows[1], /^Baseball Bat (from|found at)/);
        socket.server({ cmd: "ReceivedItems", index: 0, items });
        ap.deliverPendingForDevelopment();
        document.querySelector("#loa-ap-receipt").expiresAt = 0;
        ap.presentItemsForDevelopment();
        assert.equal(document.querySelector("#loa-ap-receipt"), null, "Replay showed a second delivery notice");
        assert.equal($gameParty.numItems($dataWeapons[15]), 1);
        scenarios++;

        $gameParty.gainItem($dataWeapons[15], 98);
        socket.server({ cmd: "ReceivedItems", index: 2, items: [items[0]] });
        ap.deliverPendingForDevelopment();
        ap.presentItemsForDevelopment();
        assert.equal(ap.pendingItems().length, 1);
        assert.equal(document.querySelector("#loa-ap-receipt"), null, "Undelivered item showed a receipt");
        $gameParty.gainItem($dataWeapons[15], -1);
        ap.deliverPendingForDevelopment();
        ap.presentItemsForDevelopment();
        assert.equal(ap.pendingItems().length, 0);
        assert.match(document.querySelector("#loa-ap-receipt").textContent, /Baseball Bat/);
        scenarios++;

        submit("ws://bad:invalid-port");
        assert.equal(ap.connectionState, "connected");
        assert.equal(socket.readyState, 1, "Invalid settings disconnected the working session");
        assert.equal(sockets.length, 1);
        globalThis.WebSocket = class { constructor() { throw new Error("Probe socket failure"); } };
        submit("ws://localhost:38304");
        assert.equal(ap.connectionState, "connected");
        assert.equal(socket.readyState, 1);
        assert.match(control(".loa-error").textContent, /Probe socket failure/);
        globalThis.WebSocket = TestSocket;
        scenarios++;

        control(".loa-disconnect").click();
        assert.equal(ap.connectionState, "disconnected");
        assert.ok(ap.active);
        assert.equal(ap.identity().seedName, "native-menu-probe");
        control(".loa-close").click();
        assert.equal(dialog(), null);
        assert.equal(scene._commandWindow.active, true);
        scenarios++;

        scene._commandWindow.callHandler("loaArchipelago");
        assert.equal(control("#loa-ap-name").value, "Menu Test");
        assert.equal(control("#loa-ap-password").value, "");
        control("#loa-ap-name").dispatchEvent(new KeyboardEvent("keydown", {
            key: "Escape", keyCode: 27, bubbles: true, cancelable: true,
        }));
        assert.equal(dialog(), null);
        assert.equal(scene._commandWindow.active, true);
        scenarios++;

        $gameVariables.setValue(15, 3);
        $gameVariables.setValue(16, 4);
        const interpreter = new Game_Interpreter();
        interpreter.setup($dataCommonEvents[4].list, 0);
        interpreter._index = 59;
        interpreter.command122([15, 15, 1, 0, 1]);
        interpreter._index = 135;
        interpreter.command117([6]);
        assert.ok(ap.dayHold);
        scene = menu();
        scene._commandWindow.callHandler("loaNextDay");
        assert.equal(document.activeElement, control(".loa-close"));
        assert.equal(control(".loa-deadlines").hidden, false);
        assert.equal(control(".loa-deadlines").open, true);
        assert.match(control(".loa-description").textContent, /Vanilla quest deadlines still apply/);
        assert.match(control(".loa-description").textContent, /unfinished quests do not advance afterward/);
        assert.match(control(".loa-deadlines summary").textContent, /not a complete list/);
        const actionBounds = control(".loa-actions").getBoundingClientRect();
        assert.ok(actionBounds.top >= 0 && actionBounds.bottom <= innerHeight,
            "Day-advance actions must remain visible with the expanded warning");
        assert.match(control(".loa-deadlines div").textContent, /8 unchecked/);
        assert.match(control(".loa-deadlines div").textContent, /noon on Day 4/);
        assert.match(control(".loa-deadlines div").textContent, /Jawbone Club/);
        assert.doesNotMatch(control(".loa-deadlines div").textContent, /Joel Resolution|Benjamin|Madison/);
        control(".loa-close").click();
        assert.equal($gameVariables.value(15), 3);
        assert.ok(ap.dayHold);
        assert.equal(scene.popped, false);
        scenarios++;

        scene._commandWindow.callHandler("loaNextDay");
        for (const event of $gameMap.events()) event.clearStartingFlag();
        control("form").dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
        assert.equal($gameVariables.value(15), 4, JSON.stringify({ error: dialog()?.querySelector(".loa-error").textContent,
            eventRunning: $gameMap.isEventRunning(), reserved: $gameTemp._commonEventQueue }));
        assert.equal(ap.dayHold, false);
        assert.equal(scene.popped, true);
        assert.equal(dialog(), null);
        assert.ok($gameTemp.isCommonEventReserved());
        $gameTemp.clearCommonEventReservation();
        scenarios++;

        $gameVariables.setValue(16, 12);
        scene = menu();
        scene._commandWindow.callHandler("loaArchipelago");
        assert.match(control(".loa-deadline-text").textContent, /Access may already be lost/);
        // Settings tab writes the overlay preferences used on the map.
        control('[data-tab="settings"]').click();
        control(".loa-hud-toggle").checked = true;
        control(".loa-hud-toggle").dispatchEvent(new Event("change"));
        control(".loa-hud-side").value = "right";
        control(".loa-hud-side").dispatchEvent(new Event("change"));
        assert.deepEqual([ConfigManager.loaHud, ConfigManager.loaHudRight], [true, true]);
        control(".loa-close").click();
        scenarios++;

        // The overlay shows the latest log lines and hides behind the dialog.
        ap.presentItemsForDevelopment();
        const hud = document.querySelector("#loa-ap-hud");
        assert.equal(hud.style.display, "block");
        assert.match(hud.textContent, /Received Baseball Bat/);
        // Status rows: clock/day, check progress and the nearest deadline.
        assert.match(hud.textContent, /^Day \d+ · \d\d:\d\d/);
        assert.match(hud.textContent, /\d+ \/ \d+ checks/);
        assert.match(hud.textContent, /Original teeth apartment · (closes Day 4, 12:00|may already be missed)/);
        assert.ok(hud.querySelector("svg"), "Analog clock drawn");
        // The tracker sits on the opposite side with the current room's checks.
        const tracker = document.querySelector("#loa-ap-tracker");
        assert.equal(tracker.style.display, "block");
        assert.notEqual(tracker.style.left, "", "Tracker opposite a right-side status box");
        assert.match(tracker.textContent, /^THIS ROOM/);
        assert.match(tracker.textContent, /\d of 3 checks left|All 3 checks found/);
        assert.doesNotMatch(tracker.textContent, /Charan's Rose|Crossword/, "Unstarted optional quests stay hidden");
        assert.notEqual(hud.style.right, "", "Right-side setting applied");
        assert.equal(hud.style.pointerEvents, "none");
        scene._commandWindow.callHandler("loaArchipelago");
        ap.presentItemsForDevelopment();
        assert.equal(hud.style.display, "none", "Overlay hidden while the window is open");
        control(".loa-close").click();
        ConfigManager.loaHud = false;
        ap.presentItemsForDevelopment();
        assert.equal(hud.style.display, "none", "Option switches the overlay off");
        ConfigManager.loaHudRight = false;
        scenarios++;

        DataManager.setupNewGame();
        scene = menu();
        scene._commandWindow.callHandler("loaArchipelago");
        DataManager.setupNewGame();
        assert.equal(dialog(), null, "New game left the previous save's dialog open");
        scenarios++;
        return { scenarios };
    } finally {
        ConfigManager.loaHud = originalHud;
        ConfigManager.loaHudRight = false;
        DataManager.setupNewGame();
        globalThis.WebSocket = originalSocket;
        SceneManager.updateScene = originalUpdateScene;
        if (originalPreferences === null) localStorage.removeItem(preferencesKey);
        else localStorage.setItem(preferencesKey, originalPreferences);
    }
};
