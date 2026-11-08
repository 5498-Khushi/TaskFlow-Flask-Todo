
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "taskflow-secret-key"

DATABASE = "database.db"


# Database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create database table
def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


# Home page - Read tasks
@app.route('/')
def index():
    conn = get_db_connection()
    tasks = conn.execute(
        "SELECT * FROM tasks ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template('index.html', tasks=tasks)


# Add task - Create
@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()

    if not title:
        flash("Task title cannot be empty!", "danger")
        return redirect(url_for('index'))

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO tasks (title, description) VALUES (?, ?)",
        (title, description)
    )
    conn.commit()
    conn.close()

    flash("Task added successfully!", "success")
    return redirect(url_for('index'))


# Edit task - Update
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    conn = get_db_connection()

    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?", (id,)
    ).fetchone()

    if task is None:
        conn.close()
        flash("Task not found!", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()

        if not title:
            conn.close()
            flash("Task title cannot be empty!", "danger")
            return redirect(url_for('edit_task', id=id))

        conn.execute(
            "UPDATE tasks SET title = ?, description = ? WHERE id = ?",
            (title, description, id)
        )
        conn.commit()
        conn.close()

        flash("Task updated successfully!", "success")
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit.html', task=task)


# Mark task as completed or pending
@app.route('/toggle/<int:id>', methods=['POST'])
def toggle_task(id):
    conn = get_db_connection()

    conn.execute("""
        UPDATE tasks
        SET completed = CASE WHEN completed = 0 THEN 1 ELSE 0 END
        WHERE id = ?
    """, (id,))

    conn.commit()
    conn.close()

    return redirect(url_for('index'))


# Delete task - Delete
@app.route('/delete/<int:id>', methods=['POST'])
def delete_task(id):
    conn = get_db_connection()

    conn.execute("DELETE FROM tasks WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    flash("Task deleted successfully!", "success")
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
