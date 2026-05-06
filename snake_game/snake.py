#!/usr/bin/env python3

import curses
import random
import time
import requests


SERVER_URL = "http://localhost:5000"

# Game settings
WIDTH = 60
HEIGHT = 40
INITIAL_SPEED = 0.15


def get_highscores():
    try:
        response = requests.get(f"{SERVER_URL}/highscores", timeout=2)
        return response.json()
    except Exception:
        return []


def submit_score(name, score):
    try:
        data = {"name": name, "score": score}
        response = requests.post(f"{SERVER_URL}/highscores", json=data, timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def draw_border(win):
    win.border()


def draw_snake(win, snake):
    for i, (y, x) in enumerate(snake):
        if i == 0:
            win.addch(y, x, "@")
        else:
            win.addch(y, x, "#")


def draw_food(win, food):
    win.addch(food[0], food[1], "*")


def draw_score(win, score):
    win.addstr(0, 2, f" Score: {score} ")


def spawn_food(snake):
    while True:
        y = random.randint(1, HEIGHT)
        x = random.randint(1, WIDTH)
        if (y, x) not in snake:
            return (y, x)


def get_new_direction(key, current_direction):
    directions = {
        ord("w"): (-1, 0),
        ord("W"): (-1, 0),
        curses.KEY_UP: (-1, 0),
        ord("s"): (1, 0),
        ord("S"): (1, 0),
        curses.KEY_DOWN: (1, 0),
        ord("a"): (0, -1),
        ord("A"): (0, -1),
        curses.KEY_LEFT: (0, -1),
        ord("d"): (0, 1),
        ord("D"): (0, 1),
        curses.KEY_RIGHT: (0, 1),
    }

    if key in directions:
        return directions[key]
    return current_direction


def show_game_over(win, score, reason):
    win.clear()
    h, w = win.getmaxyx()
    msg1 = "GAME OVER"
    msg2 = f"You {reason}!"
    msg3 = f"Your score: {score}"
    msg4 = "Press any key to continue..."
    win.addstr(h // 2 - 2, (w - len(msg1)) // 2, msg1)
    win.addstr(h // 2 - 1, (w - len(msg2)) // 2, msg2)
    win.addstr(h // 2, (w - len(msg3)) // 2, msg3)
    win.addstr(h // 2 + 1, (w - len(msg4)) // 2, msg4)
    win.refresh()
    win.nodelay(False)
    win.getch()


def show_highscores(win, scores):
    win.clear()
    h, w = win.getmaxyx()
    win.addstr(2, (w - 12) // 2, "HIGH SCORES")
    win.addstr(3, (w - 12) // 2, "-----------")

    if not scores:
        win.addstr(5, (w - 18) // 2, "No scores yet!")
    else:
        for i, entry in enumerate(scores[:10]):
            line = f"{i+1}. {entry['name']:<15} {entry['score']}"
            win.addstr(5 + i, (w - 25) // 2, line)

    win.addstr(h - 2, (w - 24) // 2, "Press any key to play...")
    win.refresh()
    win.nodelay(False)
    win.getch()


def ask_name(win):
    h, w = win.getmaxyx()
    win.clear()
    win.addstr(h // 2 - 1, (w - 20) // 2, "Enter your name:")
    win.refresh()
    curses.echo()
    name = win.getstr(h // 2, (w - 20) // 2, 15)
    curses.noecho()
    return name.decode("utf-8").strip()


def game_loop(win):
    curses.curs_set(0)
    win.nodelay(True)
    win.keypad(True)

    # Starting snake position
    snake = [(HEIGHT // 2, WIDTH // 2), (HEIGHT // 2, WIDTH // 2 - 1), (HEIGHT // 2, WIDTH // 2 - 2)]
    direction = (0, 1)
    food = spawn_food(snake)
    score = 0
    speed = INITIAL_SPEED
    last_move_time = time.time()

    while True:
        key = win.getch()

        if key == ord("q") or key == ord("Q"):
            return score, True, "quit"

        new_direction = get_new_direction(key, direction)
        direction = new_direction

        now = time.time()
        if now - last_move_time < speed:
            continue
        last_move_time = now

        head_y, head_x = snake[0]
        new_head = (head_y + direction[0], head_x + direction[1])

        # Check wall collision
        if new_head[0] < 1 or new_head[0] > HEIGHT - 1 or new_head[1] < 1 or new_head[1] > WIDTH - 1:
            return score, False, "crashed into a wall"

        # Check self collision
        if new_head in snake[1:]:
            return score, False, "bit your own tail"

        snake.insert(0, new_head)

        if new_head == food:
            score += 10
            food = spawn_food(snake)
            if speed > 0.05:
                speed -= 0.002
        else:
            snake.pop()

        # Draw everything
        draw_border(win)
        draw_snake(win, snake)
        draw_food(win, food)
        draw_score(win, score)
        win.refresh()


def main(stdscr):
    curses.initscr()

    # Show highscores before game starts
    scores = get_highscores()
    show_highscores(stdscr, scores)

    while True:
        score, quit_early, reason = game_loop(stdscr)

        show_game_over(stdscr, score, reason)

        if score > 0:
            name = ask_name(stdscr)
            if name:
                submitted = submit_score(name, score)

        # Show updated highscores
        scores = get_highscores()
        show_highscores(stdscr, scores)

        # Ask to play again
        h, w = stdscr.getmaxyx()
        stdscr.clear()
        msg = "Play again? (y/n)"
        stdscr.addstr(h // 2, (w - len(msg)) // 2, msg)
        stdscr.nodelay(False)
        stdscr.refresh()

        key = stdscr.getch()
        if key != ord("y") and key != ord("Y"):
            break


if __name__ == "__main__":
    curses.wrapper(main)