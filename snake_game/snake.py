#!/usr/bin/env python3

import curses
import random
import time
import requests

SERVER_URL = "http://localhost:5000"

# Game settings
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
        win.addch(y, x, "@" if i == 0 else "#")


def draw_food(win, food):
    win.addch(food[0], food[1], "*")


def draw_score(win, score):
    win.addstr(0, 2, f" Score: {score} ")


def spawn_food(win, snake):
    h, w = win.getmaxyx()
    while True:
        y = random.randint(1, h - 2)
        x = random.randint(1, w - 2)
        if (y, x) not in snake:
            return (y, x)


def get_new_direction(key, current_direction):
    directions = {
        ord("w"): (-1, 0),
        ord("s"): (1, 0),
        ord("a"): (0, -1),
        ord("d"): (0, 1),
        curses.KEY_UP: (-1, 0),
        curses.KEY_DOWN: (1, 0),
        curses.KEY_LEFT: (0, -1),
        curses.KEY_RIGHT: (0, 1),
    }

    return directions.get(key, current_direction)


def game_loop(win):
    curses.curs_set(0)
    win.nodelay(True)
    win.keypad(True)

    h, w = win.getmaxyx()

    snake = [
        (h // 2, w // 2),
        (h // 2, w // 2 - 1),
        (h // 2, w // 2 - 2),
    ]

    direction = (0, 1)
    food = spawn_food(win, snake)
    score = 0
    speed = INITIAL_SPEED
    last_move_time = time.time()

   while True:
    key = win.getch()

    if key in (ord("q"), ord("Q")):
        return score, True, "quit"


    direction = get_new_direction(key, direction)

    now = time.time()
    if now - last_move_time < speed:
        continue
    last_move_time = now

    head_y, head_x = snake[0]
    new_head = (head_y + direction[0], head_x + direction[1])

    h, w = win.getmaxyx()

    if (
        new_head[0] <= 0 or new_head[0] >= h - 1 or
        new_head[1] <= 0 or new_head[1] >= w - 1
    ):
        return score, False, "crashed into a wall"

    if new_head in snake[1:]:
        return score, False, "bit your own tail"

    snake.insert(0, new_head)

    if new_head == food:
        score += 10
        food = spawn_food(win, snake)
        if speed > 0.05:
            speed -= 0.002
    else:
        snake.pop()

    win.erase()
    draw_border(win)
    draw_snake(win, snake)
    draw_food(win, food)
    draw_score(win, score)
    win.refresh()


def show_game_over(win, score, reason):
    win.clear()
    h, w = win.getmaxyx()

    win.addstr(h // 2 - 2, (w - 9) // 2, "GAME OVER")
    win.addstr(h // 2 - 1, (w - len(reason) - 6) // 2, f"You {reason}!")
    win.addstr(h // 2, (w - 15) // 2, f"Score: {score}")
    win.addstr(h // 2 + 1, (w - 26) // 2, "Press any key to continue")

    win.refresh()
    win.nodelay(False)
    win.getch()


def ask_name(win):
    win.clear()
    h, w = win.getmaxyx()

    win.addstr(h // 2, (w - 15) // 2, "Enter name:")
    win.refresh()

    curses.echo()
    name = win.getstr(h // 2 + 1, (w - 10) // 2, 15)
    curses.noecho()

    return name.decode().strip()


def main(stdscr):
    scores = get_highscores()
    show_game_over(stdscr, 0, "start")

    while True:
        score, quit_early, reason = game_loop(stdscr)

        show_game_over(stdscr, score, reason)

        if score > 0:
            name = ask_name(stdscr)
            if name:
                submit_score(name, score)

        scores = get_highscores()

        stdscr.clear()
        h, w = stdscr.getmaxyx()
        stdscr.addstr(h // 2, (w - 18) // 2, "Play again? (y/n)")
        stdscr.refresh()

        key = stdscr.getch()
        if key not in (ord("y"), ord("Y")):
            break


if __name__ == "__main__":
    curses.wrapper(main)