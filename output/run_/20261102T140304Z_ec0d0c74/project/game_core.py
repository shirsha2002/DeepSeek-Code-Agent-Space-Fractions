from fractions import Fraction

class Question:
    """Represents a multiple-choice fraction question.
    
    Public constructor: Question(qid, prompt, options, answer, explanation='').
    qid is any non-empty string. options is a list of strings each parseable as a Fraction.
    answer is one of the options and must parse as a Fraction.
    check(answer_string) returns True if the given string is equivalent to the stored answer,
    False otherwise (including invalid input).
    """
    def __init__(self, qid, prompt, options, answer, explanation=''):
        if not isinstance(qid, str) or not qid:
            raise ValueError('qid must be a non-empty string')
        if not isinstance(prompt, str) or not prompt:
            raise ValueError('prompt must be a non-empty string')
        if not isinstance(options, list) or not options:
            raise ValueError('options must be a non-empty list')
        for opt in options:
            if not isinstance(opt, str) or not opt:
                raise ValueError('each option must be a non-empty string')
            try:
                Fraction(opt)
            except (ValueError, ZeroDivisionError):
                raise ValueError(f'invalid fraction option: {opt}')
        if not isinstance(answer, str) or not answer:
            raise ValueError('answer must be a non-empty string')
        try:
            Fraction(answer)
        except (ValueError, ZeroDivisionError):
            raise ValueError(f'invalid fraction answer: {answer}')
        if answer not in options:
            raise ValueError('answer must be one of the options')
        self.qid = qid
        self.prompt = prompt
        self.options = list(options)
        self.answer = answer
        self.explanation = explanation

    def check(self, answer_string):
        """Return True if answer_string is equivalent to self.answer; False otherwise."""
        try:
            return Fraction(answer_string) == Fraction(self.answer)
        except (ValueError, ZeroDivisionError):
            return False

class Game:
    """Manages game state and scoring.
    
    Public API:
    Game(questions) with non-empty list of Question.
    State strings exactly: 'playing', 'paused', 'game_over'.
    submit(answer_string) returns True if correct, False if wrong; raises ValueError if paused,
    game_over, or current question already answered. A correct answer scores once.
    next_question() advances after answered; sets state='game_over' after last. Raises ValueError
    if unanswered or not playing.
    pause()/resume() handle state transitions. restart() resets all state.
    """
    def __init__(self, questions):
        if not isinstance(questions, list) or not questions:
            raise ValueError('questions must be a non-empty list')
        if not all(isinstance(q, Question) for q in questions):
            raise ValueError('all items must be Question instances')
        self.questions = list(questions)
        self.state = 'playing'
        self.score = 0
        self.index = 0
        self.answered_current = False

    def submit(self, answer_string):
        if self.state == 'paused':
            raise ValueError('cannot submit while paused')
        if self.state == 'game_over':
            raise ValueError('game is over')
        if self.answered_current:
            raise ValueError('current question already answered')
        q = self.questions[self.index]
        correct = q.check(answer_string)
        if correct:
            self.score += 1
        self.answered_current = True
        return correct

    def next_question(self):
        if self.state != 'playing':
            raise ValueError('can only advance while playing')
        if not self.answered_current:
            raise ValueError('current question not answered')
        self.index += 1
        self.answered_current = False
        if self.index >= len(self.questions):
            self.state = 'game_over'

    def pause(self):
        if self.state != 'playing':
            raise ValueError('can only pause while playing')
        self.state = 'paused'

    def resume(self):
        if self.state != 'paused':
            raise ValueError('can only resume while paused')
        self.state = 'playing'

    def restart(self):
        self.state = 'playing'
        self.score = 0
        self.index = 0
        self.answered_current = False
