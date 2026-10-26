# Web Application Exercise

A little exercise to build a web application following an agile development process. See the [instructions](instructions.md) for more detail.

## Product vision statement

We aim to create a web app that allows teachers to keep track of their students and the grades they have given to their students.

## User stories
 
[User Story Issues](https://github.com/software-students-fall2026/web-app-exercise-raven/issues?q=is%3Aissue+state%3Aopen) 

## Steps to run software

1. Clone repository and move into the folder:
    ```
    git clone https://github.com/software-students-fall2026/web-app-exercise-raven.git
    cd web-app-exercise-raven
    ```
2. For every clone, run course setup script:
    - Mac/Linux: `python3 .automations/setup.py`
    - Windows: `python .automations/setup.py` 
3. Install dependencies: `pip install -r requirements.txt`
4. Copy example into your own `.env` file:
    - Mac/Linux/Git Bash: `cp env.example .env`
    - Windows (cmd): `copy env.example .env`

### Running the app

1. Run `python app.py` (`python3` on Mac if `python` is not aliased)
2. Open `http://localhost:5001` in browser
3. Press `Ctrl + C` in the terminal to stop running the app

## Task boards
 
- [Sprint 1](https://github.com/orgs/software-students-fall2026/projects/45) 
- [Sprint 2](https://github.com/orgs/software-students-fall2026/projects/67) 
