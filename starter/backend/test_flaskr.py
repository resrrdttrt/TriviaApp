import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category, db
import random



class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_user = "postgres"
        self.database_passward = "1234"
        self.database_host = "localhost:5432"
        self.database_path = "postgres://{}:{}@{}/{}".format(self.database_user, self.database_passward, self.database_host, self.database_name)
        setup_db(self.app, self.database_path)


        # A question for useing in the test.
        self.new_question = {
            "answer": "Uruguay",
            "category": 6,
            "difficulty": 4,
            "question": "Which country won the first ever soccer World Cup in 1930?"
            }


        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    # Category test for endpoint (GET) and failure

    def test_get_paginated_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_categories'])
        self.assertTrue(len(data['categories']))

    def test_404_request_not_exist_categories(self):
        response = self.client().get('/categories/10')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['massage'], 'Not found')


    def test_get_questions_category(self):
        response = self.client().get('/categories/4/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    # Questions test for each endpoint (POST, GET, DELETE)

    def test_get_paginated_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))


    def test_404_request_beyond_valid_page(self):
        response = self.client().get('/questions?page=50')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['massage'], 'Not found')




    # insert new question
    # test to check the new question insert went well or fail.
    def test_insert_new_question(self):
        newquestion = {
            'question': 'new_question',
            'answer': 'new_answer',
            'difficalty': 4,
            'category': 1
        }
        total_questions = db.session.query(Question).all()

        response = self.client().post('/questions', json = newquestion)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    # fail insert new question
    # test to check the new question insert is fail.
    def test_422_failing_insert_new_question(self):
        response = self.client().post('/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["massage"], "Unprocessable")
        


    # delete exist question
    # test to check the deleted question went well or fail but will fail anyway.
    def test_delete_question(self):
        response = self.client().delete('/questions/5')
        data = json.loads(response.data)

        questions = db.session.query(Question).\
        filter(Question.id == 5).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 5)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(question, None)


    def test_422_delete_not_exist_question(self):
        response = self.client().delete('/questions/1000')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data["massage"], "Unprocessable")



    def test_search_questions(self):
        new_search = {'searchTerm': 'd'}
        response = self.client().post('/questions/search', json=new_search)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    def test_404_search_questions_not_exist(self):
        response = self.client().post('/questions/search', json={'searchTerm':'sea검색rch'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        
        
        
  
    # # Quizz play game test for endpoint (POST)

    def test_quizz_game(self):
        quizz_game = {'previous_questions': [],
        'quiz_category': {'id': 4}}

        response = self.client().post('/quizzes', json = quizz_game)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_fail_quizz_game(self):
        quizz_game = {'previous_questions': []}
        response = self.client().post('/quizzes', json = quizz_game)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["massage"], "Unprocessable")



    


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()