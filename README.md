# Snake + Highscore Server

Et snake spill i terminalen som lagrer highscores i en database.

## Struktur

```
snake_project/
├── requirements.txt
├── snake_game/
│   └── snake.py          # Spillet
└── highscore_server/
    ├── server.py         # Flask highscore API
    └── highscores.db     # Lages automatisk når server kjøres første gang 
```

### 1. Start highscore server
med aktivert venv:
```bash
python server.py
```

Serveren starter på http://localhost:5000

### 2. Start spill
med aktivert venv:
```bash
python snake.py
```

###
TO TERMINALVINDUER
Begge skal åpne mappen med repo

Ene vindu: 
python highscore_server/server.py (ikke spill vindu)
python3 snake_game/snake.py (Spill vindu)




## Input

| Key | Action |
|-----|--------|
| W / ↑ | Opp |
| S / ↓ | Ned |
| A / ← | Venstre |
| D / → | Høyre |
| Q | Avslutt spill |

## API Endepunkter

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /highscores | Hent topp 10 poengsummer |
| POST | /highscores | Legg inn ny highscore |
| GET | /highscores/<name> | Hent poeng for spesefikk spiller |
| DELETE | /highscores/<id> | Slett en poengsum |
| GET | /stats | Statistikk |
