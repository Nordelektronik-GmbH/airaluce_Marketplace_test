TODO README – AVITANA aira luce Home-Assistant-Integration
Aktueller Stand
Sichtbarer Produktname
Überall für den Benutzer sichtbar:

AVITANA aira luce
Technische Bezeichnungen bleiben unverändert
DOMAIN = airaluce
custom_components/airaluce
Device Informationen
device = AVITANA aira luce
model = aira luce
manufacturer = AVITANA GmbH
README Grundstruktur
Einleitung
Voraussetzungen
Verbindung mit dem AVITANA aira luce Beleuchtungs- und Lüftungssystem herstellen
Repository im Marketplace bzw. HACS vorbereiten
Installation über Marketplace
Installation über HACS (ältere HA-Versionen)
Home Assistant neu starten
Integration hinzufügen
Dashboard installieren (optional)
configuration.yaml prüfen
Home Assistant erneut neu starten
Support
README Einleitung
Verwenden:

AVITANA aira luce
Home-Assistant-Integration

Die Home-Assistant-Integration für AVITANA aira luce ermöglicht die Einbindung kompatibler AVITANA aira luce Leuchten/Systeme in Home Assistant und stellt die verfügbaren Funktionen zur Automatisierung und Visualisierung bereit.

Beleuchtung, Lüfter und weitere Funktionen stehen damit anschließend als Home-Assistant-Entitäten zur Verfügung.

Repository
Aktuelles Testrepository:

https://github.com/Nordelektronik-GmbH/airaluce_Marketplace_test

Offene Punkte
Provisioning beschreiben
Noch vollständig zu dokumentieren:

Erstinbetriebnahme
Provisioning
WLAN / LAN Einrichtung
DHCP oder feste IP
Geräteerkennung
Geräteregistrierung
Netzwerkvoraussetzungen
Verbindung mit AVITANA aira luce
Noch zu klären:

Wie erhält das System seine IP-Adresse?
HTTP oder HTTPS?
Welcher Standard-Port?
Benutzername erforderlich?
Passwort erforderlich?
Token erforderlich?
Wie prüft der Benutzer die Erreichbarkeit?
Fehlersuche bei Verbindungsproblemen
Dashboard Dokumentation
Noch zu überarbeiten:

airaluce.yaml
packages
www
Dashboard Screenshots
Import-Anleitung
configuration.yaml
Noch zu dokumentieren:

bestehende Konfiguration prüfen
vorhandenen homeassistant:-Block erweitern
niemals zweiten homeassistant:-Block anlegen
Beispiel:

homeassistant: packages: !include_dir_named packages

Marketplace Dokumentation
Noch prüfen:

endgültiger Marketplace-Workflow
endgültiger HACS-Workflow
Screenshots ergänzen
Prüfung gegen aktuelle Home-Assistant-Version
Git Repository
Aktueller geplanter Inhalt:

LICENSE
README.md
custom_components/
dashboard/
hacs.json
tests/
Git Ignore
.pio/
.vscode/
__pycache__/
.pytest_cache/
*.pyc

*rc/
scripts/
data/

platformio.ini**artitions.csv

NAMENSPRUEFUNG*md
README_alles.md

dashboard/PR*EFABLAUF
W*chtiger Hinweis
Die READMEist derzeit ein Arbeitsenturf.

Vor der erstenöffentlichen Veröffentlichung müssninsbesondere folgende Punkte finalgeprüft werden*

Provisioning
Netzwerkkon*iguration
Installationsablauf*- Dashboard-Dokumentation
Market*lace-/*ACS-Ablauf
Screens*ots
Support-*nformationen

💡 Damit hast du einen sauberen „Parkplatz“ für den aktuellen Stand. Nach der Pause kannst du genau dort weitermachen, insbesondere beim Thema Provisioning, denn das ist momentan der wichtigste noch offene Abschnitt.