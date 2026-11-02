# Space Fractions

A local Windows desktop educational game for sixth-grade fraction practice. Built with Python 3.13 and Tkinter, using only the standard library.

## How to Run

1. Ensure Python 3.13 is installed on Windows.
2. Open a terminal in the project directory.
3. Run:
   ```
   python main.py
   ```

The game will open a window with a dark space theme. On first run, an intro animation plays; click "Skip Intro" or wait.

## Gameplay

- You will answer 10 multiple-choice fraction questions.
- Click a fraction button or press keys 1-4 to select.
- Each correct answer awards 1 point.
- After answering, the correct/incorrect feedback and explanation appear.
- Click "Next Question" or press 'n' to proceed.
- Pause with button or 'p', resume similarly.
- At the end, see your score and a feedback message.
- Scores are saved to a local database and can be viewed from the main menu.

## Admin

- From the main menu, click "Admin".
- On first use, you will be prompted to create an admin password (minimum 4 characters).
- Passwords are salted and hashed with PBKDF2-HMAC-SHA256.
- Only one admin account exists. After login, you can add custom questions.
- Custom questions are validated: prompt non-empty, exactly 4 options, answer among options, and all options/answer must be valid fractions.

## Data Storage

All data is stored in a SQLite database located in:
`%APPDATA%\SpaceFractions\space_fractions.db`

Tables:
- `questions`: stores game questions.
- `scores`: stores score history.
- `admin`: stores admin credentials (salt and hash).

No network access is used. The application is entirely local.

## Tests

Run tests from the project root:
```
python -m unittest tests.test_game
```

Tests cover game logic (Question, Game) and storage (SQLite, admin auth). They use temporary directories and do not modify the real database.

## Architecture Notes

The original architecture documentation describes a web-based microservices system with cloud deployment. This desktop application is a provisional local adaptation. It does not implement microservices, OAuth2, Kubernetes, cloud infrastructure, or production SLOs. The cloud contracts (openapi.yaml, internal.proto, etc.) are retained as reference in the source inputs but are not deployed. Security is implemented locally with salted password hashing and role separation between player and admin.

## Assumptions

- The game is for a single local user; no concurrent multi-user support.
- Admin password is set locally on first run; there is no password recovery.
- Questions can be added by admin but not edited or deleted through UI (though database directly could be modified).
