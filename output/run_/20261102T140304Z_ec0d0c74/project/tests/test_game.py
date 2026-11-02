import unittest
import tempfile
import os
import sqlite3
from contextlib import closing
from fractions import Fraction
from game_core import Question, Game
from storage import (
    init_db, save_question, get_questions, save_score, get_score_history,
    admin_create, admin_authenticate, admin_exists
)

class TestQuestion(unittest.TestCase):
    def test_valid_question(self):
        q = Question('q1', 'Which is larger?', ['1/2', '3/4', '2/5', '5/8'], '3/4', 'Because 3/4 is largest')
        self.assertEqual(q.qid, 'q1')
        self.assertTrue(q.check('3/4'))
        self.assertTrue(q.check('6/8'))
        self.assertFalse(q.check('1/2'))
        self.assertFalse(q.check('invalid'))

    def test_invalid_question(self):
        with self.assertRaises(ValueError):
            Question('', 'Prompt', ['1/2'], '1/2')
        with self.assertRaises(ValueError):
            Question('q', '', ['1/2'], '1/2')
        with self.assertRaises(ValueError):
            Question('q', 'Prompt', [], '1/2')
        with self.assertRaises(ValueError):
            Question('q', 'Prompt', ['1/2'], '3/4')
        with self.assertRaises(ValueError):
            Question('q', 'Prompt', ['a'], '3/4')

class TestGame(unittest.TestCase):
    def setUp(self):
        self.q1 = Question('q1', 'Which is larger?', ['1/2', '3/4', '2/5', '5/8'], '3/4', 'Explanation')
        self.q2 = Question('q2', 'Which is equal to 1/2?', ['3/6', '2/5', '4/7', '5/9'], '3/6', 'Explanation')
        self.game = Game([self.q1, self.q2])

    def test_initial_state(self):
        self.assertEqual(self.game.state, 'playing')
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.index, 0)

    def test_reject_empty_list(self):
        with self.assertRaises(ValueError):
            Game([])

    def test_submit_correct(self):
        self.assertTrue(self.game.submit('3/4'))
        self.assertEqual(self.game.score, 1)

    def test_submit_wrong(self):
        self.assertFalse(self.game.submit('1/2'))
        self.assertEqual(self.game.score, 0)

    def test_submit_equivalent_fraction(self):
        self.assertTrue(self.game.submit('6/8'))
        self.assertEqual(self.game.score, 1)

    def test_submit_invalid_input(self):
        self.assertFalse(self.game.submit('not a fraction'))
        self.assertEqual(self.game.score, 0)

    def test_submit_raises_if_paused(self):
        self.game.pause()
        with self.assertRaises(ValueError):
            self.game.submit('3/4')

    def test_submit_raises_if_game_over(self):
        self.game.submit('3/4')
        self.game.next_question()
        self.game.submit('3/6')
        self.game.next_question()
        with self.assertRaises(ValueError):
            self.game.submit('1/2')

    def test_submit_raises_if_already_answered(self):
        self.game.submit('3/4')
        with self.assertRaises(ValueError):
            self.game.submit('1/2')

    def test_next_question_advances(self):
        self.game.submit('3/4')
        self.game.next_question()
        self.assertEqual(self.game.index, 1)
        self.assertFalse(self.game.answered_current)

    def test_next_question_raises_if_unanswered(self):
        with self.assertRaises(ValueError):
            self.game.next_question()

    def test_next_question_raises_if_not_playing(self):
        self.game.pause()
        with self.assertRaises(ValueError):
            self.game.next_question()

    def test_game_over_after_last(self):
        self.game.submit('3/4')
        self.game.next_question()
        self.assertEqual(self.game.state, 'playing')
        self.game.submit('3/6')
        self.game.next_question()
        self.assertEqual(self.game.state, 'game_over')
        with self.assertRaises(ValueError):
            self.game.submit('1/2')

    def test_pause_resume(self):
        self.game.pause()
        self.assertEqual(self.game.state, 'paused')
        with self.assertRaises(ValueError):
            self.game.pause()
        self.game.resume()
        self.assertEqual(self.game.state, 'playing')
        with self.assertRaises(ValueError):
            self.game.resume()

    def test_restart(self):
        self.game.submit('3/4')
        self.game.next_question()
        self.game.pause()
        self.game.restart()
        self.assertEqual(self.game.state, 'playing')
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.index, 0)
        self.assertFalse(self.game.answered_current)

class TestStorage(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tempdir.name, 'test.db')
        init_db(self.db_path)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_save_and_get_questions(self):
        q = Question('q1', 'Prompt', ['1/2', '3/4'], '3/4', 'Explanation')
        save_question(self.db_path, q)
        questions = get_questions(self.db_path)
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0].qid, 'q1')
        self.assertEqual(questions[0].prompt, 'Prompt')
        self.assertEqual(questions[0].options, ['1/2', '3/4'])
        self.assertEqual(questions[0].answer, '3/4')

    def test_score_history(self):
        save_score(self.db_path, 8, 10)
        save_score(self.db_path, 10, 10)
        history = get_score_history(self.db_path, limit=10)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0][0], 10)
        self.assertEqual(history[1][0], 8)

    def test_admin_create_authenticate(self):
        self.assertFalse(admin_exists(self.db_path))
        self.assertTrue(admin_create(self.db_path, 'securepassword'))
        self.assertTrue(admin_exists(self.db_path))
        self.assertTrue(admin_authenticate(self.db_path, 'securepassword'))
        self.assertFalse(admin_authenticate(self.db_path, 'wrongpassword'))
        self.assertFalse(admin_create(self.db_path, 'another'))

    def test_admin_password_not_stored_plaintext(self):
        admin_create(self.db_path, 'secret')
        with closing(sqlite3.connect(self.db_path)) as conn:
            row = conn.execute('SELECT salt, hash FROM admin').fetchone()
        salt, hashed = row
        self.assertNotIn('secret', hashed)
        self.assertNotIn('secret', salt)

if __name__ == '__main__':
    unittest.main()
