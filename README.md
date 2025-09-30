# Guess The Word - A Flask Wordle Game

Welcome to "Guess The Word"! This is a web-based word-guessing game, similar to Wordle, built with Python and the Flask web framework. It features a complete user authentication system, daily play limits, and a powerful admin dashboard for managing the game.

## ✨ Features

* **User & Admin Roles:** Separate registration and login for regular players and administrators.
* **Daily Play Limits:** Users get 3 games per day, with each game having 5 attempts to guess the word.
* **Dynamic Word Grid:** A clean, interactive grid that provides feedback on each guess (`correct`, `present`, `absent`).
* **Admin Dashboard:**
    * Add new words to the game's dictionary.
    * View all player activity and statistics.
    * Monitor daily engagement.

## 🚀 Getting Started

Follow these instructions to get the project up and running on your local machine.

### Prerequisites

Make sure you have the following installed:

* Python 3.x
* `pip` (Python package installer)
* `Flask` library (`pip install Flask`)

### Installation & Setup

1.  **Clone the repository**
    ```bash
    git clone https://github.com/Tyson1729/Word-Guess-Game.git
    cd Word-Guess-Game
    ```

2.  **Initialize the database**
    * This is a crucial one-time step that creates all the necessary database files (`.db`) and populates the word list.
    ```bash
    python db_init.py
    ```

### Running the Application

1.  **Start the Flask server**
    * Run the following command in your terminal:
    ```bash
    flask run
    ```
    *Alternatively, you can run `python app.py`.*

2.  **Open the application in your browser**
    * Once the server is running, you will see output in your terminal. Open your web browser and navigate to the address provided, which is typically:
        **http://127.0.0.1:5000**

## 🎮 How to Use

1.  **Register an Account:** You can register as either a "User" or an "Admin".
2.  **Login:** Use your credentials to log in. You will be redirected to the appropriate page based on your role.
3.  **Playing the Game (User):**
    * You will see the game board and instructions.
    * You have 3 games to play each day. For each game, you get 5 attempts to guess the word.
    * After winning or losing a game, click "Play Again" to start your next game.
4.  **Managing the Game (Admin):**
    * The admin dashboard allows you to add new words, view all words in the database, and check player statistics.

Enjoy the game!
