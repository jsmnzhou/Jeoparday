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
    pw, ph = int(rw * 0.8), int(rh * 0.8)
    x = rx + (rw - pw) // 2
    y = ry + (rh - ph) // 2
    window.geometry(f"{pw}x{ph}+{x}+{y}")

    content_frame = tk.Frame(window)
    content_frame.pack(expand=True, fill="both", padx=20, pady=20)

    img_label = None
    question_label = None

    # Example image question
    if category in ["video game\n screenshots", "country flags", "guess the character"]:
        img_path = resource_path(questions_data[category][value]["question"])
        img = Image.open(img_path)

        max_width = int(pw * 0.8)
        max_height = int(ph * 0.6)
        orig_width, orig_height = img.size
        scale = min(max_width / orig_width, max_height / orig_height)
        new_width = int(orig_width * scale)
        new_height = int(orig_height * scale)

        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)

        img_label = tk.Label(content_frame, image=photo)
        img_label.image = photo  # keep reference
        img_label.pack(pady=10)

    elif category in ["anime openings", "movie/video games\n soundtracks"]:
        full_audio_path = resource_path(questions_data[category][value]["question"])

        def play_audio_threaded():
            def play_audio():
                pygame.mixer.music.load(full_audio_path)
                pygame.mixer.music.play()
            threading.Thread(target=play_audio, daemon=True).start()

        audio_button = tk.Button(window, text="Play Audio", font=("Arial", 14), command=play_audio_threaded)
        audio_button.pack(pady=10)

    else:
        if "file" in questions_data[category][value]:
            img_path = resource_path(questions_data[category][value]["file"])
            img = Image.open(img_path)

            max_width = int(pw * 0.7)
            max_height = int(ph * 0.5)
            orig_width, orig_height = img.size
            scale = min(max_width / orig_width, max_height / orig_height)
            new_width = int(orig_width * scale)
            new_height = int(orig_height * scale)

            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            img_label = tk.Label(content_frame, image=photo)
            img_label.image = photo  # keep reference
            img_label.pack(pady=10)

            question_label = tk.Label(content_frame, 
                          text=questions_data[category][value]["question"], 
                          font=("Arial", 35), 
                          wraplength=pw * 0.9,  # Wrap at 90% of popup width
                          justify="center")
            question_label.pack(pady=30)
        else:

            question_label = tk.Label(content_frame, 
                            text=questions_data[category][value]["question"], 
                            font=("Arial", 50), 
                            wraplength=pw * 0.9,  # Wrap at 90% of popup width
                            justify="center")
            question_label.pack(pady=30)

    answer_label = tk.Label(content_frame, 
                        text="", 
                        font=("Arial", 40), 
                        fg="green", 
                        wraplength=pw * 0.9, 
                        justify="center")

    def reveal_answer():
        # Set answer text (you can replace this with your real answer logic)
        answer_label.config(text=questions_data[category][value]["answer"])
        answer_label.pack(pady=10)
        reveal_button.config(text="Close", command=window.destroy)

    reveal_button = tk.Button(window, text="Reveal Answer", font=("Arial", 14), command=reveal_answer)
    reveal_button.pack(pady=10)

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
    root.geometry("1200x800")

    main_frame = tk.Frame(root, padx=20, pady=20, bg="black")
    main_frame.pack(fill="both", expand=True)

    board_frame = tk.Frame(main_frame, bg="black")
    board_frame.pack(fill="both", expand=True)

    categories = get_categories(board_num)
    values = ["200", "400", "600", "800", "1000"]

    for col, cat in enumerate(categories):
        tk.Label(board_frame, text=cat.upper(), font=("Impact", 18), bg="navy", fg="white").grid(row=0, column=col, sticky="nsew", padx=2, pady=2)
        for row, val in enumerate(values):
            btn = tk.Button(board_frame, text=("$ " + str(val)), font=("Helvetica", 40, "bold"))
            btn.grid(row=row+1, column=col, sticky="nsew", padx=2, pady=2)

            btn.config(command=lambda b=btn, c=cat, v=val: on_card_click(b, c, v, questions_data))

    for i in range(len(categories)):
        board_frame.grid_columnconfigure(i, weight=1, uniform="category")
    for i in range(len(values) + 1):
        board_frame.grid_rowconfigure(i, weight=1)

    score_frame = tk.Frame(main_frame, bg="gray20", pady=10)
    score_frame.pack(fill="x")

    team_scores = []
    for i in range(num_teams):
        frame = tk.Frame(score_frame, bg="gray30", padx=10, pady=5)
        frame.pack(side="left", expand=True, fill="both", padx=5)
        tk.Label(frame, text=f"Team {i+1}", font=("Arial", 14, "bold"), bg="gray30", fg="white").pack()
        var = tk.StringVar(value="0")
        team_scores.append(var)
        tk.Label(frame, textvariable=var, font=("Arial", 16), bg="gray30", fg="yellow").pack()
        btn_frame = tk.Frame(frame, bg="gray30")
        btn_frame.pack()
        tk.Button(btn_frame, text="-200", command=lambda idx=i: update_score(idx, -200)).pack(side="left", padx=2)
        tk.Button(btn_frame, text="+200", command=lambda idx=i: update_score(idx, 200)).pack(side="left", padx=2)
        
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


