from flask import Flask, render_template, request, redirect, url_for, flash, session, g
import sqlite3
import random
from datetime import date
from functools import wraps
import re

# App Configuration
app = Flask(__name__)
app.secret_key = "a_very_secure_and_complex_secret_key"
DATABASE_NAME = "database.db"
MAX_DAILY_GAMES = 3
MAX_ATTEMPTS_PER_GAME = 5

# Database Helper
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE_NAME)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            flash("You must be logged in to view this page.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("You do not have permission to access this page.", "error")
            return redirect(url_for('user_page'))
        return f(*args, **kwargs)
    return decorated_function

# Game Logic Helpers
def get_random_word():
    db = get_db()
    word_row = db.execute("SELECT word FROM words ORDER BY RANDOM() LIMIT 1").fetchone()
    return word_row['word'] if word_row else "FLASK"

def check_guess_logic(guess, correct_word):
    feedback = [''] * 5
    temp_correct = list(correct_word)
    
    for i, letter in enumerate(guess):
        if letter == temp_correct[i]:
            feedback[i] = 'correct'
            temp_correct[i] = None
            
    for i, letter in enumerate(guess):
        if feedback[i] == '':
            if letter in temp_correct:
                feedback[i] = 'present'
                temp_correct[temp_correct.index(letter)] = None
            else:
                feedback[i] = 'absent'
    return feedback

# Authentication Routes
@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"].strip()
        password = request.form["password"]
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE name = ? AND password = ?", (name, password)).fetchone()

        if user:
            session.clear()
            session["username"] = user["name"]
            session["role"] = user["role"]
            
            if user["role"] == "admin":
                return redirect(url_for("admin_page"))
            else:
                return redirect(url_for("user_page"))
        else:
            flash("Invalid username or password.", "error")
            
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        password = request.form["password"]
        role = request.form.get("role")

        if len(re.findall(r'[a-zA-Z]', name)) < 5:
            flash("Username must contain at least 5 alphabetic characters.", "error")
            return render_template("register.html", register_data=request.form)
        
        if len(password) < 5 or not re.search(r'[a-zA-Z]', password) or not re.search(r'\d', password) or not re.search(r'[$%*@]', password):
            flash("Password must be >= 5 chars, with a letter, number, and a symbol ($, %, *, @).", "error")
            return render_template("register.html", register_data=request.form)

        if not role or role not in ['user', 'admin']:
            flash("Please select a valid role.", "error")
            return render_template("register.html", register_data=request.form)

        try:
            db = get_db()
            db.execute("INSERT INTO users (name, password, role) VALUES (?, ?, ?)", (name, password, role))
            db.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists.", "error")
            return render_template("register.html", register_data=request.form)
            
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))
    
# New Route to Handle "Play Again"
@app.route("/play_again")
@login_required
def play_again():
    """Clears the session of a completed game to start a new one."""
    session.pop('secret_word', None)
    session.pop('guesses', None)
    session.pop('feedback', None)
    session.pop('game_over', None)
    flash("Starting your next game. Good luck!", "success")
    return redirect(url_for('user_page'))

# User Gameplay Route
@app.route("/user", methods=["GET", "POST"])
@login_required
def user_page():
    username = session["username"]
    today_str = str(date.today())
    db = get_db()
    
    user = db.execute("SELECT * FROM users WHERE name = ?", (username,)).fetchone()
    if user['last_played_date'] != today_str:
        db.execute("UPDATE users SET remaining_attempts = ?, last_played_date = ? WHERE name = ?", 
                   (MAX_DAILY_GAMES, today_str, username))
        db.commit()
        session.clear()
        session['username'] = user['name']
        session['role'] = user['role']
        user = db.execute("SELECT * FROM users WHERE name = ?", (username,)).fetchone()

    if request.method == "POST":
        if session.get('game_over'):
             flash("Please click 'Play Again' to start a new game.", "error")
             return redirect(url_for('user_page'))

        if user['remaining_attempts'] <= 0 or 'secret_word' not in session:
             flash("You cannot make a guess right now.", "error")
             return redirect(url_for('user_page'))
        
        guess = request.form.get("guess", "").upper()
        if len(guess) == 5 and guess.isalpha():
            secret_word = session['secret_word']
            
            db.execute("INSERT INTO activities (username, guessed_word, correct_word, date) VALUES (?, ?, ?, ?)",
                       (username, guess, secret_word, today_str))
            db.commit()
            
            feedback = check_guess_logic(guess, secret_word)
            session['guesses'].append(guess)
            session['feedback'].append(feedback)
            session.modified = True
            
            is_win = (guess == secret_word)
            session['is_win'] = is_win
            is_game_over = is_win or len(session['guesses']) >= MAX_ATTEMPTS_PER_GAME

            if is_game_over:
                db.execute("UPDATE users SET remaining_attempts = remaining_attempts - 1 WHERE name = ?", (username,))
                db.commit()
                session['game_over'] = True
                
                if is_win:
                    flash(f"You guessed it! The word was {secret_word}.", "success")
                else:
                    flash(f"No more attempts! The word was {secret_word}.", "error")
            
            return redirect(url_for('user_page'))
        else:
            flash("Your guess must be 5 alphabetic characters.", "error")
            return redirect(url_for('user_page'))

    # GET request logic
    user = db.execute("SELECT * FROM users WHERE name = ?", (username,)).fetchone()
    
    if user['remaining_attempts'] > 0 and 'secret_word' not in session and not session.get('game_over'):
        session['secret_word'] = get_random_word()
        session['guesses'] = []
        session['feedback'] = []
        session['is_win'] = False

    show_play_again = session.get('game_over', False) and user['remaining_attempts'] > 0
    show_guess_form = not session.get('game_over') and user['remaining_attempts'] > 0

    return render_template("user.html", 
                           username=username, 
                           guesses=session.get('guesses', []), 
                           feedback=session.get('feedback', []),
                           remaining_attempts=user['remaining_attempts'],
                           max_attempts=MAX_ATTEMPTS_PER_GAME,
                           show_play_again=show_play_again,
                           show_guess_form=show_guess_form,
                           is_win=session.get('is_win', False))

# Admin Dashboard Route
@app.route("/admin", methods=["GET", "POST"])
@login_required
@admin_required
def admin_page():
    db = get_db()
    message = None
    
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add_word":
            new_word = request.form.get("new_word", "").upper()
            if len(new_word) == 5 and new_word.isalpha():
                try:
                    db.execute("INSERT INTO words (word) VALUES (?)", (new_word,))
                    db.commit()
                    message = ("success", f"Word '{new_word}' added successfully.")
                except sqlite3.IntegrityError:
                    message = ("error", "That word already exists in the database.")
            else:
                message = ("error", "Word must be 5 alphabetic characters.")
    
    all_users = db.execute("SELECT name, role FROM users ORDER BY name").fetchall()
    total_users = len(all_users)
    total_words = db.execute("SELECT COUNT(*) FROM words").fetchone()[0]
    all_words = db.execute("SELECT word FROM words ORDER BY word").fetchall()
    recent_activity = db.execute("SELECT * FROM activities ORDER BY id DESC LIMIT 10").fetchall()
    
    return render_template("admin.html",
                           admin_name=session["username"],
                           total_users=total_users,
                           total_words=total_words,
                           all_words=all_words,
                           recent_activity=recent_activity,
                           all_users=all_users,
                           message=message)

if __name__ == "__main__":
    app.run(debug=True)