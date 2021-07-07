from flask import Flask,  request,  render_template
from recommender import random_recommender, neighbor_recommender


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
    recommendations = neighbor_recommender(user_name)
    return render_template('recommend.html', user_name=user_name,
                                            recommendations=recommendations)


if __name__ == "__main__":
    # runs app and debug=True ensures that when we make changes the web server restarts
    app.run(debug=True)
