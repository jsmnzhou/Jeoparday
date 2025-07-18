import tkinter as tk
from tkinter import messagebox
import sys
import os
from PIL import Image, ImageTk
import json
import pygame
import threading

# Load questions at startup
def load_questions(board_num):
    path = resource_path("assets/" + str(board_num) + "/questions.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

questions_data = {}

def get_categories(board_num):
    match board_num:
        case 1:
            return ["anime", "video games", "music", "video game\n screenshots", "country flags"]
        case 2:
            return ["movies", "memes", "anime openings", "quotes", "comics"]
        case 3:
            return ["movie/video games\n soundtracks", "board games", "miscellaneous", "content creators", "guess the character"]


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

logo_path = resource_path("assets/images/logo.png")

def open_question(questions_data, category, value):
    window = tk.Toplevel(root)
    window.title(f"{category} - {value}")

    root.update_idletasks()
    rw, rh = root.winfo_width(), root.winfo_height()
    rx, ry = root.winfo_x(), root.winfo_y()
    pw, ph = int(rw * 0.8), int(rh * 0.85)  # Slightly taller
    x = rx + (rw - pw) // 2
    y = ry + (rh - ph) // 2
    window.geometry(f"{pw}x{ph}+{x}+{y}")
    window.configure(bg="#283593")

    # Header
    header = tk.Label(
        window,
        text=f"{category.upper()} - ${value}",
        font=("Impact", 36, "bold"),
        bg="#283593",
        fg="#ffd600",
        pady=10
    )
    header.pack(fill="x")

    content_frame = tk.Frame(window, bg="#283593")
    content_frame.pack(expand=True, fill="both", padx=30, pady=30)

    img_label = None
    question_label = None

    # Image question
    if category in ["video game\n screenshots", "country flags", "guess the character"]:
        img_path = resource_path(questions_data[category][value]["question"])
        img = Image.open(img_path)

        max_width = int(pw * 0.8)
        max_height = int(ph * 0.5)
        orig_width, orig_height = img.size
        scale = min(max_width / orig_width, max_height / orig_height)
        new_width = int(orig_width * scale)
        new_height = int(orig_height * scale)

        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)

        img_label = tk.Label(content_frame, image=photo, bg="#283593")
        img_label.image = photo  # keep reference
        img_label.pack(pady=10)

        # Do NOT show filename or question text for image questions

    elif category in ["anime openings", "movie/video games\n soundtracks"]:
        full_audio_path = resource_path(questions_data[category][value]["question"])

        def play_audio_threaded():
            def play_audio():
                pygame.mixer.music.load(full_audio_path)
                pygame.mixer.music.play()
            threading.Thread(target=play_audio, daemon=True).start()

        audio_button = tk.Button(
            content_frame,
            text="▶ Play Audio",
            font=("Arial Rounded MT Bold", 18, "bold"),
            bg="#ffd600",
            fg="#283593",
            activebackground="#fffde7",
            activeforeground="#283593",
            bd=0,
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2",
            command=play_audio_threaded
        )
        audio_button.pack(pady=20)

    else:
        if "file" in questions_data[category][value]:
            img_path = resource_path(questions_data[category][value]["file"])
            img = Image.open(img_path)

            max_width = int(pw * 0.7)
            max_height = int(ph * 0.4)
            orig_width, orig_height = img.size
            scale = min(max_width / orig_width, max_height / orig_height)
            new_width = int(orig_width * scale)
            new_height = int(orig_height * scale)

            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            img_label = tk.Label(content_frame, image=photo, bg="#283593")
            img_label.image = photo  # keep reference
            img_label.pack(pady=10)

        # Question text
        question_label = tk.Label(
            content_frame,
            text=questions_data[category][value]["question"],
            font=("Arial Rounded MT Bold", 32),
            bg="#283593",
            fg="#fffde7",
            wraplength=pw * 0.9,
            justify="center"
        )
        question_label.pack(pady=30)
    if not question_label and "question" in questions_data[category][value]:
        # For image/audio only questions, show a smaller label if needed
        if category not in ["anime openings", "movie/video games\n soundtracks", "video game\n screenshots", "country flags", "guess the character"]:
            question_label = tk.Label(
                content_frame,
                text=questions_data[category][value]["question"],
                font=("Arial Rounded MT Bold", 32),
                bg="#283593",
                fg="#fffde7",
                wraplength=pw * 0.9,
                justify="center"
            )
            question_label.pack(pady=30)

    answer_label = tk.Label(
        content_frame,
        text="",
        font=("Arial Rounded MT Bold", 32),
        fg="#ffd600",
        bg="#283593",
        wraplength=pw * 0.9,
        justify="center"
    )

    def reveal_answer():
        answer_label.config(text=questions_data[category][value]["answer"])
        answer_label.pack(pady=20, after=question_label if question_label else img_label)
        reveal_button.config(text="Close", command=window.destroy)

    reveal_button = tk.Button(
        content_frame,
        text="Reveal Answer",
        font=("Arial Rounded MT Bold", 20, "bold"),
        bg="#ffd600",
        fg="#283593",
        activebackground="#fffde7",
        activeforeground="#283593",
        bd=0,
        relief="flat",
        padx=20,
        pady=8,
        cursor="hand2",
        command=reveal_answer
    )
    reveal_button.pack(pady=20)

    window.grab_set()

def update_score(team_idx, delta):
    current = int(team_scores[team_idx].get())
    team_scores[team_idx].set(str(current + delta))

def on_card_click(button, category, value, questions_data):
    button.config(text="")  # Clear the price text
    open_question(questions_data, category, value)


def start_game():
    global num_teams, board_num, root, team_scores
    num_teams = int(team_var.get())
    board_num = int(board_var.get())
    popup.destroy()
    pygame.mixer.init()

    questions_data = load_questions(board_num)

    # Now launch the board
    root = tk.Tk()
    root.title(f"Jeopardy Board {board_num}")
    root.geometry("1300x900")
    root.configure(bg="#1a237e")  # Deep blue background

    # Solid background using a canvas (no gradient, no white line)
    bg_canvas = tk.Canvas(root, width=1300, height=900, highlightthickness=0, bg="#1a237e", bd=0)
    bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

    # Jeopardy Title Banner
    title_frame = tk.Frame(root, bg="#283593")
    title_frame.pack(fill="x", pady=(0, 10))
    tk.Label(
        title_frame,
        text="JEOPARDY!",
        font=("Impact", 60, "bold"),
        fg="#ffd600",  # Jeopardy yellow
        bg="#283593",
        pady=20
    ).pack()

    main_frame = tk.Frame(root, padx=20, pady=20, bg="#1a237e")
    main_frame.pack(fill="both", expand=True)

    board_frame = tk.Frame(main_frame, bg="#1a237e", bd=8, relief="ridge", highlightbackground="#ffd600", highlightcolor="#ffd600", highlightthickness=4)
    board_frame.pack(fill="both", expand=True, pady=(0, 20))

    categories = get_categories(board_num)
    values = ["200", "400", "600", "800", "1000"]

    # Category headers
    for col, cat in enumerate(categories):
        tk.Label(
            board_frame,
            text=cat.upper(),
            font=("Impact", 22, "bold"),
            bg="#283593",
            fg="#ffd600",
            bd=2,
            relief="ridge",
            padx=10,
            pady=10
        ).grid(row=0, column=col, sticky="nsew", padx=4, pady=4)
        for row, val in enumerate(values):
            btn = tk.Button(
                board_frame,
                text=("$" + str(val)),
                font=("Arial Rounded MT Bold", 36, "bold"),
                bg="#1a237e",
                fg="#ffd600",
                activebackground="#3949ab",
                activeforeground="#fffde7",
                bd=3,
                relief="raised",
                cursor="hand2",
                highlightthickness=0
            )
            btn.grid(row=row+1, column=col, sticky="nsew", padx=4, pady=4)
            btn.config(command=lambda b=btn, c=cat, v=val: on_card_click(b, c, v, questions_data))

            # Add hover effect
            def on_enter(e, b=btn):
                b.config(bg="#3949ab")
            def on_leave(e, b=btn):
                b.config(bg="#1a237e")
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

    for i in range(len(categories)):
        board_frame.grid_columnconfigure(i, weight=1, uniform="category")
    for i in range(len(values) + 1):
        board_frame.grid_rowconfigure(i, weight=1)

    # Scoreboard
    score_frame = tk.Frame(main_frame, bg="#283593", pady=10, bd=4, relief="ridge", highlightbackground="#ffd600", highlightcolor="#ffd600", highlightthickness=2)
    score_frame.pack(fill="x", pady=(10, 0))

    team_scores = []
    for i in range(num_teams):
        frame = tk.Frame(score_frame, bg="#3949ab", padx=10, pady=5, bd=2, relief="groove")
        frame.pack(side="left", expand=True, fill="both", padx=10)
        tk.Label(frame, text=f"Team {i+1}", font=("Arial Rounded MT Bold", 18, "bold"), bg="#3949ab", fg="#ffd600").pack()
        var = tk.StringVar(value="0")
        team_scores.append(var)
        tk.Label(frame, textvariable=var, font=("Arial Rounded MT Bold", 22), bg="#3949ab", fg="#fffde7").pack()
        btn_frame = tk.Frame(frame, bg="#3949ab")
        btn_frame.pack()
        tk.Button(btn_frame, text="-200", font=("Arial", 12, "bold"), bg="#c62828", fg="white", command=lambda idx=i: update_score(idx, -200), width=6, relief="ridge").pack(side="left", padx=4)
        tk.Button(btn_frame, text="+200", font=("Arial", 12, "bold"), bg="#2e7d32", fg="white", command=lambda idx=i: update_score(idx, 200), width=6, relief="ridge").pack(side="left", padx=4)

    root.mainloop()

# --- STARTUP POPUP ---
popup = tk.Tk()
popup.title("Start Jeopardy")

tk.Label(popup, text="Number of Teams:", font=("Arial", 14)).pack(padx=10, pady=5)
team_var = tk.StringVar()
tk.Entry(popup, textvariable=team_var, font=("Arial", 14)).pack(padx=10, pady=5)

tk.Label(popup, text="Board Number:", font=("Arial", 14)).pack(padx=10, pady=5)
board_var = tk.StringVar()
tk.Entry(popup, textvariable=board_var, font=("Arial", 14)).pack(padx=10, pady=5)

tk.Button(popup, text="Start Game", font=("Arial", 14), command=start_game).pack(pady=10)

popup.mainloop()


