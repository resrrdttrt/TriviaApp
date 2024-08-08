import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import math
import sys

from models import setup_db, Question, Category, db


# paginate 10 question for each page
QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_question = questions[start:end]

    return current_question

 # create and configure the app
def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    
# @TODO: Set up CORS. Allow '*' for origins.
# Delete the sample route after completing the TODOs
    CORS(app, resources={r"*/api/*": {"origins": "*"}})
# @TODO: Use the after_request decorator to set Access-Control-Allow

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers",
            "Content-Type, Authorization")
        response.headers.add(
            "Access-Control-Allow-Methods",
            "GET, POST, PATCH, DELETE, OPTIONS")
        return response



# @TODO:
# Create an endpoint to handle GET requests
# for all available categories.

    @app.route("/categories")
    def get_categories():
        try:
            #  Query all categoris by id.
            categories_query = db.session.query(Category)\
                .order_by(Category.id).all()
            #  Abort 404 if categories Not found.
            if len(categories_query) == 0:
                abort(404)
            # Return True for found category and cat type and cat length.
            return jsonify({
                'success': True,
                'categories': {category.id: category.type for category in categories_query},
                'total_categories': len(Category.query.all())
            })
        # abort Not found the required data not exist
        except BaseException:
            abort(404)


#   @TODO:
#   Create an endpoint to handle GET requests for questions,
#   including pagination (every 10 questions).
#   This endpoint should return a list of questions,
#   number of total questions, current category, categories.

#   TEST: At this point, when you start the application
#   you should see questions and categories generated,
#   ten questions per page and pagination at the bottom of the screen for three pages.
#   Clicking on the page numbers should update the questions.

    @app.route("/questions")
    def get_questions():
        #  Query all question and paginate_questions
        queryquestion = db.session.query(Question).order_by(Question.id).all()
        print(queryquestion)
        request_question = paginate_questions(request, queryquestion)
        #  Query all categoris by type.
        get_category = db.session.query(Category).order_by(Category.type).all()
        #  Abort 404 if questions in each page.
        if len(request_question) == 0:
            abort(404)
        questid = db.session.query(Question).get(Question.id)
        print(questid)
        #  Return questions cat type and cat length.
        return jsonify({
            'success': True,
            'questions': request_question,
            'total_questions': len(queryquestion),
            # 'categories': {category.id: category.type for category in get_category},
        })
        abort(422)


#   @TODO:
#   Create an endpoint to DELETE question using a question ID.

#   TEST: When you click the trash icon next to a question, the question will be removed.
#   This removal will persist in the database and when you refresh the page.

    @app.route("/questions/<int:questions_id>", methods=["DELETE"])
    def delete_question(questions_id):
        try:
            # Query qustion by id
            # getquestionid = db.session.query(Question).get(Question.id).all
            query_question_todelete = db.session.query(Question)\
                .filter(Question.id == questions_id).one_or_none()
            print(questions_id)
            # abort Not found if couldn't get the id
            if query_question_todelete is None:
                abort(404)
            # after getting the question ids delete the selected id
            query_question_todelete.delete()
            return jsonify({
                'success': True,
                'deleted': questions_id
            })

        except BaseException:
            abort(422)


#   @TODO:
#   Create an endpoint to POST a new question,
#   which will require the question and answer text,
#   category, and difficulty score.

#   TEST: When you submit a question on the 'Add' tab,
#   the form will clear and the question will appear at the end of the last page
#   of the questions list in the 'List' tab.


    @app.route("/questions", methods=["POST"])
    def create_question():
        try:
            # Get the data from the body.
            body = request.get_json()
            newquestion = body.get('question', None)
            newanswer = body.get('answer', None)
            newcategory = body.get('category', None)
            newdifficulty = body.get('difficulty', None)
            # after geting the data insert new question.
            question = Question(
                question=newquestion,
                answer=newanswer,
                difficulty=newdifficulty,
                category=newcategory)
            question.insert()
            # Query all the questions to view the data after new question
            # creation.
            queryallquwstions = db.session.query(
                Question).order_by(Question.id).all()
            newcurrentquestion = paginate_questions(request, queryallquwstions)
            return jsonify({
                'success': True,
                'created': question.id,
                'questions': newcurrentquestion,
                'total_questions': len(Question.query.all())
            })
        except BaseException:
            abort(422)


#   @TODO:
#   Create a POST endpoint to get questions based on a search term.
#   It should return any questions for whom the search term
#   is a substring of the question.

#   TEST: Search by any phrase. The questions list will update to include
#   only question that include that string within their question.
#   Try using the word "title" to start.

    @app.route("/questions/search", methods=["POST"])
    def get_questions_based_on_search_term():
        try:
            # Get search term from body
            searchbody = request.get_json()
            questionsearch = searchbody.get('searchTerm', None)
            # Query any question from the databse using ilike format in order
            # to find any record by search term
            if questionsearch:
                searchresult = db.session.query(Question) .filter(
                    Question.question.ilike('%' + questionsearch + '%')).all()
            return jsonify({
                'success': True,
                'questions': [question.format() for question in searchresult],
                'total_questions': len(searchresult),
                'current_category': None
            })
        except BaseException:
            abort(404)

    # @TODO:
    # Create a GET endpoint to get questions based on category.

    # TEST: In the 'List' tab / main screen, clicking on one of the
    # categories in the left column will cause only questions of that
    # category to be shown.

    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_based_on_category(category_id):
        #  Query Categories by id
        categoriesquery = db.session.query(Category).get(category_id)
        print(categoriesquery)
        # Check if we got all categories by id if not abort Not found.
        if not categoriesquery:
            abort(404)
        # Get each group of question with their categories.
        try:
            questionsbycategories = db.session.query(Question)\
                .filter_by(Question.category == str(category_id)).all()
            # paginate again the questions with their categories then return
            # all for view.
            questionspage = paginate_questions(request, questionsbycategories)
            return jsonify({
                'success': True,
                'questions': questionspage,
                'current_category': str(category_id),
                'total_questions': len(Question.query.all())
            })
        except BaseException:
            abort(404)


#   @TODO:
#   Create a POST endpoint to get questions to play the quiz.
#   This endpoint should take category and previous question parameters
#   and return a random questions within the given category,
#   if provided, and that is not one of the previous questions.

#   TEST: In the 'Play' tab, after a user selects 'All' or a category,
#   one question at a time is displayed, the user is allowed to answer
#   and shown whether they were correct or not.

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            # get the request body , previous questions and the category.
            frombody = request.get_json()
            prevquestion = frombody.get('previous_questions')
            quizzcategory = frombody.get('quiz_category')
            getcategoid = db.session.query(Category).get(category_id)
            # Abort 422 if not get previous_questions and quiz_category
            if ((quizzcategory is None) or (prevquestion is None)):
                abort(422)
            # Query questions which not in prevquestion if not exsit.
            if quizzcategory['id'] == 0:
                prevquiz = db.session.query(Question)\
                    .filter(Question.id.notin_((prevquestion))).all()
            # Query question for called category
            else:
                prevquiz = db.session.query(Question)\
                    .filter_by(category=category['id'])\
                    .filter(Question.id.notin_((prevquestion))).all()
            # Get rondom question using randrange method returns which will
            # selected question from the specified range.
            rondomquiz = prevquiz[random.randrange(
                0, len(prevquiz))].format()if len(prevquiz) > 0 else None

            # return the question
            return jsonify({
                'success': True,
                'question': rondomquiz
            })
        except BaseException:
            abort(422)


#   @TODO:
#   Create error handlers for all expected errors
#   including 404 and 422.

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'massage': 'Not found'
        }), 404

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'massage': 'Not allowed method'
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'massage': 'Unprocessable'
        }), 422

    @app.errorhandler(400)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 400,
            'massage': 'Bad request'
        }), 400

    @app.errorhandler(500)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 500,
            'massage': 'Server error'
        }), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='localhost', port=5000, debug=False)
