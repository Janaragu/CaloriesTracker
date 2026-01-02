# 🚀 CalorieSnap Reflex - Modular Version

## 📁 Projekt-Struktur (Modular & Organisiert!)

```
caloriesnap-reflex-modular/
├── caloriesnap/              # Main app package
│   ├── __init__.py
│   ├── caloriesnap.py       # Main app file
│   │
│   ├── states/              # State Management
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication (Login/Signup/Logout)
│   │   ├── profile.py       # User Profile & Fitness Calculations
│   │   └── meals.py         # Meals & AI Food Analysis
│   │
│   ├── components/          # Reusable UI Components
│   │   ├── __init__.py
│   │   ├── navbar.py        # Navigation Bar
│   │   └── cards.py         # Card Components (stat, meal, feature, info)
│   │
│   └── pages/               # Page Components
│       ├── __init__.py
│       ├── landing.py       # Landing Page
│       ├── auth.py          # Login & Signup Pages
│       └── dashboard.py     # Dashboard (Overview, Add Meal, Settings)
│
├── requirements.txt          # Dependencies
├── rxconfig.py              # Reflex Configuration
└── README.md                # This file
```

---

## ✨ Modular Struktur Vorteile

### **Vorher (Eine Datei):**
```python
caloriesnap.py  # 700+ Zeilen - unübersichtlich!
```

### **Nachher (Modular):**
```python
states/
  auth.py        # 100 Zeilen - nur Authentication
  profile.py     # 100 Zeilen - nur Profile
  meals.py       # 150 Zeilen - nur Meals

components/
  navbar.py      # 50 Zeilen
  cards.py       # 100 Zeilen

pages/
  landing.py     # 100 Zeilen
  auth.py        # 100 Zeilen
  dashboard.py   # 200 Zeilen
```

**Viel übersichtlicher!** ✅

---

## 🎯 Was jede Datei macht

### **States (Daten & Logik)**

#### `states/auth.py`
```python
- is_logged_in      # Ist User eingeloggt?
- user_id          # User ID
- signup()         # Neuen Account erstellen
- login()          # Einloggen
- logout()         # Ausloggen
```

#### `states/profile.py`
```python
- weight_kg, height_cm, age  # Körperdaten
- activity_level, goal       # Fitness-Daten
- load_profile()            # Profil laden
- update_profile()          # Profil speichern
- calculate_bmr()           # BMR berechnen
- calculate_tdee()          # TDEE berechnen
```

#### `states/meals.py`
```python
- meals, today_meals        # Mahlzeiten-Liste
- analyzed_food            # AI-Analyse Ergebnis
- load_meals()             # Mahlzeiten laden
- analyze_food()           # Foto mit AI analysieren
- save_meal()              # Mahlzeit speichern
- delete_meal()            # Mahlzeit löschen
- today_calories           # Kalorien heute (computed)
```

### **Components (UI Bausteine)**

#### `components/navbar.py`
```python
navbar() → Navigation Bar mit Logo & Login/Logout
```

#### `components/cards.py`
```python
stat_card()     → Statistik-Karte (Kalorien, Protein, etc.)
meal_card()     → Mahlzeiten-Karte mit Delete-Button
feature_card()  → Feature-Karte für Landing Page
info_card()     → Info-Karte für Dashboard
```

### **Pages (Seiten)**

#### `pages/landing.py`
```python
landing_page() → Hero + Features + CTA
```

#### `pages/auth.py`
```python
login_page()   → Login-Formular
signup_page()  → Signup-Formular
```

#### `pages/dashboard.py`
```python
dashboard_page()  → Dashboard mit 3 Tabs:
  - overview_tab()   → Fortschritt + Mahlzeiten
  - add_meal_tab()   → Foto hochladen + AI
  - settings_tab()   → Profil bearbeiten
```

---

## 🚀 Installation & Start

### 1. Setup
```bash
cd caloriesnap-reflex-modular

# Virtual Environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# Dependencies
pip install -r requirements.txt

# Reflex initialisieren
reflex init
```

### 2. App starten
```bash
reflex run
```

**App läuft auf:** http://localhost:3000

---

## 🔧 Wie man Code bearbeitet

### Neue State hinzufügen
```python
# Neue Datei: states/analytics.py
import reflex as rx

class AnalyticsState(rx.State):
    weekly_data: list = []
    
    def load_weekly_stats(self):
        # Load from Supabase
        ...
```

### Neuen Component erstellen
```python
# In components/cards.py
def progress_card(percentage: int) -> rx.Component:
    return rx.card(
        rx.circular_progress(value=percentage)
    )
```

### Neue Page hinzufügen
```python
# Neue Datei: pages/analytics.py
import reflex as rx

def analytics_page() -> rx.Component:
    return rx.container(
        rx.heading("Analytics")
    )

# In app.py registrieren:
app.add_page(analytics_page, route="/analytics")
```

---

## 📦 Import-Structure

### States importieren
```python
from caloriesnap.states.auth import AuthState
from caloriesnap.states.profile import ProfileState
from caloriesnap.states.meals import MealState
```

### Components importieren
```python
from caloriesnap.components.navbar import navbar
from caloriesnap.components.cards import stat_card, meal_card
```

### Pages importieren
```python
from caloriesnap.pages.landing import landing_page
from caloriesnap.pages.dashboard import dashboard_page
```

---

## 🎨 Design System

### Farben
```python
# Primary: Green
color_scheme="green"     # Emerald/Teal

# Secondary Colors:
"blue"    # für Protein
"purple"  # für Carbs
"orange"  # für Fat
"red"     # für Delete/Logout
```

### Spacing
```python
spacing="2"  # Klein (8px)
spacing="4"  # Medium (16px)
spacing="6"  # Groß (24px)
spacing="8"  # Sehr groß (32px)
```

### Sizes
```python
size="2"  # Text: Klein
size="3"  # Input/Button: Normal
size="4"  # Button: Groß
size="5"  # Heading: Klein
size="7"  # Heading: Mittel
size="8"  # Heading: Groß
```

---

## 🔄 State Management Flow

### Beispiel: Meal hinzufügen

```
1. User uploadt Foto
   ↓
2. MealState.analyze_food() wird aufgerufen
   ↓
3. Claude API wird angerufen
   ↓
4. analyzed_food wird gesetzt
   ↓
5. UI zeigt Ergebnis (rx.cond)
   ↓
6. User klickt "Save"
   ↓
7. MealState.save_meal() wird aufgerufen
   ↓
8. Supabase speichert Meal
   ↓
9. MealState.load_meals() lädt neu
   ↓
10. UI updated automatisch
```

### State Updates sind reaktiv!
```python
class State(rx.State):
    count: int = 0
    
    def increment(self):
        self.count += 1  # UI updated automatisch!
```

---

## 🐛 Debugging

### State ausgeben
```python
# In einer Page/Component:
rx.text(f"Debug: {MealState.today_calories}")
```

### Console Logs
```python
# In State-Methode:
def save_meal(self):
    print(f"Saving meal: {self.analyzed_food}")
    ...
```

### Reflex Dev Tools
```bash
# In separatem Terminal:
reflex db init  # Database checken
```

---

## 📊 Database (Supabase)

### Tables
```sql
users:
- user_id, email, full_name
- weight_kg, height_cm, age, gender
- activity_level, goal
- daily_calorie_goal

meals:
- id, user_id
- food_name, calories, protein, carbs, fat
- portion_size, confidence
- created_at
```

### Config
```python
# In states/auth.py:
SUPABASE_URL = "https://..."
SUPABASE_KEY = "eyJ..."
```

---

## 🚀 Deployment

### Reflex Cloud
```bash
reflex deploy
```

### Render.com
```bash
Build Command:
pip install -r requirements.txt && reflex init

Start Command:
reflex run --env prod --backend-only
```

---

## ✅ Features Checklist

- [x] Landing Page mit Hero & Features
- [x] Login/Signup mit Supabase
- [x] Dashboard mit 3 Tabs
- [x] AI Food Recognition (Claude Vision)
- [x] Meal Tracking (CRUD)
- [x] Profile Management
- [x] BMR/TDEE Calculation
- [x] Responsive Design
- [x] Modular Code Structure
- [x] Error Handling
- [x] Loading States

---

## 💡 Best Practices

### 1. Ein State pro Feature
```python
✅ states/auth.py, states/profile.py, states/meals.py
❌ state.py (alles in einer Datei)
```

### 2. Kleine, wiederverwendbare Components
```python
✅ stat_card(), meal_card(), feature_card()
❌ Ein großer Component für alles
```

### 3. Klare Datei-Namen
```python
✅ pages/dashboard.py, components/navbar.py
❌ page1.py, comp.py
```

### 4. Docstrings verwenden
```python
def load_meals(self):
    """Load user's meals from database"""
    ...
```

---

## 🎓 Lern-Ressourcen

### Reflex Docs
- https://reflex.dev/docs/getting-started/introduction/
- https://reflex.dev/docs/library/
- https://reflex.dev/docs/state/overview/

### Supabase Docs
- https://supabase.com/docs/guides/getting-started/quickstarts/python

### Anthropic Docs
- https://docs.anthropic.com/claude/docs/vision

---

## 🆘 Häufige Fehler

### "Module not found"
```bash
# Lösung:
pip install -r requirements.txt --force-reinstall
```

### "State not updating"
```bash
# Lösung: Vergiss nicht yield!
async def analyze_food(self):
    self.analyzing = True
    yield  # WICHTIG!
    ...
```

### "Import Error"
```bash
# Lösung: __init__.py Files vorhanden?
touch caloriesnap/__init__.py
touch caloriesnap/states/__init__.py
```

---

## 📝 TODO / Erweiterungen

### Geplante Features:
- [ ] Analytics Page mit Charts
- [ ] Weekly/Monthly Reports
- [ ] Export zu PDF
- [ ] Barcode Scanner
- [ ] Recipe Database
- [ ] Social Features
- [ ] Dark Mode
- [ ] Multi-Language

### Code Improvements:
- [ ] Unit Tests hinzufügen
- [ ] Error Logging
- [ ] Performance Optimization
- [ ] Cache implementieren

---

## 🎉 Fertig!

**Du hast jetzt eine komplett modulare Reflex-App!**

Jede Datei hat ihre klare Aufgabe:
- **States** = Daten & Logik
- **Components** = UI Bausteine
- **Pages** = Komplette Seiten

**Viel einfacher zu warten und erweitern!** 💪

Start mit:
```bash
reflex run
```

**Viel Erfolg! 🚀**
