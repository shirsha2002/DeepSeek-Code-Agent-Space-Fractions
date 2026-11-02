import tkinter as tk
from tkinter import messagebox
import os
import random
from game_core import Game, Question
from storage import (
    init_db, get_questions, save_question, save_score, get_score_history,
    admin_create, admin_authenticate, admin_exists, get_app_data_dir
)

DEFAULT_QUESTIONS = [
    Question('q1', 'Which fraction is larger?', ['1/2', '3/4', '2/5', '5/8'], '3/4', 'Convert to decimals: 1/2=0.5, 3/4=0.75, so 3/4 is largest.'),
    Question('q2', 'Which fraction is equal to 1/2?', ['3/6', '2/5', '4/7', '5/9'], '3/6', '3/6 simplifies to 1/2.'),
    Question('q3', 'Which fraction is larger?', ['2/3', '3/5', '4/7', '5/8'], '2/3', '2/3 ≈0.666, 3/5=0.6, 4/7≈0.571, 5/8=0.625, so 2/3 is largest.'),
    Question('q4', 'Which fraction is smaller?', ['2/3', '3/5', '4/7', '1/2'], '1/2', '1/2=0.5, all others are larger.'),
    Question('q5', 'Which fraction is larger?', ['1/3', '1/4', '1/5', '1/6'], '1/3', 'Larger denominator means smaller piece, so 1/3 is largest.'),
    Question('q6', 'Which fraction is equal to 2/3?', ['4/6', '5/8', '6/9', '7/10'], '4/6', '4/6 simplifies to 2/3.'),
    Question('q7', 'Which fraction is larger?', ['3/4', '4/5', '5/6', '7/8'], '7/8', 'Each is about 0.75, 0.8, 0.833, 0.875, so 7/8 is largest.'),
    Question('q8', 'Which fraction is equal to 3/4?', ['6/8', '7/9', '8/10', '9/12'], '6/8', '6/8 simplifies to 3/4.'),
    Question('q9', 'Which fraction is larger?', ['5/8', '2/3', '3/4', '4/5'], '4/5', '4/5=0.8, 3/4=0.75, 2/3≈0.666, 5/8=0.625, so 4/5 is largest.'),
    Question('q10', 'Which fraction is equal to 1/3?', ['2/6', '2/5', '3/8', '4/9'], '2/6', '2/6 simplifies to 1/3.'),
]

class SpaceFractionsApp:
    def __init__(self, root, data_dir):
        self.root = root
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, 'space_fractions.db')
        init_db(self.db_path)
        self.admin_session = False
        self.questions = get_questions(self.db_path)
        if not self.questions:
            for q in DEFAULT_QUESTIONS:
                save_question(self.db_path, q)
            self.questions = get_questions(self.db_path)
        self.game = None
        self.intro_after = None
        self.intro_canvas = None
        self.stars = []
        self.root.title("Space Fractions")
        self.root.geometry("900x650")
        self.root.configure(bg='#0b0e1a')
        self.frame = tk.Frame(self.root, bg='#0b0e1a')
        self.frame.pack(fill='both', expand=True)
        self.show_intro()

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.root.unbind('1')
        self.root.unbind('2')
        self.root.unbind('3')
        self.root.unbind('4')
        self.root.unbind('p')
        self.root.unbind('n')

    def show_intro(self):
        self.clear_frame()
        self.intro_canvas = tk.Canvas(self.frame, bg='#0b0e1a', highlightthickness=0)
        self.intro_canvas.pack(fill='both', expand=True)
        self.intro_canvas.create_text(450, 100, text='Space Fractions', font=('Helvetica', 32, 'bold'), fill='white')
        self.intro_canvas.create_text(450, 140, text='A Math Adventure', font=('Helvetica', 18), fill='silver')
        self.stars = []
        for _ in range(50):
            x = random.randint(50, 850)
            y = random.randint(200, 500)
            star = self.intro_canvas.create_oval(x, y, x+2, y+2, fill='white', outline='')
            self.stars.append(star)
        skip_btn = tk.Button(self.frame, text='Skip Intro', command=self.skip_intro, bg='#1a2035', fg='white', relief='flat')
        skip_btn.place(x=830, y=600)
        self.intro_after = self.root.after(50, self.animate_intro)

    def animate_intro(self):
        if not hasattr(self, 'intro_canvas') or self.intro_canvas is None:
            return
        for star in self.stars:
            if random.random() < 0.1:
                self.intro_canvas.itemconfig(star, fill='#cccccc')
            else:
                self.intro_canvas.itemconfig(star, fill='white')
        self.intro_after = self.root.after(50, self.animate_intro)

    def skip_intro(self):
        if self.intro_after is not None:
            self.root.after_cancel(self.intro_after)
            self.intro_after = None
        self.intro_canvas = None
        self.show_main_menu()

    def show_main_menu(self):
        self.clear_frame()
        title = tk.Label(self.frame, text='Space Fractions', font=('Helvetica', 36, 'bold'), bg='#0b0e1a', fg='white')
        title.pack(pady=30)
        subtitle = tk.Label(self.frame, text='Learn fractions among the stars!', font=('Helvetica', 18), bg='#0b0e1a', fg='silver')
        subtitle.pack(pady=5)
        btn_style = {'bg': '#1a2035', 'fg': 'white', 'font': ('Helvetica', 16), 'relief': 'flat', 'width': 20, 'pady': 5}
        tk.Button(self.frame, text='Play Game', command=self.start_game, **btn_style).pack(pady=10)
        tk.Button(self.frame, text='How to Play', command=self.show_help, **btn_style).pack(pady=10)
        tk.Button(self.frame, text='Score History', command=self.show_scores, **btn_style).pack(pady=10)
        tk.Button(self.frame, text='Admin', command=self.show_admin_login, **btn_style).pack(pady=10)
        tk.Button(self.frame, text='Quit', command=self.root.quit, **btn_style).pack(pady=10)

    def start_game(self):
        self.game = Game(self.questions)
        self.show_gameplay()

    def show_gameplay(self):
        self.clear_frame()
        if self.game is None or self.game.state == 'game_over':
            self.show_end()
            return
        top = tk.Frame(self.frame, bg='#0b0e1a')
        top.pack(pady=10)
        self.score_label = tk.Label(top, text=f"Score: {self.game.score}", font=('Helvetica', 16), bg='#0b0e1a', fg='white')
        self.score_label.pack(side='left', padx=20)
        tk.Label(top, text=f"Question {self.game.index+1} of {len(self.game.questions)}", font=('Helvetica', 16), bg='#0b0e1a', fg='white').pack(side='left', padx=20)
        q = self.game.questions[self.game.index]
        tk.Label(self.frame, text=q.prompt, font=('Helvetica', 20), bg='#0b0e1a', fg='white').pack(pady=20)
        self.option_buttons = []
        for i, opt in enumerate(q.options):
            btn = tk.Button(self.frame, text=opt, font=('Helvetica', 16), bg='#1a2035', fg='white', relief='flat', width=15,
                            command=lambda o=opt: self.submit_answer(o))
            btn.pack(pady=5)
            self.option_buttons.append(btn)
        self.feedback_label = tk.Label(self.frame, text='', font=('Helvetica', 14), bg='#0b0e1a', fg='white')
        self.feedback_label.pack(pady=10)
        btn_frame = tk.Frame(self.frame, bg='#0b0e1a')
        btn_frame.pack(pady=20)
        self.pause_btn = tk.Button(btn_frame, text='Pause', command=self.pause_game, bg='#1a2035', fg='white', relief='flat')
        self.pause_btn.pack(side='left', padx=10)
        self.next_btn = tk.Button(btn_frame, text='Next Question', command=self.next_question, bg='#1a2035', fg='white', relief='flat')
        self.next_btn.pack(side='left', padx=10)
        self.root.bind('1', lambda e: self.submit_answer(q.options[0]) if len(q.options) > 0 else None)
        self.root.bind('2', lambda e: self.submit_answer(q.options[1]) if len(q.options) > 1 else None)
        self.root.bind('3', lambda e: self.submit_answer(q.options[2]) if len(q.options) > 2 else None)
        self.root.bind('4', lambda e: self.submit_answer(q.options[3]) if len(q.options) > 3 else None)
        self.root.bind('p', lambda e: self.pause_game())
        self.root.bind('n', lambda e: self.next_question())

    def submit_answer(self, answer):
        if self.game is None or self.game.state != 'playing':
            return
        try:
            correct = self.game.submit(answer)
            q = self.game.questions[self.game.index]
            if correct:
                self.feedback_label.config(text='Correct!', fg='green')
                self.score_label.config(text=f"Score: {self.game.score}")
            else:
                self.feedback_label.config(text=f"Incorrect. {q.explanation}", fg='red')
            for btn in self.option_buttons:
                btn.config(state='disabled')
        except ValueError as e:
            self.feedback_label.config(text=str(e), fg='orange')

    def next_question(self):
        if self.game is None:
            return
        try:
            self.game.next_question()
            if self.game.state == 'game_over':
                self.show_end()
            else:
                self.show_gameplay()
        except ValueError as e:
            self.feedback_label.config(text=str(e), fg='orange')

    def pause_game(self):
        if self.game is None:
            return
        try:
            self.game.pause()
            self.pause_btn.config(text='Resume', command=self.resume_game)
            for btn in self.option_buttons:
                btn.config(state='disabled')
            self.feedback_label.config(text='Game paused. Press Resume to continue.', fg='yellow')
        except ValueError as e:
            self.feedback_label.config(text=str(e), fg='orange')

    def resume_game(self):
        if self.game is None:
            return
        try:
            self.game.resume()
            self.pause_btn.config(text='Pause', command=self.pause_game)
            for btn in self.option_buttons:
                btn.config(state='normal')
            self.feedback_label.config(text='')
        except ValueError as e:
            self.feedback_label.config(text=str(e), fg='orange')

    def show_end(self):
        if self.game is None:
            return
        score = self.game.score
        total = len(self.game.questions)
        if score >= 9:
            message = "Outstanding! You're a fraction star!"
        elif score >= 7:
            message = "Great job! Keep practicing!"
        elif score >= 5:
            message = "Good effort! You'll improve!"
        else:
            message = "Keep exploring! Fractions get easier with practice."
        save_score(self.db_path, score, total)
        self.clear_frame()
        tk.Label(self.frame, text="Game Over", font=('Helvetica', 28), bg='#0b0e1a', fg='white').pack(pady=20)
        tk.Label(self.frame, text=f"Your Score: {score}/{total}", font=('Helvetica', 20), bg='#0b0e1a', fg='white').pack(pady=10)
        tk.Label(self.frame, text=message, font=('Helvetica', 16), bg='#0b0e1a', fg='silver').pack(pady=10)
        tk.Button(self.frame, text='Play Again', command=self.start_game, bg='#1a2035', fg='white', relief='flat', font=('Helvetica', 14)).pack(pady=10)
        tk.Button(self.frame, text='Main Menu', command=self.show_main_menu, bg='#1a2035', fg='white', relief='flat', font=('Helvetica', 14)).pack(pady=10)

    def show_help(self):
        self.clear_frame()
        tk.Label(self.frame, text="How to Play", font=('Helvetica', 24), bg='#0b0e1a', fg='white').pack(pady=20)
        help_text = (
            "You will answer 10 fraction questions.\n"
            "Choose the correct fraction by clicking a button or pressing keys 1-4.\n"
            "Each correct answer gives 1 point.\n"
            "You can pause/resume with 'p' or the button.\n"
            "After answering, click Next Question or press 'n' to continue.\n"
            "At the end, see your score and feedback."
        )
        tk.Label(self.frame, text=help_text, font=('Helvetica', 14), bg='#0b0e1a', fg='white', justify='left').pack(pady=20)
        tk.Button(self.frame, text='Back to Menu', command=self.show_main_menu, bg='#1a2035', fg='white', relief='flat', font=('Helvetica', 14)).pack(pady=10)

    def show_scores(self):
        self.clear_frame()
        tk.Label(self.frame, text="Score History", font=('Helvetica', 24), bg='#0b0e1a', fg='white').pack(pady=20)
        scores = get_score_history(self.db_path, limit=10)
        if not scores:
            tk.Label(self.frame, text="No scores yet. Play a game!", font=('Helvetica', 14), bg='#0b0e1a', fg='white').pack(pady=10)
        else:
            for i, (score, total, date) in enumerate(scores, 1):
                tk.Label(self.frame, text=f"{i}. Score: {score}/{total} on {date}", font=('Helvetica', 14), bg='#0b0e1a', fg='white').pack(pady=2)
        tk.Button(self.frame, text='Back to Menu', command=self.show_main_menu, bg='#1a2035', fg='white', relief='flat', font=('Helvetica', 14)).pack(pady=10)

    def show_admin_login(self):
        self.clear_frame()
        tk.Label(self.frame, text="Admin Login", font=('Helvetica', 24), bg='#0b0e1a', fg='white').pack(pady=20)
        if not admin_exists(self.db_path):
            tk.Label(self.frame, text="No admin account found. Create password:", font=('Helvetica', 14), bg='#0b0e1a', fg='white').pack(pady=5)
            self.password_entry = tk.Entry(self.frame, show='*', font=('Helvetica', 14), bg='#1a2035', fg='white', insertbackground='white')
            self.password_entry.pack(pady=5)
            tk.Button(self.frame, text='Create Admin', command=self.create_admin, bg='#1a2035', fg='white', relief='flat', font=('Helvetica', 14)).pack(pady=10)
        else:
            tk.Label(self.frame, text="Enter admin password:", font=('Helvetica', 14), bg='#0b0e1a', fg='white').pack(pady=5)
            self.password_entry = tk.Entry(self.frame, show='*', font=('Helvetica', 14), bg='#1a2035', fg='white', insertbackground='white')
            self.password_entry.pack(pady=5)
            tk.Button(self.frame, text='Login', command=self.login_admin, bg='#1a2035', fg='white', relief='flat', font=('Helvetica', 14)).pack(pady=10)
        tk.Button(self.frame, text='Back', command=self.show_main_menu, bg='#1a2035', fg='white', relief='flat', font=('Helvetica', 14)).pack(pady=10)

    def create_admin(self):
        password = self.password_entry.get()
        if len(password) < 4:
            messagebox.showerror('Password Too Short', 'Admin password must be at least 4 characters.')
            return
        if admin_create(self.db_path, password):
            messagebox.showinfo('Success', 'Admin account created.')
            self.show_admin_login()
        else:
            messagebox.showerror('Exists', 'Admin account already exists.')

    def login_admin(self):
        password = self.password_entry.get()
        if admin_authenticate(self.db_path, password):
            self.admin_session = True
            self.show_admin_panel()
        else:
            messagebox.showerror('Login Failed', 'Incorrect password.')

    def show_admin_panel(self):
        if not self.admin_session:
            self.show_main_menu()
            return
        self.clear_frame()
        tk.Label(self.frame, text="Admin Panel", font=('Helvetica', 24), bg='#0b0e1a', fg='white').pack(pady=20)
        tk.Label(self.frame, text="Current Questions:", font=('Helvetica', 16), bg='#0b0e1a', fg='white').pack(pady=5)
        listbox = tk.Listbox(self.frame, font=('Helvetica', 12), bg='#1a2035', fg='white', width=80, height=10)
        listbox.pack(pady=5)
        for q in self.questions:
            listbox.insert('end', f"{q.qid}: {q.prompt}")
        tk.Button(self.frame, text='Add Question', command=self.add_question, bg='#1a2035', fg='white', relief='flat', font=('Helvetica', 14)).pack(pady=5)
        tk.Button(self.frame, text='Logout', command=self.admin_logout, bg='#1a2035', fg='white', relief='flat', font=('Helvetica', 14)).pack(pady=5)
        tk.Button(self.frame, text='Back to Menu', command=self.show_main_menu, bg='#1a2035', fg='white', relief='flat', font=('Helvetica', 14)).pack(pady=5)

    def add_question(self):
        dialog = tk.Toplevel(self.root)
        dialog.title('Add Question')
        dialog.geometry('400x300')
        dialog.configure(bg='#0b0e1a')
        tk.Label(dialog, text='Prompt:', bg='#0b0e1a', fg='white').pack(pady=5)
        prompt_entry = tk.Entry(dialog, width=50, bg='#1a2035', fg='white')
        prompt_entry.pack(pady=5)
        tk.Label(dialog, text='Options (comma separated, 4 options):', bg='#0b0e1a', fg='white').pack(pady=5)
        options_entry = tk.Entry(dialog, width=50, bg='#1a2035', fg='white')
        options_entry.pack(pady=5)
        tk.Label(dialog, text='Correct answer (must be one of options):', bg='#0b0e1a', fg='white').pack(pady=5)
        answer_entry = tk.Entry(dialog, width=50, bg='#1a2035', fg='white')
        answer_entry.pack(pady=5)
        def save_new_question():
            prompt = prompt_entry.get().strip()
            options = [o.strip() for o in options_entry.get().split(',') if o.strip()]
            answer = answer_entry.get().strip()
            if not prompt or len(options) != 4 or not answer:
                messagebox.showerror('Invalid', 'Need prompt, exactly 4 options, and answer.')
                return
            if answer not in options:
                messagebox.showerror('Invalid', 'Answer must be one of options.')
                return
            from fractions import Fraction
            try:
                Fraction(answer)
                for opt in options:
                    Fraction(opt)
            except (ValueError, ZeroDivisionError):
                messagebox.showerror('Invalid', 'All options and answer must be valid fractions like 3/4.')
                return
            qid = f"custom_{len(self.questions)+1}"
            try:
                q = Question(qid, prompt, options, answer, 'Custom question')
            except ValueError as e:
                messagebox.showerror('Invalid', str(e))
                return
            save_question(self.db_path, q)
            self.questions = get_questions(self.db_path)
            dialog.destroy()
            self.show_admin_panel()
        tk.Button(dialog, text='Save', command=save_new_question, bg='#1a2035', fg='white', relief='flat').pack(pady=10)

    def admin_logout(self):
        self.admin_session = False
        self.show_main_menu()

if __name__ == '__main__':
    root = tk.Tk()
    data_dir = get_app_data_dir()
    app = SpaceFractionsApp(root, data_dir)
    root.mainloop()
