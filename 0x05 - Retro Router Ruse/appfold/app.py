import os
import smtplib
import sqlite3
import uuid
from functools import wraps
from urllib import response

import requests
from flask import Flask, render_template, request, flash, redirect, session, url_for, make_response


app = Flask(__name__)
app.secret_key = '329302-32193-2_+_@+#+@_#+_@+#V@<#>V:"#>@{V#:@'
connection = sqlite3.connect('app.db', check_same_thread=False)
cursor = connection.cursor()
cursor1 = connection.cursor()

generated_tokens = {}
generated_tokens1 = {}


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged" in session:
            return f(*args, **kwargs)
        else:
            flash("Attempt to register", "flash1")
            return redirect("/login")

    return wrap


def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "adminLogged" in session:
            return f(*args, **kwargs)
        else:
            flash("Dont skip steps", "flash1")
            return redirect("/login")

    return wrap




@app.route("/", methods=['POST', 'GET'])
def homepage():
    return render_template("index.html")


@app.route("/login", methods=['POST', 'GET'])
def login():

    if request.method == "GET":
        return render_template("login.html")
    else:
        if not request.form.get("email") or not request.form.get("password"):
            flash("Please enter email and password.", "flash1")
            return render_template("login.html")
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            result = cursor.execute("SELECT email FROM users WHERE email = ? AND password = ?", (email, password))
            user = result.fetchall()
            if len(user) == 1:
                flash("Invalid email or password.", "flash1")
                return render_template("login.html")
            else:
                flash("Invalid email or password.", "flash1")
                return render_template("login.html")
        except Exception as e:
            print("problem:" + str(e))
            flash("An unexpected error occured, please try again.\n", "danger")
    return render_template("login.html")


@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        if not request.form.get("email") or not request.form.get("password") or not request.form.get(
                "confirm_password"):
            flash("Please fill in all the required fields.", "flash1")
            return render_template("register.html")
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if (password != confirm_password):
            flash("Password did not match", "flash1")
            return render_template("register.html")
        try:
            cursor1.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            if email != "admin@sheridancollege.ca" or password != "sheridaniscool1234":
                flash("You did not enter the same credentials", "flash1")
                return render_template("register.html")
            else:
                connection.commit()
                flash("User has been registered successfully, Please login now.", "flash1")
                return redirect(url_for("login"))
        except Exception as e:

            flash("Some error has occured, maybe something changed at the logic screen.\n", "flash1")
            session["logged"] = True
            print("problem:" + str(e))

        return render_template("register.html")


@app.route("/reset")
def reset():
    flash("page has been reset", "success")
    session.pop("logged", None)
    session.pop("adminLogged", None)
    session.clear()
    return render_template("login.html")


@app.route("/resetpassword", methods=['POST', 'GET'])
@login_required
def resetpassword():
    # flash("Enter the email provided", "flash2")
    if request.form.get("email") == "admin@sheridancollege.ca":
        flash("Email sent", "flash1")
        email = request.form.get('email')
        token1 = str(uuid.uuid4())
        generated_tokens[email] = token1
        token = request.args.get("token")

        # switch to https if posted
        response = requests.get("http://" + request.host + "/resetpassword", params={'token': token1})
        print(response)

        print("test1", generated_tokens)

        return render_template("resetpassword.html", token1=token1, token=token, flash2=flash)

    token = request.args.get("token")
    generated_tokens1["admin@sheridancollege.ca"] = token

    if token in generated_tokens.values():
        # send custom URL with the TOKEN

        return render_template("change_password.html")
    else:
        # flash("Wrong token", "flash1")
        print("no match")
        return render_template("resetpassword.html")
    return render_template("resetpassword.html", flash1=flash)


def dict_values_equal(generated_tokens, generated_tokens1):
    return set(generated_tokens.values()) == set(generated_tokens1.values())


@app.route("/change_password", methods=['POST', 'GET'])
def change_password():
    print("test3", generated_tokens)
    print("test4", generated_tokens1)

    if dict_values_equal(generated_tokens, generated_tokens1):
        print("passed")

        password = request.form.get('password')
        confirm_password = request.form.get('newpassword')
        if password != confirm_password:
            flash("Passwords do not match", "flash1")
            return render_template("change_password.html")
        else:
            session["adminLogged"] = True
            return redirect(url_for("you_made_it"))

        return render_template("change_password.html")
    else:
        flash("Token is not valid, send a reset password link first", "flash1")
    return render_template("change_password.html")


@app.route("/you_made_it", methods=['POST', 'GET'])
@admin_required
def you_made_it():  # might need to change this to just login :?

    response = make_response(render_template("you_made_it.html"))
    if dict_values_equal(generated_tokens, generated_tokens1):
        response.headers.add('flag', 'retroCTF{h0St_iS_n022t_s@fE}')
    else:
        flash("no shortcuts", "flash1")
    return response


# @app.route('/admin', methods=['GET', 'POST'])
# @login_required
# def admin():
#     return render_template("admin.html")
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
