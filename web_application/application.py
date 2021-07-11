from flask import Flask,  request,  render_template, redirect
from application.recommender import random_recommender, neighbor_recommender, nmf_recommender
from application.utils import ohe_user_boardgames, user_rated_boardgames, rank_ohe_categories,lookup_boardgame

from rq import Queue
from rq.job import Job
from application.worker import conn

q = Queue(connection=conn)


# here we construct a Flack object and the __name__ sets this script as the root
app = Flask(__name__)

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

    #recommendations = random_recommender(10)
    recommendations = nmf_recommender(user_name)

    categories = ohe_user_boardgames('Ser0', 'categories')
    top_categories = rank_ohe_categories(categories)

    mechanics = ohe_user_boardgames('Ser0', 'machanics')
    top_mechanics = rank_ohe_categories(mechanics)

    #send job to worker process
    #job = q.enqueue(nmf_recommender, user_name, job_id='nmf_job')
    #print(job.get_id())
    #print(job.get_status())
    #print(job.key)
    
    return render_template('recommend.html',user_name=user_name, 
                                            recommendations=recommendations,
                                            top_categories=top_categories,
                                            top_mechanics=top_mechanics)

@app.route('/recommend_new_user')
def recommend_new_user():
    user_name = request.args.getlist('user_name')[0]
    print(user_name)
    recommendations = random_recommender(15)

    
    return render_template('new_user_recommend.html', recommendations=recommendations)


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
