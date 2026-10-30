// 2026_10_13_CL: Geaendert: Lokale Regressionstests fuer die Light-/Zonenkarte aufgenommen.
// Warum: Attributauswertung, Farbrichtung, Klickbehandlung und Slidereingaben muessen reproduzierbar pruefbar sein.
// Wirkung: Sechs Node-Tests pruefen die Fehlerkorrekturen ohne laufenden Home Assistant und ohne Zusatzpakete.
// alt: Fuer die JavaScript-Zonenkarte gab es keinen lokalen Regressionstest.
// 2026_10_21_CL: Geaendert: Testdaten und Dashboard-YAML gegen die bestaetigten HA-IDs pruefen.
// Warum: Die bisherigen Kartentests erkannten falsche Entity-Verweise in der Dashboard-YAML nicht.
// Wirkung: Reale Light-/Sensor-IDs und ein YAML-Abgleich sichern die vorlaeufige Zuordnung ab.
// alt: light.test und sensor.color waren Platzhalter; die YAML-Verweise wurden nicht mitgeprueft.
// Rueckaenderung: Die frueheren Dashboard-IDs bleiben im Kommentar von dashboard/airaluce.yaml dokumentiert.
// 2026_10_21_CL: Geaendert: Verzoegerte HA-Rueckmeldungen nach dem Loslassen gesondert testen.
// Warum: Ein abgeschlossener Serviceaufruf bestaetigt noch nicht den im Browser empfangenen Light-Zustand.
// Wirkung: Tests erkennen kurzes Zurueckspringen und pruefen Bestaetigung, Ablauf, Fehler und Zonenwechsel.
// alt: Die Render-Sperre wurde nur waehrend des Ziehens getestet.
const assert = require("node:assert/strict");
const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const vm = require("node:vm");
const { test } = require("node:test");

function createCard(config = {}, states = {}) {
  let Card;
  const calls = [];
  const storage = new Map();
  const timers = new Map();
  let nextTimer = 0;
  const context = {
    setTimeout(callback) { timers.set(++nextTimer, callback); return nextTimer; },
    clearTimeout(timer) { timers.delete(timer); },
    HTMLElement: class {
      attachShadow() {
        this.shadowRoot = {
          innerHTML: "",
          addEventListener() {},
          querySelector() {
            return { textContent: "", style: {}, addEventListener() {} };
          },
        };
      }
    },
    customElements: { define(name, constructor) { Card = constructor; } },
    window: {},
    sessionStorage: {
      getItem: (key) => storage.get(key),
      setItem: (key, value) => storage.set(key, value),
    },
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, "../../dashboard/www/airaluce-zone-control.js"), "utf8"), context);
  const card = new Card();
  card.setConfig({ zone_entity: "select.zone", light_entity: "light.airaluce", ...config });
  card.hass = {
    states: {
      "select.zone": { state: "Top" },
      "light.airaluce": { state: "on", attributes: { brightness: 128, color_temp_kelvin: 6500 } },
      ...states,
    },
    callService: async (...args) => { calls.push(args); },
    navigate: (target) => { calls.push(["navigate", target]); },
  };
  return { card, calls, timers };
}

test("detail sliders read light attributes, not on/off", () => {
  const { card } = createCard();
  assert.match(card.shadowRoot.innerHTML, /data-current-brightness>50 %/);
  assert.match(card.shadowRoot.innerHTML, /data-kind="color" type="range"[^>]*value="50"/);
  assert.doesNotMatch(card.shadowRoot.innerHTML, /NaN/);
});

test("off light displays zero brightness", () => {
  const { card } = createCard({}, {
    "light.airaluce": { state: "off", attributes: { brightness: 128, color_temp_kelvin: 4000 } },
  });
  assert.match(card.shadowRoot.innerHTML, /data-current-brightness>0 %/);
});

for (const [zone, expectedColor] of [["Top", 94], ["Bottom", 25], ["Top+Bottom", 25]]) {
  test(`off ${zone} reads its color sensor and on still reads Light attributes`, () => {
    const { card, calls } = createCard({
      color_top_entity: "sensor.color_top",
      color_bottom_entity: "sensor.color_bottom",
    }, {
      "select.zone": { state: zone },
      "sensor.color_top": { state: "239" },
      "sensor.color_bottom": { state: "64" },
    });
    assert.match(card.shadowRoot.innerHTML, /data-kind="color" type="range"[^>]*value="50"/);

    card.hass = { ...card._hass, states: { ...card._hass.states,
      "light.airaluce": { state: "off", attributes: { brightness: null, color_temp_kelvin: null } },
    } };
    assert.match(card.shadowRoot.innerHTML, /data-current-brightness>0 %/);
    assert.match(card.shadowRoot.innerHTML, new RegExp(`data-kind="color" type="range"[^>]*value="${expectedColor}"`));

    card.hass = { ...card._hass, states: { ...card._hass.states,
      "light.airaluce": { state: "on", attributes: { brightness: 255, color_temp_kelvin: 7000 } },
    } };
    assert.match(card.shadowRoot.innerHTML, /data-current-brightness>100 %/);
    assert.match(card.shadowRoot.innerHTML, /data-kind="color" type="range"[^>]*value="60"/);
    assert.equal(calls.length, 0);
  });
}

test("unknown and unavailable Light states do not use the off color sensor", () => {
  for (const state of ["unknown", "unavailable"]) {
    const { card } = createCard({ color_top_entity: "sensor.color_top" }, {
      "light.airaluce": { state, attributes: { color_temp_kelvin: 6500 } },
      "sensor.color_top": { state: "239" },
    });
    assert.match(card.shadowRoot.innerHTML, /data-kind="color" type="range"[^>]*value="50"/);
  }
});

test("missing and unavailable off color sensors preserve the previous Kelvin fallback", () => {
  for (const sensorState of [undefined, "unknown", "unavailable"]) {
    const { card } = createCard({ color_top_entity: "sensor.color_top" }, {
      "light.airaluce": { state: "off", attributes: { color_temp_kelvin: 6500 } },
      "sensor.color_top": { state: sensorState },
    });
    assert.match(card.shadowRoot.innerHTML, /data-kind="color" type="range"[^>]*value="50"/);
  }
});

test("zero is a valid off color sensor value", () => {
  const { card } = createCard({ color_top_entity: "sensor.color_top" }, {
    "light.airaluce": { state: "off", attributes: { color_temp_kelvin: 6500 } },
    "sensor.color_top": { state: "0" },
  });
  assert.match(card.shadowRoot.innerHTML, /data-kind="color" type="range"[^>]*value="0"/);
});

test("compact off color previews retain their existing source", () => {
  const { card } = createCard({
    compact: true,
    preview_color_entity: "sensor.color_bottom",
    color_top_entity: "sensor.color_top",
  }, {
    "light.airaluce": { state: "off", attributes: { color_temp_kelvin: null } },
    "sensor.color_top": { state: "239" },
    "sensor.color_bottom": { state: "0" },
  });
  assert.match(card.shadowRoot.innerHTML, /data-color-dot style="background: rgb\(255,213,128\)"/);
});

test("raw preview color agrees with Kelvin conversion", () => {
  const { card } = createCard({ compact: true, preview_color_entity: "sensor.color_top" }, {
    "sensor.color_top": { state: "0" },
  });
  assert.match(card.shadowRoot.innerHTML, /data-color-dot style="background: rgb\(255,213,128\)"/);
});

test("compact click has only the delegated handler", () => {
  const { card } = createCard({ compact: true, zone: "Bottom" });
  let directHandlers = 0;
  card.shadowRoot.querySelector = () => ({ addEventListener() { directHandlers += 1; } });
  card._render();
  assert.equal(directHandlers, 0);
});

test("HA updates do not replace a slider while dragging", () => {
  const { card } = createCard();
  const originalHtml = card.shadowRoot.innerHTML;
  card._onInput({ composedPath: () => [{ dataset: { kind: "brightness" }, value: "25" }] });
  card.hass = { ...card._hass, states: { ...card._hass.states, "light.airaluce": {
    state: "on", attributes: { brightness: 255, color_temp_kelvin: 9000 },
  } } };
  assert.equal(card.shadowRoot.innerHTML, originalHtml);
});

test("brightness command selects the zone first and keeps submitted value", async () => {
  const { card, calls } = createCard({ zone: "Bottom" });
  const input = { dataset: { kind: "brightness" }, value: "25" };
  card._hass.callService = async (...args) => {
    calls.push(args);
    if (args[0] === "select") input.value = "100";
  };
  await card._onChange({ composedPath: () => [input] });
  assert.equal(calls.length, 2);
  assert.equal(calls[0][2].entity_id, "select.zone");
  assert.equal(calls[0][2].option, "Bottom");
  assert.equal(calls[1][2].entity_id, "light.airaluce");
  assert.equal(calls[1][2].brightness, 64);
});

for (const kind of ["brightness", "color"]) {
  test(`${kind} keeps submitted value until delayed HA confirmation`, async () => {
    const { card } = createCard({}, { "select.zone": { state: "Bottom" } });
    const input = { dataset: { kind }, value: "72" };
    const sliderValue = () => Number(card.shadowRoot.innerHTML.match(
      new RegExp(`data-kind="${kind}" type="range"[^>]*value="([^"]+)"`),
    )[1]);
    card._onInput({ composedPath: () => [input] });
    await card._onChange({ composedPath: () => [input] });
    assert.equal(sliderValue(), 72, "Service completion must not restore old HA value");
    card.hass = { ...card._hass, states: { ...card._hass.states, "sensor.unrelated": { state: "1" } } };
    assert.equal(sliderValue(), 72, "Unrelated HA updates must not restore old value");
    card.hass = { ...card._hass, states: { ...card._hass.states, "light.airaluce": {
      state: "on", attributes: { brightness: 183, color_temp_kelvin: 7588 },
    } } };
    assert.equal(sliderValue(), 72, "Rounded firmware confirmation must be accepted");
    card.hass = { ...card._hass, states: { ...card._hass.states, "light.airaluce": {
      state: "on", attributes: { brightness: 128, color_temp_kelvin: 6500 },
    } } };
    assert.equal(sliderValue(), 50, "Later external changes must be displayed again");
  });
}

test("unconfirmed slider value expires instead of hiding actual HA state forever", async () => {
  const { card, timers } = createCard();
  await card._onChange({ composedPath: () => [{ dataset: { kind: "color" }, value: "72" }] });
  assert.equal(timers.size, 1);
  timers.values().next().value();
  assert.equal(timers.size, 0);
  assert.ok(/data-kind="color" type="range"[^>]*value="50"/.test(card.shadowRoot.innerHTML));
});

test("failed command releases pending slider value immediately", async () => {
  const { card, timers } = createCard();
  card._hass.callService = async () => { throw new Error("Service failed"); };
  await assert.rejects(card._onChange({ composedPath: () => [{ dataset: { kind: "color" }, value: "72" }] }), /Service failed/);
  assert.equal(timers.size, 0);
  assert.ok(/data-kind="color" type="range"[^>]*value="50"/.test(card.shadowRoot.innerHTML));
});

test("zone change discards the previous zone's pending slider value", async () => {
  const { card, timers } = createCard();
  await card._onChange({ composedPath: () => [{ dataset: { kind: "color" }, value: "72" }] });
  assert.equal(timers.size, 1);
  card.hass = { ...card._hass, states: { ...card._hass.states, "select.zone": { state: "Bottom" } } };
  assert.equal(timers.size, 0);
  assert.ok(/data-kind="color" type="range"[^>]*value="50"/.test(card.shadowRoot.innerHTML));
});

test("new slider input supersedes an older unconfirmed command", async () => {
  const { card, timers } = createCard();
  await card._onChange({ composedPath: () => [{ dataset: { kind: "color" }, value: "72" }] });
  await card._onChange({ composedPath: () => [{ dataset: { kind: "color" }, value: "30" }] });
  assert.equal(timers.size, 1);
  card.hass = { ...card._hass, states: { ...card._hass.states, "light.airaluce": {
    state: "on", attributes: { brightness: 128, color_temp_kelvin: 7588 },
  } } };
  assert.ok(/data-kind="color" type="range"[^>]*value="30"/.test(card.shadowRoot.innerHTML));
  card.hass = { ...card._hass, states: { ...card._hass.states, "light.airaluce": {
    state: "on", attributes: { brightness: 128, color_temp_kelvin: 5500 },
  } } };
  assert.equal(timers.size, 0);
});

test("brightness and color confirmations are tracked independently", async () => {
  const { card, timers } = createCard();
  await card._onChange({ composedPath: () => [{ dataset: { kind: "brightness" }, value: "30" }] });
  await card._onChange({ composedPath: () => [{ dataset: { kind: "color" }, value: "72" }] });
  assert.equal(timers.size, 2);
  card.hass = { ...card._hass, states: { ...card._hass.states, "light.airaluce": {
    state: "on", attributes: { brightness: 76, color_temp_kelvin: 6500 },
  } } };
  assert.equal(timers.size, 1);
  assert.ok(/data-kind="brightness" type="range"[^>]*value="30"/.test(card.shadowRoot.innerHTML));
  assert.ok(/data-kind="color" type="range"[^>]*value="72"/.test(card.shadowRoot.innerHTML));
});

test("leaving the card clears pending confirmation timers", async () => {
  const { card, timers } = createCard();
  await card._onChange({ composedPath: () => [{ dataset: { kind: "color" }, value: "72" }] });
  assert.equal(timers.size, 1);
  card.disconnectedCallback();
  assert.equal(timers.size, 0);
});

test("dashboard YAML uses the confirmed HA IDs and zone preview sources", () => {
  const python = path.join(os.homedir(), ".platformio", "penv", process.platform === "win32" ? "Scripts/python.exe" : "bin/python");
  const parsed = spawnSync(python, ["-c", "import json, sys, yaml; print(json.dumps(yaml.safe_load(sys.stdin)))"], {
    input: fs.readFileSync(path.join(__dirname, "../../dashboard/airaluce.yaml"), "utf8"),
    encoding: "utf8",
  });
  assert.equal(parsed.status, 0, parsed.error?.message || parsed.stderr);
  const dashboard = JSON.parse(parsed.stdout);
  const knownEntities = new Set([
    "select.zone", "light.airaluce", "fan.airaluce_fan", "switch.power",
    "sensor.brightness_top", "sensor.brightness_bottom", "sensor.color_top", "sensor.color_bottom",
  ]);
  const cards = [];
  const references = [];
  function inspect(value) {
    if (Array.isArray(value)) {
      value.forEach(inspect);
    } else if (value && typeof value === "object") {
      if (value.type === "custom:airaluce-zone-control") cards.push(value);
      for (const [key, child] of Object.entries(value)) {
        if (key === "entity" || key.endsWith("_entity")) references.push(child);
        inspect(child);
      }
    }
  }
  inspect(dashboard);
  assert.equal(references.length, 18);
  for (const entity of references) assert.ok(knownEntities.has(entity), `Unbekannte Entity-ID: ${entity}`);
  assert.equal(cards.length, 4);
  for (const card of cards) {
    assert.equal(card.zone_entity, "select.zone");
    assert.equal(card.light_entity, "light.airaluce");
  }
  assert.deepEqual(cards.map((card) => card.zone), ["Top", "Bottom", "Top+Bottom", undefined]);
  assert.deepEqual(cards.map((card) => card.preview_brightness_entity), [
    "sensor.brightness_top", "sensor.brightness_bottom", "sensor.brightness_bottom", undefined,
  ]);
  assert.deepEqual(cards.map((card) => card.preview_color_entity), [
    "sensor.color_top", "sensor.color_bottom", "sensor.color_bottom", undefined,
  ]);
  assert.equal(cards[3].color_top_entity, "sensor.color_top");
  assert.equal(cards[3].color_bottom_entity, "sensor.color_bottom");
});