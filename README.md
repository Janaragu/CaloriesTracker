# CalorieSnap - AI-Powered Nutrition Tracking

Eine Reflex-App zur Kalorienerfassung mit AI-gestützter Bilderkennung.

## Projektstruktur

```
caloriesnap/
├── rxconfig.py              # Reflex Konfiguration
├── requirements.txt         # Python Dependencies
├── render.yaml              # Render.com Deployment Config
├── README.md
└── caloriesnap/             # App-Ordner (MUSS so heißen!)
    ├── __init__.py
    ├── caloriesnap.py       # Hauptanwendung
    ├── components/
    │   ├── __init__.py
    │   ├── navbar.py
    │   └── cards.py
    ├── pages/
    │   ├── __init__.py
    │   ├── landing.py
    │   ├── auth.py
    │   └── dashboard.py
    └── states/
        ├── __init__.py
        ├── auth.py
        ├── profile.py
        └── meals.py
```

## Lokale Entwicklung

```bash
# Repository klonen
git clone <your-repo-url>
cd caloriesnap

# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder: venv\Scripts\activate  # Windows

# Dependencies installieren
pip install -r requirements.txt

# Reflex initialisieren
reflex init

# App starten
reflex run
```

## Deployment auf Render.com

### Schritt 1: GitHub Repository erstellen

1. Gehe zu GitHub und erstelle ein neues Repository
2. Push dieses Projekt zu GitHub:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/DEIN-USERNAME/caloriesnap.git
git push -u origin main
```

### Schritt 2: Render.com Setup

1. Gehe zu [render.com](https://render.com) und logge dich ein
2. Klicke auf "New" → "Web Service"
3. Verbinde dein GitHub Repository
4. Konfiguriere den Service:

| Einstellung | Wert |
|-------------|------|
| **Name** | caloriesnap |
| **Runtime** | Python |
| **Build Command** | `pip install -r requirements.txt && reflex init && reflex export --frontend-only --no-zip` |
| **Start Command** | `reflex run --env prod --backend-host 0.0.0.0 --backend-port 10000` |

5. Füge Environment Variables hinzu:
   - `PYTHON_VERSION` = `3.11`
   - `PORT` = `10000`
   - Optional: `SUPABASE_URL` und `SUPABASE_KEY` für Produktion

6. Klicke "Create Web Service"

### Schritt 3: Warten

Das erste Deployment dauert ca. 5-10 Minuten. Danach ist deine App unter `https://caloriesnap.onrender.com` verfügbar.

## Umgebungsvariablen

| Variable | Beschreibung |
|----------|-------------|
| `SUPABASE_URL` | Supabase Projekt URL |
| `SUPABASE_KEY` | Supabase Service Role Key |
| `PYTHON_VERSION` | Python Version (3.11 empfohlen) |

## Features

- 🍔 AI-gestützte Essenerkennung (Claude Vision API)
- 📊 Kalorien- und Makro-Tracking
- 🎯 Personalisierte Kalorienziele
- 📱 Responsive Design
- 🔐 Benutzerauthentifizierung via Supabase

## Technologie-Stack

- **Frontend & Backend**: Reflex (Python)
- **Datenbank**: Supabase (PostgreSQL)
- **AI**: Anthropic Claude Vision API
- **Hosting**: Render.com
