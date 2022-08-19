from flask import Flask, render_template, request, flash
from pymongo import MongoClient
from forms import SignUp, SignIn
from turbo_flask import Turbo

app = Flask(__name__)
turbo = Turbo(app)
app.secret_key = 'Login System'
cluster = "mongodb://localhost:27017"
client = MongoClient(cluster)
db = client['practice']
users = db.login_system_data


@app.after_request
def after_request(response):
    # if the response has the turbo-stream content type, then append one more
    # stream with the contents of the alert section of the page
    if response.headers['Content-Type'].startswith(
            'text/vnd.turbo-stream.html'):
        print(1)
        response.response.append(turbo.update(
            render_template('alert.html'), 'alert').encode())
        if response.content_length:
            response.content_length += len(response.response[-1])
    return response


@app.route("/", methods=['GET', 'POST'])
def index():
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
            dict = {'name': name, 'email': email, 'password': password}
            users.insert_one(dict)
            flash("User Added")

        if turbo.can_stream():
            return turbo.stream(turbo.update(name_error, 'name_error'))

    if signin.signin.data and signin.validate():
        print('Sign In')
        email = request.form['email']
        password = request.form['password']
        data = users.find_one({'email': email})
        if data is None:
            flash("No such email exist")
        elif password != data['password']:
            flash("Incorrect Password")
        else:
            flash("User Logged In")

        if turbo.can_stream():
            return turbo.stream(turbo.update(name_error, 'name_error'))

    return render_template("sign_up_in.html", signup=signup, signin=signin)


if __name__ == "__main__":
    app.run(use_reloader=True)
