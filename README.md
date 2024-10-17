<div align="center">

# Trivivo

</div>

"Trivivo" is a website developed by me that aims to test you with 15 questions of varying difficulty and topics, with staggering timeouts. The aim is to score the highest among the quiz-takers!

## To-do
- [ ] make a script that would populate the database and make the game running
- [ ] revamp frontend using TailwindCSS


## Project Structure
```text
.
├── adminpanel
├── auth
├── game
├── kbc
├── static
└── templates
```

- `adminpanel` app handles administrator actions of the app, allowing administrators to perform elevated actions such as CRUD operations, changing timeout speeds, etc.
- `auth` app handles authentication of users/admins to various sites.
- `game` app handles the game logic of the app, involving timeouts, progression to the next levels, score/leaderboard handling, etc.
- `kbc` is the project folder (for Django projects).
- `static` holds the staticfiles for the project & apps.
- `templates` holds the templates for all the apps that get rendered when called via the `views.py` in each app.
