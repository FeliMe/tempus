# Tempus

Eine leistungsstarke Desktop-Anwendung zur Visualisierung großer Zeitreihendatensätze. Verarbeitet Dateien mit Millionen von Zeilen flüssig durch natives Rendering – kein Browser-Engpass.

## Installation

### Schnellinstallation (Empfohlen)

Nach dem Klonen des Repositories können Sie entweder das Skript `install.sh` in Ihrem Dateimanager doppelklicken oder folgende Befehle ausführen:

```bash
# Option 1: install.sh im Dateimanager doppelklicken

# Option 2: Im Terminal ausführen
make setup
```

### Was wird installiert

Der Befehl `make setup` installiert:

1. **mise** - Ein Runtime-Manager für Entwicklungswerkzeuge
2. **uv** - Schneller Python-Paketmanager (installiert über mise)
3. **ruff** - Python-Linter und -Formatter (installiert über mise)
4. **ty** - Statischer Typprüfer (installiert über mise)
5. **Qt6-Entwicklungsbibliotheken** - Erforderlich für das PyQt6-GUI-Framework

### Alternative Installation (Ohne mise)

Falls Sie mise nicht verwenden möchten oder die mise-Installation fehlschlägt, können Sie die minimal erforderlichen Abhängigkeiten manuell installieren:

#### 1. uv installieren (Erforderlich)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Oder verwenden Sie das Makefile-Target:

```bash
make install-uv
```

#### 2. Qt6-Entwicklungsbibliotheken installieren (Erforderlich)

Qt6-Entwicklungsbibliotheken werden für PyQt6 benötigt. Installieren Sie diese mit dem Paketmanager Ihres Systems:

**Debian/Ubuntu:**

```bash
sudo apt install -y qt6-base-dev
```

**Fedora:**

```bash
sudo dnf install -y qt6-qtbase-devel
```

**Arch Linux:**

```bash
sudo pacman -S --noconfirm qt6-base
```

**openSUSE:**

```bash
sudo zypper install -y qt6-base-devel
```

Oder verwenden Sie das Makefile-Target, das Ihren Paketmanager automatisch erkennt:

```bash
make qt-dev
```

#### 3. Python-Abhängigkeiten installieren

```bash
uv sync
```

### Fehlerbehebung

- **mise-Installation schlägt fehl**: Verwenden Sie den alternativen Installationspfad oben mit `make install-uv` und `make qt-dev`
- **Qt6 wird während `uv sync` nicht gefunden**: Stellen Sie sicher, dass die Qt6-Entwicklungsbibliotheken installiert sind (`make qt-dev`)
- **Befehl nach Installation nicht gefunden**: Öffnen Sie eine neue Terminal-Shell, um den PATH neu zu laden

## Verwendung

```bash
# Option 1: run.sh im Dateimanager doppelklicken

# Option 2: Im Terminal ausführen
uv run tempus-desktop

# Oder eine Datei direkt öffnen
uv run tempus-desktop data/MessTemperatur_20251221.csv
```

### Steuerung

- **Mausrad**: X-Achse (Zeit) zoomen
- **Klicken + Ziehen**: Ansicht verschieben
- **Strg+O**: CSV-Datei öffnen
- **Strg+R**: Ansicht zurücksetzen, um alle Daten anzuzeigen
- **Strg+H**: Fadenkreuz ein-/ausschalten
- **Strg+L**: Layer-Manager-Panel ein-/ausschalten

## Technologie-Stack

- **PyQt6** - Desktop-GUI-Framework
- **pyqtgraph** - Hochleistungs-Plotting (OpenGL-beschleunigt)
- **Pandas** - Datenverarbeitung (mit PyArrow-Backend für bessere Performance)
- **pyqtdarktheme** - Modernes Dark-Theme-Styling

## Entwicklungsumgebung einrichten

### Entwicklungswerkzeuge

Die folgenden Werkzeuge werden von mise verwaltet (siehe [mise.toml](mise.toml)):

- **uv** - Paketmanager
- **ruff** - Linting und Formatierung
- **ty** - Statische Typprüfung

### Prüfungen ausführen

```bash
# Linting
ruff check .

# Typprüfung
ty check
```
