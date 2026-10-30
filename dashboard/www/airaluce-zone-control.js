// 2026_10_02_CL: Geaendert: Zonenkarte steuert Helligkeit/Farbtemperatur ueber die native Light-Entitaet.
// Warum: Die getrennten Number-Entitaeten wurden durch light.airaluce ersetzt.
// Wirkung: Die Karte behaelt den Web-Farbverlauf und nutzt light.turn_on/light.turn_off.
// alt: Helligkeit und Farbe wurden mit number.set_value gesteuert.
class AiraLuceZoneControl extends HTMLElement {
  setConfig(config) {
    if (!config.zone_entity || !config.light_entity) {
      throw new Error("zone_entity und light_entity sind erforderlich.");
    }
    this.config = {
      compact: false,
      ...config,
    };
    if (!this.shadowRoot) {
      this.attachShadow({ mode: "open" });
      this.shadowRoot.addEventListener("input", (event) => this._onInput(event));
      this.shadowRoot.addEventListener("change", (event) => this._onChange(event));
      this.shadowRoot.addEventListener("click", (event) => this._onClick(event));
    }
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return this.config?.compact ? 2 : 5;
  }

  _state(entityId, fallback = "0") {
    return this._hass?.states?.[entityId]?.state ?? fallback;
  }

  _zoneLabel() {
    const labels = { Top: "oben", Bottom: "unten", "Top+Bottom": "oben + unten" };
    // 2026_10_13_CL: Geaendert: Fehlenden oder ungueltigen Zonenstatus ausdruecklich anzeigen.
    // Warum: Eine nicht verfuegbare Select-Entitaet ist keine bestaetigte Auswahl beider Zonen.
    // Wirkung: Die Detailansicht meldet Zone nicht verfuegbar statt oben + unten.
    // alt: Unbekannte Zustaende wurden als oben + unten dargestellt.
    return labels[this._state(this.config.zone_entity, "")] ?? "Zone nicht verfuegbar";
  }

  _zoneOption() {
    return this.config.zone ?? this._state(this.config.zone_entity, "Top+Bottom");
  }

  _expectedZoneKey() {
    return `airaluce-zone-control.expected-zone.${this.config.zone_entity}`;
  }

  _rememberExpectedZone() {
    sessionStorage.setItem(this._expectedZoneKey(), this._zoneOption());
  }

  _externalZoneMessage() {
    if (this.config.compact) return "";
    const expected = sessionStorage.getItem(this._expectedZoneKey());
    const active = this._state(this.config.zone_entity, "Top+Bottom");
    if (!expected || expected === active) return "";
    return `Achtung: Bedienfokus extern auf ${this._zoneLabel()} geändert.`;
  }

  _thumbTop(value) {
    return 9 + (100 - Number(value)) * 2.02;
  }

  _colorCss(value) {
    const color = Math.max(0, Math.min(100, Number(value) || 0));
    const warm = [255, 213, 128];
    const white = [255, 255, 255];
    const cold = [173, 216, 230];
    const start = color <= 50 ? warm : white;
    const end = color <= 50 ? white : cold;
    const ratio = color <= 50 ? color / 50 : (color - 50) / 50;
    const rgb = start.map((channel, index) => Math.round(channel + (end[index] - channel) * ratio));
    return `rgb(${rgb.join(",")})`;
  }

  async _call(domain, service, data) {
    await this._hass.callService(domain, service, data);
  }

  async _setFocus() {
    const option = this._zoneOption();
    if (this._state(this.config.zone_entity) !== option) {
      await this._call("select", "select_option", {
        entity_id: this.config.zone_entity,
        option,
      });
    }
  }

  _onInput(event) {
    const input = event.composedPath().find((element) => element?.dataset?.kind);
    if (!input) return;
    // 2026_10_13_CL: Geaendert: Neuaufbau der Karte waehrend einer Slidereingabe sperren.
    // Warum: HA-Rueckmeldungen koennen eintreffen, waehrend der Benutzer den Regler zieht.
    // Wirkung: _render behaelt den aktiven Regler bis zum Abschluss des Stellbefehls bei.
    // alt: Jede HA-Aktualisierung ersetzte den Regler durch den zuletzt gemeldeten Wert.
    this._editing = true;
    const value = input.value;
    if (input.dataset.kind === "brightness") {
      this.shadowRoot.querySelector("[data-current-brightness]").textContent = `${value} %`;
      this.shadowRoot.querySelector("[data-brightness-thumb]").style.top = `${this._thumbTop(value)}px`;
    } else if (input.dataset.kind === "color") {
      this.shadowRoot.querySelector("[data-color-thumb]").style.top = `${this._thumbTop(value)}px`;
      this.shadowRoot.querySelector("[data-color-dot]").style.background = this._colorCss(value);
    }
  }

  // 2026_10_21_CL: Geaendert: Slider-Sollwerte bis zur HA-Bestaetigung getrennt vormerken.
  // Warum: Serviceabschluss und Empfang des neuen Light-Zustands koennen zeitlich auseinanderliegen.
  // Wirkung: Alte Rueckmeldungen setzen den Regler nicht kurz zurueck; nach zehn Sekunden gilt wieder HA.
  // alt: Nach dem Loslassen wurde sofort der zuletzt bekannte, eventuell noch alte HA-Wert gerendert.
  _holdPendingValue(kind, value) {
    this._clearPendingValue(kind);
    this._pendingValues ??= {};
    const pending = { value, zone: this._zoneOption() };
    this._pendingValues[kind] = pending;
    pending.timer = setTimeout(() => {
      if (this._pendingValues[kind] !== pending) return;
      this._clearPendingValue(kind);
      this._render();
    }, 10000);
    return pending;
  }

  _clearPendingValue(kind) {
    const pending = this._pendingValues?.[kind];
    if (!pending) return;
    clearTimeout(pending.timer);
    delete this._pendingValues[kind];
  }

  disconnectedCallback() {
    for (const kind of Object.keys(this._pendingValues ?? {})) this._clearPendingValue(kind);
  }

  async _onChange(event) {
    const input = event.composedPath().find((element) => element?.dataset?.kind);
    if (!input || this.config.compact) return;
    // 2026_10_13_CL: Geaendert: Eingabewert vor dem Zonenwechsel sichern und Sperre in finally loesen.
    // Warum: Asynchrone Serviceaufrufe duerfen den abgeschlossenen Benutzerwert nicht veraendern.
    // Wirkung: Der Stellbefehl nutzt den erfassten Wert; danach wird die HA-Rueckmeldung angezeigt.
    // alt: input.value wurde erst nach await gelesen; eine durchgehende Render-Sperre fehlte.
    const kind = input.dataset.kind;
    const value = Number(input.value);
    let pending;
    this._editing = true;
    try {
      await this._setFocus();
      pending = this._holdPendingValue(kind, value);
      if (kind === "brightness") {
        const brightness = Math.round(value * 2.55);
        if (brightness === 0) {
          await this._call("light", "turn_off", { entity_id: this.config.light_entity });
        } else {
          await this._call("light", "turn_on", {
            entity_id: this.config.light_entity,
            brightness,
          });
        }
        return;
      }

      const colorTempKelvin = Math.round(4000 + value * 50);
      await this._call("light", "turn_on", {
        entity_id: this.config.light_entity,
        color_temp_kelvin: colorTempKelvin,
      });
    } catch (error) {
      if (pending && this._pendingValues?.[kind] === pending) this._clearPendingValue(kind);
      throw error;
    } finally {
      this._editing = false;
      this._render();
    }
  }

  // 2026_10_13_CL: Geaendert: Zonenklicks ausschliesslich ueber den delegierten ShadowRoot-Handler bedienen.
  // Warum: Ein zusaetzlicher Klickhandler auf .card fuehrte dieselbe Navigation nochmals aus.
  // Wirkung: Pro Klick wird der Zonenwechsel mit anschliessender Navigation nur einmal gestartet.
  // alt: _render registrierte neben diesem Handler einen weiteren Handler auf jeder kompakten Karte.
  async _onClick(event) {
    const button = event.composedPath().find((element) => element?.dataset?.action);
    if (!button || !this.config.compact) return;
    await this._navigateToControl();
  }

  async _navigateToControl() {
    this._rememberExpectedZone();
    await this._setFocus();
    if (typeof this._hass.navigate === "function") {
      this._hass.navigate(this.config.navigation_path);
      return;
    }
    window.history.pushState({}, "", this.config.navigation_path);
    window.dispatchEvent(new Event("location-changed"));
  }

  _render() {
    if (!this._hass || !this.config || this._editing) return;
    // 2026_10_13_CL: Geaendert: Light-Attribute auswerten und Vorschau-Rohfarbe direkt auf Prozent abbilden.
    // Warum: Light-Zustaende sind on/off; Kelvin und Firmware-Rohfarbe steigen beide von warm nach kalt.
    // Wirkung: Gueltige Sliderwerte, Helligkeit 0 bei Aus und gleiche Farbrichtung in Vorschau und Detail.
    // alt: on/off wurde numerisch umgerechnet und die Vorschau-Farbrichtung zusaetzlich invertiert.
    const light = this._hass.states[this.config.light_entity];
    const attributes = light?.attributes ?? {};
    const brightnessValue = this.config.preview_brightness_entity
      ? Number(this._state(this.config.preview_brightness_entity)) / 2.55
      : light?.state === "on" ? Number(attributes.brightness ?? 0) / 2.55 : 0;
    // 2026_10_22_CL: Geaendert: Farbposition der Detailkarte bei off aus dem Zonensensor lesen.
    // Warum: HA veroeffentlicht bei ausgeschaltetem Licht keine Farbtemperatur.
    // Wirkung: Farbe bleibt erhalten; bei on gelten weiter Kelvin, Helligkeit und Stellbefehle bleiben gleich.
    // alt: Fehlende Kelvin wurden als 4000 K dargestellt und zogen den Farbregler auf warm.
    const offColorEntity = {
      Top: this.config.color_top_entity,
      Bottom: this.config.color_bottom_entity,
      "Top+Bottom": this.config.color_bottom_entity,
    }[this._state(this.config.zone_entity, "")];
    const offColorValue = Number(this._hass.states[offColorEntity]?.state);
    const colorValue = this.config.preview_color_entity
      ? Number(this._state(this.config.preview_color_entity)) / 2.55
      : !this.config.compact && light?.state === "off" && Number.isFinite(offColorValue)
        ? offColorValue / 2.55
        : (Number(attributes.color_temp_kelvin ?? 4000) - 4000) / 50;
    const values = {
      brightness: Number.isFinite(brightnessValue) ? Math.round(Math.max(0, Math.min(100, brightnessValue))) : 0,
      color: Number.isFinite(colorValue) ? Math.round(Math.max(0, Math.min(100, colorValue))) : 0,
    };
    // 2026_10_21_CL: Geaendert: Sollwerte erst bei passender Rueckmeldung oder Zonenwechsel freigeben.
    // Warum: Auch fremde HA-Updates koennen noch alte Light-Attribute enthalten; Firmwarewerte werden gerundet.
    // Wirkung: Der Regler bleibt stabil, akzeptiert einen Prozentpunkt Rundung und folgt danach wieder HA.
    // alt: Das erste Rendern nach Serviceabschluss zeigte bedingungslos die vorhandenen Light-Attribute.
    for (const [kind, pending] of Object.entries(this._pendingValues ?? {})) {
      if (pending.zone !== this._state(this.config.zone_entity)
          || !["on", "off"].includes(light?.state)
          || Math.abs(values[kind] - pending.value) <= 1) {
        this._clearPendingValue(kind);
      } else {
        values[kind] = pending.value;
      }
    }
    const { brightness, color } = values;
    const title = this.config.compact ? this.config.title : this._zoneLabel();
    const externalZoneMessage = this._externalZoneMessage();
    const disabled = this.config.compact ? "disabled" : "";
    const action = this.config.compact ? "open" : "";

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        .card { box-sizing: border-box; width: fit-content; max-width: 100%; min-height: 164px; padding: 16px; background: var(--card-background-color, white); border-radius: var(--ha-card-border-radius, 12px); box-shadow: var(--ha-card-box-shadow, none); color: var(--primary-text-color); }
        .card.compact { cursor: pointer; min-height: 128px; }
        h2 { margin: 0 0 14px; font-size: 1.15rem; font-weight: 600; letter-spacing: 0; text-transform: none; }
        .focus-note { margin: -4px 0 12px; padding: 8px 10px; border-left: 3px solid #d99500; background: #fff3d6; color: #5b4100; font-size: .9rem; }
        .controls { display: flex; align-items: stretch; gap: 24px; width: max-content; max-width: 100%; min-height: 290px; }
        .control { display: grid; grid-template-columns: 82px 38px; grid-template-rows: auto 1fr auto; column-gap: 20px; min-width: 142px; }
        .control strong { grid-column: 1 / -1; margin-bottom: 8px; }
        .vertical { grid-column: 1; grid-row: 2; width: 82px; height: 220px; appearance: slider-vertical; writing-mode: vertical-lr; direction: rtl; margin: 0; cursor: pointer; }
        .brightness-track { grid-column: 1; grid-row: 2; position: relative; width: 82px; height: 220px; border-radius: 9px; background: linear-gradient(to top, #000000 0%, #ffffff 100%); }
        .brightness-track input { position: absolute; inset: 0; width: 100%; height: 100%; margin: 0; opacity: 0; cursor: pointer; writing-mode: vertical-lr; direction: rtl; }
        .brightness-thumb { position: absolute; left: -7px; width: 96px; height: 22px; top: 9px; transform: translateY(-50%); box-sizing: border-box; border: 2px solid white; border-radius: 11px; background: #003249; box-shadow: 0 1px 4px rgba(0,0,0,.3); pointer-events: none; }
        .color-track { grid-column: 1; grid-row: 2; position: relative; width: 82px; height: 220px; border-radius: 9px; background: linear-gradient(to top, #ffd580 0%, #ffffff 50%, #add8e6 100%); }
        .color-track input { position: absolute; inset: 0; width: 100%; height: 100%; margin: 0; opacity: 0; cursor: pointer; writing-mode: vertical-lr; direction: rtl; }
        .color-thumb { position: absolute; left: -7px; width: 96px; height: 22px; top: 9px; transform: translateY(-50%); box-sizing: border-box; border: 2px solid white; border-radius: 11px; background: #003249; box-shadow: 0 1px 4px rgba(0,0,0,.3); pointer-events: none; }
        .labels { grid-column: 2; grid-row: 2; position: relative; height: 220px; font-size: .9rem; white-space: nowrap; }
        .labels span { position: absolute; left: 0; transform: translateY(-50%); }
        .labels span:nth-child(1) { top: 9px; }
        .labels span:nth-child(2) { top: 25%; }
        .labels span:nth-child(3) { top: 50%; }
        .labels span:nth-child(4) { top: 75%; }
        .labels span:nth-child(5) { top: 211px; bottom: auto; transform: translateY(-50%); }
        .color-labels { grid-column: 2; grid-row: 2; position: relative; height: 220px; padding: 0; font-size: .9rem; }
        .color-labels span { position: absolute; left: 0; white-space: nowrap; }
        .color-labels span:first-child { top: 0; }
        .color-labels span:last-child { bottom: 0; }
        .compact .controls { flex-direction: column; align-items: flex-start; min-height: auto; gap: 8px; width: max-content; }
        .compact .control { display: grid; grid-template-columns: auto; grid-template-rows: auto auto; min-width: 0; }
        .compact .vertical { grid-column: 1; grid-row: 2; width: 100%; height: 42px; appearance: auto; writing-mode: horizontal-tb; direction: ltr; pointer-events: none; }
        .compact .labels, .compact .color-labels, .compact .color-track, .compact .brightness-track { display: none; }
        .compact strong { font-size: .82rem; margin-bottom: 4px; }
        .compact .compact-color-dot { display: inline-block; width: 12px; height: 12px; margin-left: 5px; border-radius: 50%; vertical-align: -1px; border: 1px solid rgba(0,0,0,.25); }
        .compact .compact-color-hint { display: inline; font-weight: 400; }
        .compact .control[data-kind="color"] strong { display: flex; align-items: center; }
        .compact .control[data-kind="color"] { display: grid; }
        .compact .control[data-kind="color"]::after { content: ""; display: block; height: 0; }
        .compact .control[data-kind="brightness"] strong { display: block; }
        .compact .control[data-kind="brightness"] strong::after { content: ""; display: block; }
        @media (max-width: 500px) { .controls { gap: 16px; } .control { grid-template-columns: 72px 35px; min-width: 125px; } .vertical { width: 72px; } }
      </style>
      <section class="card ${this.config.compact ? "compact" : ""}" data-action="${action}">
        <h2>${title}</h2>
        ${externalZoneMessage ? `<p class="focus-note">${externalZoneMessage}</p>` : ""}
        <div class="controls">
          <label class="control" data-kind="brightness">
            <strong>Helligkeit <span data-current-brightness>${brightness} %</span></strong>
            <span class="brightness-track">
              <input data-kind="brightness" type="range" min="0" max="100" step="1" value="${brightness}" ${disabled}>
              <span class="brightness-thumb" data-brightness-thumb style="top: ${this._thumbTop(brightness)}px"></span>
            </span>
            <span class="labels"><span>100 %</span><span>75 %</span><span>50 %</span><span>25 %</span><span>aus</span></span>
          </label>
          <label class="control" data-kind="color">
            <strong>Farbe <span class="compact-color-dot" data-color-dot style="background: ${this._colorCss(color)}"></span></strong>
            <span class="color-track">
              <input data-kind="color" type="range" min="0" max="100" step="1" value="${color}" ${disabled}>
              <span class="color-thumb" data-color-thumb style="top: ${this._thumbTop(color)}px"></span>
            </span>
            <span class="color-labels"><span>kalt</span><span>warm</span></span>
          </label>
        </div>
      </section>`;
  }
}

customElements.define("airaluce-zone-control", AiraLuceZoneControl);
window.customCards = window.customCards || [];
window.customCards.push({
  type: "airaluce-zone-control",
  name: "AVITANA aira luce Zone Control",
  description: "Steuert Helligkeit und Farbe fuer die aktive Zone von AVITANA aira luce.",
});
