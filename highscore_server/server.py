from flask import Flask, request, jsonify
import sqlite3
import os


app = Flask(__name__)
DB_PATH = "highscores.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


@app.route("/highscores", methods=["GET"])
def get_highscores():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, score, created_at FROM scores ORDER BY score DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "name": row["name"],
            "score": row["score"],
            "date": row["created_at"]
        })

    return jsonify(result)


@app.route("/highscores", methods=["POST"])
def add_score():
    data = request.get_json()

    name = data.get("name", "").strip()
    score = int(data.get("score", 0))

    if not name:
        return jsonify({"error": "Name is required"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO scores (name, score) VALUES (?, ?)", (name, score))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({"id": new_id, "name": name, "score": score}), 201


@app.route("/highscores/<name>", methods=["GET"])
def get_player_scores(name):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, score, created_at FROM scores WHERE name = ? ORDER BY score DESC", (name,))
    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "name": row["name"],
            "score": row["score"],
            "date": row["created_at"]
        })

    return jsonify(result)


@app.route("/highscores/<int:score_id>", methods=["DELETE"])
def delete_score(score_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM scores WHERE id = ?", (score_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "Score not found"}), 404

    cursor.execute("DELETE FROM scores WHERE id = ?", (score_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Score deleted"})


@app.route("/stats", methods=["GET"])
def get_stats():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM scores")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT MAX(score) as best FROM scores")
    best_row = cursor.fetchone()
    best = best_row["best"] if best_row else 0

    cursor.execute("SELECT AVG(score) as avg FROM scores")
    avg_row = cursor.fetchone()
    average = round(avg_row["avg"], 1) if avg_row["avg"] else 0

    conn.close()

    return jsonify({
        "total_games": total,
        "best_score": best,
        "average_score": average
    })


if __name__ == "__main__":
    init_db()
    print("Starting highscore server on http://localhost:5000")
    print("Press CTRL+C to stop")
    app.run(host="0.0.0.0", port=5000, debug=True)