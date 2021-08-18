from flask import Flask,  request,  render_template, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from application.recommender import random_recommender, nmf_recommender
from application.utils import ohe_user_boardgames, rank_ohe_categories, get_user_boardgame_ratings
from application.utils import lookup_boardgamenames, create_max_id, get_boardgame_names, create_new_user

from rq import Queue
from rq.job import Job
from application.worker import conn

q = Queue(connection=conn)


# here we construct a Flack object and the __name__ sets this script as the root
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['CONNECT_AWS_POSTGRES_BOARDGAMEGEEKS']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# a python decorator for defining a mapping between a url and a function
@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/new_user_form')
def new_user_form():
    return render_template('new_user_form.html')


@app.route('/recommend')
def recommend():
    user_name = request.args.getlist('user_name')[0]
    print(user_name)
    print('get user data')
    user = get_user_boardgame_ratings(user_name, db.engine)
    print('create recommendations')
    #recommendations = random_recommender(10, db.engine)
    max_id = create_max_id(db.engine)
    recommendations = nmf_recommender(user, max_id, db.engine)
    print('recommendations created')
    categories = ohe_user_boardgames(user, 'categories')
    top_categories = rank_ohe_categories(categories)

    mechanics = ohe_user_boardgames(user, 'machanics')
    top_mechanics = rank_ohe_categories(mechanics)

    print('finished')
    return render_template('recommend.html',user_name=user_name, 
                                            recommendations=recommendations,
                                            top_categories=top_categories,
                                            top_mechanics=top_mechanics)

@app.route('/recommend_new_user')
def recommend_new_user():
    print(request.args)
    user_name = request.args.getlist('user_name')[0]
    boardgames = request.args.getlist('boardgame')
    while '' in boardgames:
        boardgames.remove('')
    ratings = request.args.getlist('rating')
    while '' in ratings:
        ratings.remove('')   
    ratings = [int(rating) for rating in ratings]
    boardgame_names = get_boardgame_names(db.engine)
    boardgames = lookup_boardgamenames(boardgames, boardgame_names) 
    new_user = {
        'boardgames':boardgames,
        'ratings':ratings
    }
    new_user = create_new_user(new_user, db.engine)
    print('create recommendations')
    #recommendations = random_recommender(10)
    max_id = create_max_id(db.engine)
    recommendations = nmf_recommender(new_user, max_id, db.engine)
    print('recommendations created')
    categories = ohe_user_boardgames(new_user, 'categories')
    top_categories = rank_ohe_categories(categories)

    mechanics = ohe_user_boardgames(new_user, 'machanics')
    top_mechanics = rank_ohe_categories(mechanics)

    print('finished')
    return render_template('recommend.html',user_name=user_name, 
                                            recommendations=recommendations,
                                            top_categories=top_categories,
                                            top_mechanics=top_mechanics)


#@app.route("/results/<job_key>", methods=['GET'])
#def get_results(job_key):
#
#    job = Job.fetch(job_key, connection=conn)
#    if job.is_finished:
#        return str(job.result), 200
#    else:
#        print('Job not finished')
#        return redirect(f"/results/nmf_job")



if __name__ == "__main__":
    # runs app and debug=True ensures that when we make changes the web server restarts
    app.run(debug=True)
