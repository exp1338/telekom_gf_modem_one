# Telekom Glasfaser Modem 1 (ONT) Integration

Diese Home Assistant Integration ermöglicht das Auslesen des Status deines Telekom Glasfaser Modems (ONT).

## Installation

1. Kopiere den Ordner `telekom_gf_modem_one` in deinen `custom_components` Ordner innerhalb deines Home Assistant Konfigurationsverzeichnisses.
2. Starte Home Assistant neu.
3. Gehe zu **Einstellungen** -> **Geräte & Dienste**.
4. Klicke auf **Integration hinzufügen** und suche nach "Telekom Glasfaser Modem 1".
5. Gib die IP-Adresse deines Modems ein (Standard: `192.168.100.1`).

## Konfiguration

Nach der Installation kannst du das Polling-Intervall anpassen:

1. Gehe zu **Einstellungen** -> **Geräte & Dienste**.
2. Suche die Integration "Telekom Glasfaser Modem 1".
3. Klicke auf **Konfigurieren** (oder die drei Punkte -> Optionen).
4. Hier kannst du das **Polling-Intervall (in Sekunden)** festlegen.
   *   *Standardwert: 60 Sekunden.*

## Unterstützung

Diese Integration liest die Statusdaten von der Weboberfläche des ONT aus. Stelle sicher, dass dein Home Assistant das Gerät über die angegebene IP-Adresse erreichen kann.
