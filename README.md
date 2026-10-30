# AVITANA aira luce Home-Assistant-Integration

Die AVITANA aira luce Integration bindet eine kompatible AVITANA aira® luce Leuchte (im Folgenden „AVITANA aira luce System“) über das lokale Netzwerk in Home Assistant ein. Sie stellt Lichtsteuerung, Lüfterstufen, Zonenauswahl, Geräteschalter und Statussensoren als Home-Assistant-Entitäten bereit.

Das AVITANA aira luce System kombiniert LED-Beleuchtung mit integrierter Plasma-Luftreinigung. Es kann unabhängig von Home Assistant und sogar ohne Heim-WLAN betrieben werden. Die Bedienung kann auch wahlweise über die Fernbedienung oder über das integrierte Web-Interface erfolgen. Dieses ist entweder über das Heimnetzwerk oder über den integrierten lokalen Wireless Access Point (im Folgenden auch AP) erreichbar. Die Home-Assistant-Integration und das mitgelieferte Dashboard sind optionale Erweiterungen zur Einbindung in Home Assistant.

Dieses Repository ist derzeit ein Testrepository für die benutzerdefinierte Installation. Die Integration ist nicht im offiziellen HACS-Katalog gelistet.

## Inhalt

- [Funktionen in Home Assistant](#funktionen-in-home-assistant)
- [Voraussetzungen](#voraussetzungen)
- [Gerätebetrieb ohne Home Assistant](#gerätebetrieb-ohne-home-assistant)
- [Gerät mit dem Heimnetzwerk verbinden](#gerät-mit-dem-heimnetzwerk-verbinden)
- [Integration installieren](#integration-installieren)
- [Integration hinzufügen](#integration-hinzufügen)
- [Einrichtung prüfen](#einrichtung-prüfen)
- [Optionales Dashboard installieren](#optionales-dashboard-installieren)
- [Einschränkungen und Netzwerk](#einschränkungen-und-netzwerk)
- [Fehlerbehebung](#fehlerbehebung)
- [Support und Lizenz](#support-und-lizenz)

## Funktionen in Home Assistant

- Licht über Home Assistant ein- und ausschalten sowie Helligkeit und Farbtemperatur steuern.
- Die zu steuernde Lichtzone auswählen: oben, unten oder beide Zonen.
- Lüfter ein- und ausschalten sowie eine von vier Geschwindigkeitsstufen wählen.
- Den Geräte Hauptschalter ein- und ausschalten.
- Statuswerte für Helligkeit und Farbe der oberen und unteren Zone auslesen.
- Die Entitäten in Home-Assistant-Dashboards, Automationen und Szenen verwenden.
- Die lokale Weboberfläche ergänzend zu Home Assistant nutzen. Sie ist entweder im Heimnetzwerk oder über den integrierten Wireless Access Point erreichbar und funktioniert auch ohne Home Assistant.

## Voraussetzungen

- Ein kompatibles AVITANA aira luce System mit passender Firmware.
- Für die Integration: Home Assistant 2026.9.0 oder neuer.
- Für die Integration: Gerät und Home Assistant müssen sich über das lokale Netzwerk gegenseitig erreichen können.
- Für die benutzerdefinierte Installation: Zugriff auf das öffentliche GitHub-Repository und HACS beziehungsweise den Marketplace der verwendeten Home-Assistant-Version.
- Für das optionale Dashboard: Zugriff auf den Home-Assistant-Konfigurationsordner und die unten beschriebenen Dashboard-Dateien.

## Gerätebetrieb ohne Home Assistant

Home Assistant ist für den Betrieb des Geräts nicht erforderlich. Das System lässt sich über die Fernbedienung oder über die lokale Weboberfläche bedienen. Die Weboberfläche ist im Heimnetzwerk über die Geräte-IP oder ohne Heim-WLAN über den Wireless Access Point erreichbar.

Bei einem Gerät ohne gespeicherte WLAN-Konfiguration startet der Wireless Access Point (AP) beim Einschalten automatisch. Verbinde Smartphone, Tablet oder Computer mit dem Setup-WLAN und öffne anschließend die Geräteadresse (IP-Adresse) im Browser. Dadurch öffnet sich die Steuerungs-Hauptseite. Über seine Hauptseite lässt sich das Gerät bedienen.

Standardwerte des APs für das erste Setup:

| Einstellung | Standardwert |
| --- | --- |
| WLAN-Name (SSID) | `AiraLuce-Setup` |
| WLAN-Passwort | `AiraLuce123` |
| Geräteadresse | `http://192.168.4.1` |

Die Firmware des APs wählt bei belegtem Standard-Setup-Netz, also wenn es nicht verfügbar ist, automatisch ein alternatives Setup-Netz mit anderer AiraLuce-Setup Nummer und anderer IP-Adresse aus (also die Firmware wählt die IP-Adresse mit dem nächsten freien Subnetz aus). In diesem Fall zeigt die SSID die ausgewählte Nummer beziehungsweise IP-Adresse. Beispiel: Bei der SSID `AiraLuce-Setup2_IP192.168.5.1` verbindest du dich mit diesem WLAN und öffnest `http://192.168.5.1` im Browser. Die Firmware zeigt dieses auch am Ende der Hochlaufphase des AVITANA aira luce Systems in einem Blinkmuster, wo in diesem Beispiel (Fall AiraLuce-Setup2) am Ende 2-mal langsam geblinkt wird. Verwende immer die SSID und IP-Adresse, die das Gerät tatsächlich anzeigt. Bei der Standard-SSID `AiraLuce-Setup` lautet die Adresse `http://192.168.4.1`und hier wird dann nur einmal langsam am Ende der Hochlaufphase des Systems geblinkt.
In allen Fällen nach dem Verbinden mit der jeweiligen SSID mit dem gleichen WLAN-Passwort `AiraLuce123`und danach im Browser der Eingabe der tatsächlichen IP-Adresse mit Enter öffnet sich die lokale Geräteoberfläche, also die sogenannte Hauptseite des Web-Interfaces.

Ein Smartphone kann beim Verbinden melden, dass dieses WLAN keinen Internetzugang hat. Für die lokale Geräteoberfläche ist kein Internetzugang erforderlich; bleibe mit dem Setup-WLAN verbunden.

Bei einem bereits mit Heim-WLAN-Zugangsdaten konfigurierten Gerät startet der Wireless Access Point bei einem Ausfall des Heim-WLANs nicht zwangsläufig automatisch. Dazu erst einmal erklärt, die Steuerungs-Hauptseite und das WLAN-Einrichtungsformular sind zwei verschiedene Ansichten. Um das WLAN-Einrichtungsformular zu öffnen, halte Taste 3 bei der Fernbedienung etwa fünf Sekunden gedrückt. Das öffnet den Setup-Access-Point und das Einrichtungsformular. Dabei werden gespeicherte WLAN-Zugangsdaten gelöscht. Das ist auch der Weg, um bei einem bereits mit Heim-WLAN-Zugangsdaten konfigurierten Gerät, dessen Access Point nicht automatisch startet, wieder ins WLAN-Setup zu gelangen. Für die erneute Nutzung mit Home Assistant müssen die Zugangsdaten des Heim-WLANs danach neu eingegeben werden. Weitere Informationen zum Verlassen des Formulars über **Zur Hauptseite** stehen im Abschnitt [WLAN-Einrichtungsformular verlassen](#wlan-einrichtungsformular-verlassen).

## Gerät mit dem Heimnetzwerk verbinden

Die folgenden Schritte richten das Heim-WLAN für die Home-Assistant-Anbindung ein. Die Fernbedienung funktioniert auch ohne Heim-WLAN. Für den Browserzugriff ohne Heim-WLAN muss der Wireless Access Point aktiv sein; wie du ihn startest, steht im Abschnitt [Gerätebetrieb ohne Home Assistant](#gerätebetrieb-ohne-home-assistant).

### WLAN-Einrichtungsformular öffnen

Die Steuerungs-Hauptseite und das WLAN-Einrichtungsformular sind zwei verschiedene Ansichten. Um das WLAN-Einrichtungsformular zu öffnen, halte Taste 3 bei der Fernbedienung etwa fünf Sekunden gedrückt. Der Access Point wird gestartet und das Formular geöffnet. Dabei werden bereits gespeicherte WLAN-Zugangsdaten gelöscht.

Verbinde dich mit dem angezeigten Setup-WLAN. Verwende das Setup-Passwort aus der Tabelle und die anderen Angaben im Abschnitt [Gerätebetrieb ohne Home Assistant](#gerätebetrieb-ohne-home-assistant). Um das WLAN-Einrichtungsformular im Browser zu öffnen, muss die tatsächliche IP-Adresse mit Enter eingegeben werden. Bei der Standard-SSID `AiraLuce-Setup` lautet die Adresse `http://192.168.4.1`. Wird wegen 30 Sekunden Inaktivität auf dem WLAN-Einrichtungsformular schon wieder die Hauptseite angezeigt muss die Taste 3 bei der Fernbedienung etwa fünf Sekunden erneut gedrückt werden, um automatisch das Formular wieder erneut zu öffnen. Sollte sich nicht automatisch das Formular durch eine automatische Umschaltung öffnen, dann öffne anschließend `http://<AP-IP>/control-mode/setup` im Browser. Ersetze `<AP-IP>` durch die tatsächlich angezeigte Adresse, zum Beispiel `192.168.5.1`.

Bei einem Gerät ohne gespeicherte WLAN-Zugangsdaten startet der Access Point beim Einschalten automatisch. Wenn du dich bereits auf der Steuerungs-Hauptseite befindest, öffnet Taste 3 ebenfalls das WLAN-Einrichtungsformular. Startet der Access Point bei einem zuvor konfigurierten Gerät nach einem WLAN-Ausfall nicht automatisch, öffnet der fünfsekündige Tastendruck ihn erneut. Für die spätere Home-Assistant-Nutzung müssen die Zugangsdaten des Heim-WLANs danach neu eingegeben werden.

### Heim-WLAN einrichten

1. Im WLAN-Einrichtungsformular das Heim-WLAN auswählen oder dessen SSID eingeben.
2. Das WLAN-Passwort eingeben und **Konfiguration anwenden** auswählen.
3. Die Seite prüft die WLAN-Zugangsdaten. Bei ungültigen Daten erscheint eine Fehlermeldung. Korrigiere SSID oder Passwort und versuche es erneut.
4. Bei gültigen Daten erscheint eine Meldung mit der vom Router vergebenen Geräte-IP-Adresse. Notiere diese Adresse. Wenn ein Android-Wandschalter als Display für das Webinterface verwendet wird, trage dort diese Geräte-IP als Zieladresse ein.
5. Bestätige die Meldung. Danach wird die Konfiguration gespeichert und die WLAN-Verbindung hergestellt. Warte auf die Rückmeldung, ob die Verbindung erfolgreich war.
6. Öffne auf einem Gerät im Heimnetzwerk `http://<GERÄTE-IP>/api/info` mit der zuvor angezeigten IP-Adresse. Eine JSON-Antwort bestätigt, dass die Geräte-API erreichbar ist.

### WLAN-Einrichtungsformular verlassen

Wenn du das WLAN-Einrichtungsformular über den Web Access Point geöffnet hast und eine alternative Setup-Nummer ab Setup 2 verwendest, erscheint beim manuellen Klick auf **Zur Hauptseite** ein Dialog, ob die aktuelle AP-IP beibehalten oder eine freie Setup-IP gesucht werden soll. **OK** behält die aktuelle Adresse bei. **Abbrechen** sucht eine freie Setup-Nummer und startet den Access Point gegebenenfalls mit einer anderen SSID und IP neu. Verbinde dich dann erneut mit der angezeigten SSID und öffne deren IP-Adresse im Browser.

Nach 30 Sekunden ohne Eingabe kehrt das Formular automatisch zur Steuerungs-Hauptseite zurück. Dabei erscheint kein IP-Auswahldialog und die aktuelle AP-IP bleibt erhalten.

### Alternative Setup-IP speichern

Die mit **Abbrechen** neu ausgewählte AP-Setup-Nummer wird nicht schon durch die Auswahl im Dialog gespeichert. Öffne nach der Rückkehr die Steuerungs-Hauptseite über den Access Point und betätige dort erstmals einen Slider oder den Gerätemaster-Schalter. Dabei merkt sich die Firmware die gerade verwendete Setup-Nummer als bevorzugte Nummer für den nächsten AP-Start, sofern diese dann noch verfügbar ist.

Unterscheide diese AP-IP von der Heimnetz-IP: Die Meldung nach dem WLAN-Zugangstest zeigt die vom Router vergebene Heimnetz-IP. Verwende diese Adresse, wenn ein Android-Wandschalter das Webinterface über das Heim-WLAN aufrufen soll. Die AP-IP gilt nur für den direkten Zugriff über das Setup-WLAN.

### Weitere Anmerkungen 

Die IP-Adresse wird derzeit vom Router per DHCP vergeben. Sie kann sich ändern. Eine DHCP-Reservierung im Router hilft, die Adresse dauerhaft gleich zu halten. Eine feste IP-Adresse lässt sich in der Integration nicht konfigurieren.

Wenn die WLAN-Konfiguration erfolgreich übernommen wurde, wird der Setup-Access-Point normalerweise beendet. Das lokale Webinterface ist danach über die IP-Adresse im Heimnetzwerk erreichbar.

## Integration installieren

Repository-Adresse:

[https://github.com/Nordelektronik-GmbH/airaluce_Marketplace_test](https://github.com/Nordelektronik-GmbH/airaluce_Marketplace_test)

### Installation über HACS

Für den aktuellen Teststand kann das Repository als benutzerdefiniertes HACS-Repository hinzugefügt werden. HACS muss bereits installiert und eingerichtet sein.
Die aktuelle Installationsanleitung für HACS steht unter [hacs.xyz](https://www.hacs.xyz/).

1. In Home Assistant **HACS → Integrationen** öffnen.
2. Das Menü oben rechts öffnen und **Benutzerdefinierte Repositories** auswählen.
3. Die Repository-Adresse eintragen und als Kategorie **Integration** auswählen.
4. Das Repository hinzufügen und anschließend **AVITANA aira luce** in HACS öffnen.
5. **Herunterladen** auswählen und den Dialog abschließen.
6. Home Assistant neu starten.



### Installation über den Home Assistant Marketplace

HACS wird ab Home Assistant 2026.11 als Marketplace in Home Assistant integriert. Die Menüführung kann sich je nach Home-Assistant-Version unterscheiden. Verwende diesen Weg, sobald der Marketplace in deiner Installation verfügbar ist.

1. **Einstellungen → Marketplace** öffnen.
2. Im Menü die Funktion zum Hinzufügen eines benutzerdefinierten Repositorys öffnen.
3. Die Repository-Adresse eintragen und als Typ **Integration** auswählen.
4. Das Repository hinzufügen, **AVITANA aira luce** installieren und Home Assistant anschließend neu starten.

## Integration hinzufügen

Nach Installation und Neustart:

1. **Einstellungen → Geräte & Dienste → Integrationen** öffnen.
2. Unter **Entdeckt** die Karte **AVITANA aira luce** suchen und **Hinzufügen** auswählen.
3. Im Dialog das erkannte Gerät auswählen und die Einrichtung bestätigen.
4. Falls keine Karte unter **Entdeckt** erscheint, **Integration hinzufügen** auswählen und nach **AVITANA aira luce** suchen.
5. In der manuellen Einrichtung Host/IP-Adresse und Port eingeben. Verwende den Standardport `80`, sofern die Geräte-Firmware nicht ausdrücklich anders konfiguriert wurde.
6. Die Einrichtung abschließen.

Der manuelle Einrichtungsdialog fragt nach Host/IP-Adresse und Port. Er fragt nicht nach einem Anzeigenamen, Benutzernamen, Passwort oder Token.

Die automatische Erkennung verwendet das lokale Zeroconf/mDNS. Im Heimnetz ist das Gerät außerdem üblicherweise unter `http://airaluce.local` erreichbar. Wenn der Router oder das Netzwerk mDNS nicht weiterleitet, verwende die IP-Adresse.

## Einrichtung prüfen

Öffne **Einstellungen → Geräte & Dienste** und prüfe, ob AVITANA aira luce als eingerichtete Integration und Gerät erscheint. Je nach Home-Assistant-Entity-Registry können die Entity-IDs abweichen; typische Entitäten sind:

| Funktion | Typische Entity-ID | Verwendung |
| --- | --- | --- |
| Licht | `light.airaluce` | Ein/Aus, Helligkeit und Farbtemperatur der ausgewählten Zone |
| Lüfter | `fan.airaluce_fan` | Ein/Aus und vier Lüfterstufen |
| Zonenauswahl | `select.zone` | `Top`, `Bottom` oder `Top+Bottom` auswählen |
| Geräte Hauptschalter | `switch.power` | Geräte Hauptschalter ein- oder ausschalten |
| Statussensoren | `sensor.brightness_top`, `sensor.brightness_bottom`, `sensor.color_top`, `sensor.color_bottom` | Helligkeits- und Farbwerte der Zonen |

Die tatsächlichen Entity-IDs findest du unter **Einstellungen → Geräte & Dienste → AVITANA aira luce → Entitäten** oder in den Entwicklerwerkzeugen unter **Zustände**.

## Optionales Dashboard installieren

Die Integration funktioniert ohne das mitgelieferte Dashboard. Das Dashboard ist eine zusätzliche Lovelace-Oberfläche und setzt die passende Geräte-/Firmwarevariante sowie die von der YAML-Datei erwarteten Entitäten voraus. Wenn deine Entity-IDs abweichen, müssen die Verweise in der Dashboard-YAML angepasst werden.

Kopiere die Dateien in die Home-Assistant-Konfiguration (`\\HOMEASSISTANT\config` ist ein mögliches Windows-Samba-Beispiel):

| Quelldatei/-ordner im Repository | Ziel im Home-Assistant-Konfigurationsordner |
| --- | --- |
| `dashboard/airaluce.yaml` | `airaluce.yaml` |
| `dashboard/packages/airaluce_dashboard.yaml` | `packages/airaluce_dashboard.yaml` |
| `dashboard/www/airaluce-zone-control.js` | `www/airaluce-zone-control.js` |

Lege die Ordner `packages` und `www` an, falls sie noch nicht existieren.

### Packages-Eintrag prüfen

Home Assistant lädt das Dashboard-Package nur, wenn `configuration.yaml` Packages einbindet. Prüfe, ob bereits ein entsprechender Eintrag vorhanden ist:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

Lege keinen zweiten `homeassistant:`-Block an. Wenn es bereits einen solchen Block gibt, ergänze nur die eingerückte `packages`-Zeile darin. Beispiel:

```yaml
homeassistant:
  name: Home Assistant
  packages: !include_dir_named packages
```

Die Datei `dashboard/configuration.yaml` ist eine Vorlage und soll nicht unverändert über eine bestehende Home-Assistant-Konfiguration kopiert werden.

Prüfe die Home-Assistant-Konfiguration mit der in deiner Installation verfügbaren Konfigurationsprüfung und starte Home Assistant danach neu. Das Package registriert das Dashboard unter **AVITANA aira luce** in der Seitenleiste.

## Einschränkungen und Netzwerk

- Die Home-Assistant-Integration kommuniziert lokal per HTTP mit dem Gerät; der Standard-Port ist `80`. Es ist keine Cloud-Verbindung erforderlich.
- Die Integration setzt voraus, dass Home Assistant das Gerät im Netzwerk erreichen kann. Im reinen Setup-AP-Betrieb ist das Gerät nicht automatisch Teil des Heimnetzwerks und daher normalerweise nicht von Home Assistant erreichbar.
- Ein bereits konfiguriertes Gerät mit ausgefallenem Heim-WLAN startet den Setup-AP nicht in jeder Konfiguration automatisch. Wenn der AP deaktiviert ist, muss er laut Firmware durch etwa fünf Sekunden langes Betätigen von Taste 3 geöffnet werden.
- Die Geräte-IP wird per DHCP vergeben. Bei einer geänderten Adresse müssen Integration und gegebenenfalls Dashboard-Verweise aktualisiert werden; eine Router-DHCP-Reservierung kann das vermeiden.
- Das Gerät verwendet HTTP ohne TLS. Verwende es nur in einem vertrauenswürdigen lokalen Netzwerk und leite den Geräteport nicht direkt aus dem Internet weiter.
- Das optionale Dashboard ist nicht Voraussetzung für die Integration und kann je nach Gerätevariante und Entity-IDs Anpassungen benötigen.

## Fehlerbehebung

### Gerät wird nicht automatisch gefunden

- Prüfe, ob Gerät und Home Assistant mit dem Heimnetzwerk verbunden sind und sich gegenseitig erreichen können.
- Prüfe im Router die aktuelle IP-Adresse des Geräts.
- Öffne `http://<GERÄTE-IP>/api/info` im Browser. Wenn keine Antwort kommt, zuerst WLAN, IP-Adresse und Netzwerk-/Firewall-Einstellungen prüfen.
- Wenn die API erreichbar ist, füge die Integration manuell mit IP-Adresse und Port `80` hinzu. mDNS/Zeroconf kann durch VLANs, Gastnetzwerke oder Client-Isolation blockiert sein.

### Integration ist eingerichtet, aber das Gerät wird nicht aktualisiert

- Prüfe, ob sich die Geräte-IP geändert hat.
- Prüfe, ob Home Assistant und Gerät weiterhin im selben erreichbaren lokalen Netzwerk liegen.
- Prüfe das Home-Assistant-Protokoll auf Meldungen zu `airaluce` und lade die Integration nach einer Netzwerkänderung neu.

### Web Access Point oder lokale Oberfläche ist nicht erreichbar

- Verwende für den lokalen Zugriff `http://`, nicht `https://`. Beispiele sind `http://192.168.4.1`, `http://192.168.5.1` und `http://<AP-IP>/control-mode/setup`.
- Suche nach der tatsächlich ausgestrahlten Setup-SSID. Bei belegtem Standardnetz kann die Firmware einen nummerierten Setup-Namen und eine andere IP verwenden.
- Verwende das Setup-Passwort `AiraLuce123` und die zum Setup-Netz gehörende IP-Adresse.
- Bei einem bereits eingerichteten Gerät kann der AP deaktiviert sein. Öffne ihn in diesem Fall über Taste 3 für etwa fünf Sekunden.
- Bleibe beim lokalen Betrieb mit dem Setup-WLAN verbunden, auch wenn das Smartphone meldet, dass kein Internet verfügbar ist.

### Dashboard fehlt oder zeigt Fehler

- Prüfe, dass `airaluce_dashboard.yaml` im eingebundenen `packages`-Ordner liegt und `configuration.yaml` den Packages-Eintrag enthält.
- Prüfe, dass `airaluce-zone-control.js` im Ordner `www` liegt und die referenzierten Entities in Home Assistant vorhanden sind.
- Wenn du `airaluce-zone-control.js` aktualisierst, erhöhe auch den Versionswert hinter `?v=` in `packages/airaluce_dashboard.yaml`. Dadurch lädt der Browser die neue JavaScript-Datei statt einer zwischengespeicherten Version.
- Prüfe die Home-Assistant-Konfiguration und starte Home Assistant nach Änderungen neu. Lade anschließend den Browser vollständig neu.

## Support und Lizenz

Fehlerberichte und Verbesserungsvorschläge bitte über [GitHub Issues](https://github.com/Nordelektronik-GmbH/airaluce_Marketplace_test/issues) melden. Füge bei Fehlerberichten nach Möglichkeit Home-Assistant-Version, Integrationsversion und relevante Protokollmeldungen bei. Veröffentliche keine WLAN-Passwörter, Tokens oder sonstigen Zugangsdaten.

Die Lizenzbedingungen stehen in [LICENSE](LICENSE).