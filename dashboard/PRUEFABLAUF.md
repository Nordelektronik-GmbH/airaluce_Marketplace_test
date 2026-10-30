# AVITANA aira luce: Zonen und Slider pruefen

Stand Namensanzeige 2026-10-22: Sichtbare Produktnamen wurden auf
`AVITANA aira luce` vereinheitlicht. Technische Kennungen und die unten
verwendeten Bestands-Entity-IDs bleiben unveraendert. Die JavaScript-Ressource
verwendet jetzt `20261022-Vers46`; die aktuelle URL aus dem Package uebernehmen.

Stand: 2026-10-21. Der lokale Regressionstest prueft die Karte und die
Dashboard-YAML mit den bestaetigten HA-IDs. Live bestaetigt sind Zonenwechsel,
getrennte und gemeinsame Helligkeit/Farbe sowie Luefterstart mit 25 %, Betrieb
mit 50 % und Ausschalten.
Das kurze Zurueckspringen des unteren Farbreglers wurde mit Vers45 erneut
geprueft und trat laut Nutzerrueckmeldung nicht mehr auf; die Sensorwerte
bestaetigten die getrennte Farbaenderung auch nach der Wartezeit.
Die gemeinsam geprueften Dashboard-Bedienablaeufe sind damit abgeschlossen.
Firmware und Python-Integration wurden bei dieser Dashboard-Anpassung
nicht geaendert.

Die alten Dashboard-IDs sind fuer eine moegliche spaetere Rueckaenderung
im Aenderungskommentar vom 2026_10_20_CL in `dashboard/airaluce.yaml` erhalten.

## Live-Pruefergebnis 2026-10-21

Nachweise: vom Nutzer bereitgestellte HA-Zustaende, Screenshots und
Geraeteantworten von `/state`; keine automatisierte Fernpruefung durch den Assistenten.

| Pruefung | Ergebnis |
| --- | --- |
| Zonenwahl Top, Bottom, Top+Bottom | Korrekte Detailtitel und zugehoerige Werte |
| Helligkeit oben/unten getrennt | Nur die gewaehlte Zone geaendert; Gegenzone unveraendert |
| Helligkeit gemeinsam | Beide Zonen auf etwa 60 % / Rohwert 153 gestellt |
| Auswahl beider Zonen ohne Eingriff | Unterschiedliche Werte zunaechst erhalten |
| Erster Stellbefehl nach Auswahl beider Zonen | Farbwerte wie vorgesehen erst dabei angeglichen |
| Farbe oben/unten getrennt | Gegenzone und Helligkeiten unveraendert |
| Unterer Farbregler mit Vers45 | Kein Zurueckspringen mehr gemeldet; unten 35 -> 226, oben 48, beide Helligkeiten 56 |
| Farbe gemeinsam | Beide Rohwerte 135; HA-Farbtemperatur passend bei 6647 K; Helligkeiten 56 |
| Luefter 50 % und danach Aus | fan 128 -> 0; Lichtwerte und Auswahl unveraendert |
| Luefter normales Einschalten und danach Aus | fan 64 (25 %) -> 0; beide Helligkeiten 56, beide Farben 135, Power on=1 und Auswahl 3 unveraendert |

Ergaenzung vom 2026-10-21: Zusaetzlicher Ein-/Aus-Test des Luefters bestanden.
Geraetestatus nach normalem Einschalten:

```json
{"fan":64,"brightness":56,"color":135,"brightness_bottom":56,"color_bottom":135,"on":1,"selection":3,"control_mode_open":false}
```

Abschliessender Geraetestatus nach Ausschalten des Luefters:

```json
{"fan":0,"brightness":56,"color":135,"brightness_bottom":56,"color_bottom":135,"on":1,"selection":3,"control_mode_open":false}
```

Nicht durch diesen Durchlauf abgedeckt sind die Luefterstufen 75 % und 100 %,
Ein-/Aus- und Neustartfaelle des Gesamtgeraets sowie ein Langzeittest.
Auf der Merkliste bleiben die spaetere Namensvereinheitlichung bzw.
Rueckaenderung und die Pruefung des alten `switch.power_2` (unavailable/restored).
Vor einer Bereinigung erst Herkunft und Verweise klaeren; aktiv bleibt `switch.power`.

## Bereinigung alter Automationen 2026-10-21

Auf Nutzerfreigabe wurden ausschliesslich die zehn nicht verfuegbaren
HA-Automationseintraege entfernt, deren gespeicherte IDs mit der alten Vorlage
`E:\airaluce_alt9\Neuer Ordner (6)\automations.yaml` uebereinstimmten.
Die Datei auf E: bleibt unveraendert. Betroffen waren sieben alte
PlatformIO-Sendeautomationen (Luefterstufen, Helligkeit/Farbe je oben, unten,
beide) und drei Rueckspiegelungsautomationen (Helligkeit, Farbe, Luefter).

Vorher geprueft: alle zehn unavailable/restored, keine Verweise in den
geprueften HA-YAML-Dateien und beiden gespeicherten Lovelace-JSON-Dateien.
Die Entfernung erfolgte ueber die angemeldete HA-WebSocket-Schnittstelle,
nicht durch manuelle Bearbeitung von `.storage`.

Dateisicherung vor der Entfernung: `core.entity_registry` und die laufende
`automations.yaml` unter
`C:\Users\carst\AppData\Local\AiraLuce\ha-cleanup-backups\20261021-160904`.
Dies ist eine gezielte Dateisicherung, kein vollstaendiges HA-Backup.

Nachpruefung ueber HA: alle zehn Ziele aus Registry und aktuellen Zustaenden
entfernt, keine anderen Registry-Eintraege entfernt. Alle acht aktuellen
AiraLuce-Entitaeten bleiben registriert, Zustaende und Attribute unveraendert.
Andere alte Automationen und eine Namensvereinheitlichung wurden nicht angefasst.

Ergaenzung 2026-10-21: Auf Nutzerwunsch neun weitere Archivdateien unter
`E:\airaluce alt8`, `E:\airaluce_alt7`, `E:\airaluce_alt9` und `E:\Dashboard`
strukturiert auf Automation-IDs geprueft. Von 18 eindeutigen Archiv-IDs waren
acht noch als unavailable/restored in HA registriert; diese acht wurden nach
Abgleich der Registry-IDs und Verweispruefung ebenfalls entfernt. Die neun
Archivdateien selbst blieben unveraendert.

Die vier noch angezeigten Automation-Eintraege `automation.airaluce_helligkeit_oben_anzeige`,
`automation.airaluce_farbe_oben_anzeige`, `automation.airaluce_helligkeit_unten_anzeige`
und `automation.airaluce_farbe_unten_anzeige` kommen in keiner der neun Archive
vor. Auf Nutzerrueckfrage wurden sie als gleichartige alte AiraLuce-Reste
ebenfalls geprueft: alle vier unavailable/restored, ohne config_entry_id,
ohne aktive YAML-Definition/Verweise und ohne gespeicherte Dashboard-Referenz.
Nach separater Sicherung wurden genau diese vier Registry-Eintraege entfernt.
Sicherung: `C:\Users\carst\AppData\Local\AiraLuce\ha-cleanup-backups\20261021-163438`.
`light.smart_box_m1_status_led` gehoert nicht zur AiraLuce-Bereinigung und blieb
unveraendert. Die acht aktuellen AiraLuce-Geraeteentitaeten wurden nach beiden
Entfernungsrunden erneut bestaetigt.

## 1. Zuerst den Ist-Zustand festhalten

Keine parallele Bedienung ueber Webinterface, weitere Browser, Automationen
oder Geraetetasten waehrend der Tests. Die Zonenwahl ist ein gemeinsamer
Geraetezustand, kein eigener Zustand pro Browser.

1. Im Browser `http://GERAETE-IP/state` oeffnen und die JSON-Antwort notieren.
2. In HA unter Entwicklerwerkzeuge -> Zustaende die tatsaechlichen IDs suchen:
   `select.zone`, `light.airaluce`, `fan.airaluce_fan`.
   Falls die IDs anders heissen, die Dashboard-Konfiguration entsprechend
   anpassen. Anzeigenamen reichen fuer diesen Vergleich nicht aus.
3. Fuer Select den Zustand und das Attribut `options` notieren; fuer Light
   Zustand, `brightness` und `color_temp_kelvin` notieren.

Die bestaetigten Vorschau-Sensoren heissen `sensor.brightness_top`,
`sensor.brightness_bottom`, `sensor.color_top` und `sensor.color_bottom`.

Soll: `/state` enthaelt `selection` mit 1, 2 oder 3. In HA sind die Select-Optionen
`Top`, `Bottom`, `Top+Bottom`. Light hat den Zustand `on` oder `off`;
Helligkeit und Farbtemperatur stehen in seinen Attributen, nicht im Zustand.

Fehlt `selection`, stimmt der laufende Firmwarestand nicht mit dem aktuellen
Quellcode ueberein. Die Integration nimmt bei fehlendem Feld beide Zonen an.
Eine geaenderte Firmware braucht einen Firmware-Upload, nicht nur `uploadfs`.

## 2. Korrigierte Karte nach HA uebernehmen

1. `dashboard/www/airaluce-zone-control.js` nach
   `<HA-Konfiguration>/www/airaluce-zone-control.js` uebertragen.
   Die korrigierte `dashboard/airaluce.yaml` ebenfalls an den in HA
   registrierten Dashboard-Dateipfad uebertragen (laut Package `airaluce.yaml`).
2. In der bestehenden Lovelace-Ressourcenregistrierung die aktuelle URL aus
   `dashboard/packages/airaluce_dashboard.yaml` uebernehmen, einschliesslich
   des Versionsparameters `?v=...`. Keine zweite Registrierung
   derselben Karte hinzufuegen und keine bestehende HA-Konfiguration ersetzen.
3. HA-Konfiguration pruefen und die YAML-Ressourcen durch einen HA-Neustart
   laden. Danach den Dashboard-Browser vollstaendig neu laden.
4. Bei Zweifel in den Browser-Netzwerkwerkzeugen pruefen, dass die JS-Datei
   mit der im Package eingetragenen Version erfolgreich geladen wird.

Ein PlatformIO-/LittleFS-Upload uebertraegt diese HA-Dateien nicht.

## 3. Zonenauswahl ohne Dashboard testen

In Entwicklerwerkzeuge -> Aktionen ausfuehren, mit der echten Select-ID:

```yaml
action: select.select_option
target:
   entity_id: select.zone
data:
  option: Top
```

Danach mindestens einen HA-Abfragezyklus abwarten und `/state` im Browser
erneut laden. Denselben Test fuer `Bottom` und  wiederholen.

| Aktion | `/state.selection` | Select-Zustand in HA |
| --- | --- | --- |
| Top | 1 | Top |
| Bottom | 2 | Bottom |
| Top+Bottom | 3 | Top+Bottom |

Falls das nicht stimmt: direkt `http://GERAETE-IP/setSelection?selection=1`
oeffnen und danach `/state` neu laden. Fuer unten mit `selection=2` wiederholen.
Diese Aufrufe aendern den Bedienfokus, sollen allein aber keine Lichtwerte
angleichen.

- Direktaufruf funktioniert, HA-Aktion nicht: HA-Integration, Zielgeraet und
  Entity-ID pruefen; HA-Protokoll nach `airaluce` filtern.
- Auch Direktaufruf funktioniert nicht: laufende Firmware bzw. Geraet pruefen.
- Auswahl springt spaeter zurueck: weitere Bedienung oder Automationen suchen.

## 4. Light ohne Dashboard testen

Master-Power einschalten. Erst Top auswaehlen, dann diese Aktion ausfuehren:

```yaml
action: light.turn_on
target:
entity_id: light.airaluce
data:
brightness: 64
```

Soll: oben etwa 25 %, unten unveraendert. In `/state` betrifft das `brightness`,
nicht `brightness_bottom`. Rundungsabweichungen von wenigen Rohwertschritten
sind durch die Firmware-Prozentumrechnung normal.

Danach Bottom auswaehlen und mit `brightness: 191` testen: unten etwa 75 %,
oben unveraendert. Anschliessend Top+Bottom auswaehlen und `brightness: 128`
senden: beide etwa 50 %. Der erste Stellbefehl in Top+Bottom gleicht laut
Firmware auch die Farbwerte an; die blosse Auswahl noch nicht.
Damit funktioniert dieser Helligkeitsbefehl getrennt für oben.

Also als Nächstes unter Aktionen zuerst unten auswählen:
action: select.select_option
target:
  entity_id: select.zone
data:
  option: Bottom

Danach separat ausführen:
action: light.turn_on
target:
  entity_id: light.airaluce
data:
  brightness: 191

Erwartung: unten ungefähr 191, oben weiterhin 63.

Farbe separat mit `color_temp_kelvin: 4000`, `6500` und `9000` testen:
warm, Mitte, kalt. Die zugehoerigen API-Rohwerte sind etwa 0, 128 und 255.
Ein Farb-Stellbefehl ueber `light.turn_on` kann eine ausgeschaltete Zone
einschalten; deshalb diesen Test mit bereits eingeschaltetem Licht ausfuehren.

## 5. Dashboard und Fan testen

1. Kachel oben oeffnen: Titel oben, Select Top, API-Auswahl 1.
2. Helligkeit langsam ziehen, dabei einen HA-Abfragezyklus abwarten, erst dann
   loslassen. Der Regler darf waehrend des Ziehens nicht ersetzt werden.
3. Nach dem Loslassen Werte aus Karte, Light-Attribut und `/state` vergleichen.
   Besonders den Farbregler unten pruefen: Ein alter HA-Wert darf auch kurz
   nach dem Loslassen nicht mehr sichtbar werden. Die Karte behaelt den
   Sollwert bis zur Bestaetigung (Rundung bis ein Prozentpunkt) bei.
   Bei Servicefehler, Zonenwechsel oder nach zehn Sekunden ohne Bestaetigung
   wird der tatsaechliche HA-Stand wieder angezeigt; dies nicht mit einer
   erfolgreich bestaetigten Aenderung verwechseln.
4. Mit unten und oben + unten wiederholen. Nur die gewaehlte Zone darf auf
   Stellbefehle reagieren; beide nur bei Top+Bottom.
5. Warm/Kalt-Regler mit der Vorschau auf der Hauptansicht vergleichen.
6. Fan-Geschwindigkeit aendern: `/state.fan` darf sich aendern, `selection`
   und Lichtwerte muessen dabei unveraendert bleiben.

Funktionieren die HA-Aktionen aus Schritt 3/4, aber nicht die Karte, liegt der
Fehler im Frontend, einer alten JS-Ressource oder dessen Entity-Konfiguration.
Funktionieren bereits die Aktionen nicht, hilft weiteres Slider-Tuning nicht.

## Fuer die gemeinsame Auswertung

Zuerst nur diese Ergebnisse schicken: JSON von `/state`, tatsaechliche Select-ID
mit Zustand/Optionen und Ergebnis des Top-Tests aus Schritt 3. Keine Tokens,
Passwoerter oder vollstaendigen HA-Konfigurationsdateien erforderlich.

Lokaler Regressionstest im Projekt (15 Tests, einschliesslich verzoegerter
Slider-Bestaetigungen, Fehler/Ablauf, YAML-Entity-Verweise und Vorschauzuordnung):

```powershell
node --test --test-reporter=spec tests/dashboard/test_zone_control.cjs
```

Voraussetzungen: Node.js sowie der vorhandene PlatformIO-Python unter
`~/.platformio/penv` mit PyYAML fuer die YAML-Pruefung. Dieser Test liest nur
lokale Dateien; er greift nicht auf Home Assistant oder das Geraet zu.