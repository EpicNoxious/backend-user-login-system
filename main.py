import time
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session
from pymongo import MongoClient
from forms import GetStarted, SignUp, SignIn, SignOut
from functools import wraps
from turbo_flask import Turbo
import uuid

app = Flask(__name__)
turbo = Turbo(app)
app.secret_key = 'Login System'
cluster = "mongodb://localhost:27017"
client = MongoClient(cluster)
db = client['practice']
users = db.login_system_data


class User:
    def start_session(self, user):
        del user['password']
        session['logged_in'] = True
        session['user'] = user
        return jsonify(user), 200

    def signup(self, user_data):
        user = {
            "_id": user_data['_id'],
            "name": user_data['name'],
            "email": user_data['email'],
            "password": user_data['password']
        }
        users.insert_one(user)
        flash("")
        return self.start_session(user)

    def signin(self, user_data):
        user = {
            "_id": user_data['_id'],
            "name": user_data['name'],
            "email": user_data['email'],
            "password": user_data['password']
        }
        return self.start_session(user)


    def signout(self):
        session.clear()
        return redirect('/')


@app.after_request
def after_request(response):
    # if the response has the turbo-stream content type, then append one more
    # stream with the contents of the alert section of the page
    if response.headers['Content-Type'].startswith(
            'text/vnd.turbo-stream.html'):
        response.response.append(turbo.update(
            render_template('alert.html'), 'alert').encode())
        if response.content_length:
            response.content_length += len(response.response[-1])
    return response


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect("/")

    return wrap


@app.route("/", methods=['GET', 'POST'])
def index():
    begin = GetStarted()
    if begin.validate_on_submit():
        return redirect(url_for('sign_up_in'))
    return render_template('index.html', begin=begin)


@app.route("/register", methods=['GET', 'POST'])
def sign_up_in():
    signup = SignUp()
    signin = SignIn()
    name_error = ''
    if signup.signup.data and signup.validate():
        print('Sign Up')
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        result = users.find_one({'email': email})

        if result is not None:
            flash("User already exists")

        elif password != confirm_password:
            flash("Passwords don't match")

        else:
            user_data = {
                '_id': uuid.uuid4().hex,
                 'name': name,
                 'email': email,
                 'password': password
                 }
            user = User()
            user.signup(user_data)
            time.sleep(1)
            return redirect(url_for('success'))

        if turbo.can_stream():
            return turbo.stream(turbo.update(name_error, 'name_error'))

    if signin.signin.data and signin.validate():
        print('Sign In')
        email = request.form['email']
        password = request.form['password']
        user_data = users.find_one({'email': email})
        if user_data is None:
            flash("No such email exist")
        elif password != user_data['password']:
            flash("Incorrect Password")
        else:
            user = User()
            user.signin(user_data)
            time.sleep(1)
            return redirect(url_for('success'))

        if turbo.can_stream():
            return turbo.stream(turbo.update(name_error, 'name_error'))



    return render_template("sign_up_in.html", signup=signup, signin=signin)


@app.route("/success", methods=['GET', 'POST'])
@login_required
def success():
    signout = SignOut()
    user = User()
    if signout.validate_on_submit():
        user.signout()
        time.sleep(1)
        return redirect(url_for('index'))
    return render_template('success.html', signout=signout)


@app.route("/signout", methods=['GET', 'POST'])
def signout():
    user = User()
    return user.signout()


if __name__ == "__main__":
    app.run(use_reloader=True)
