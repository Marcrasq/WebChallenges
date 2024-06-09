import os
import re
import sqlite3
from functools import wraps
from pydoc import html

from flask import Flask, render_template, request, flash, redirect, session, render_template_string

## Flask app
app = Flask(__name__)
app.secret_key = 'retroCTF{"s3rV3RR_1s_V2n6e2ra3le"}'
## Connect to sqlite3 database
connection = sqlite3.connect('app.db', check_same_thread=False)
## Database cursor
cursor = connection.cursor()
SESSION_COOKIE_SECURE = True
xss_patterns = [
    re.compile(r"<script>", flags=re.I),
    re.compile(r"<[^>]*(on\w+|style|href|src)=[^>]*>", flags=re.I),
    re.compile(r"['\"]\s*(?:\w+\s*=|javascript:)", flags=re.I),
    re.compile(r"<\w+[^>]*(?<!\/)>", flags=re.I),
    re.compile(r"<\s*(i?frame|html|body|img|input|link)[^>]*>", flags=re.I),
    re.compile(r"(?:<\s*style[^>]*>)([\s\S]*?)(?:<\s*\/style[^>]*>)", flags=re.I),
    re.compile(r"(?:<\s*(?:link|script)[^>]*)(?:rel|src)\s*=\s*['\"]\s*(?:stylesheet|javascript)[^'\"]*['\"]",
               flags=re.I),
    re.compile(r"\b(?:eval|document|window)\b", flags=re.I),
]


# https://flask.palletsprojects.com/en/1.0.x/patterns/viewdecorators/
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged" in session:
            return f(*args, **kwargs)
        else:
            flash("Login first", "flash1")
            return redirect("/login")

    return wrap


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")


@app.route("/", methods=['POST', 'GET'])
def homepage():
    return render_template("homepage.html")


# SQL Inject with admin'-- filtered out.
@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        if not request.form.get("username") or not request.form.get("password"):
            flash("Please enter username and password.", "danger")
            return render_template("login.html")
        username1 = request.form.get('username')
        password1 = request.form.get('password')
        try:
            result = cursor.execute(
                "SELECT username FROM users WHERE username = '%s' AND password = '%s'" % (username1, password1))

            result = result.fetchall()
            # censored admin'-- to increase difficulty
            if result == "admin'--":
                return render_template("login.html")

            if len(result) == 1:
                session["logged"] = True
                flash("retroCTF{th3_m0sT_ba5ic_in3j3ct}", "flash1")

                return render_template("login.html")
            else:
                flash("Please enter username and password.", "danger")

                return render_template("login.html")

        except Exception as e:
            print("problem:" + str(e))
            flash("An unexpected error occured, please try again.\n", "danger")
    return render_template("login.html")


# Reflected XSS with search form (improve if possible)
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        comment = request.form['comment']

        if comment == '':
            return redirect('/search')
        else:
            cursor.execute('INSERT INTO text (text) VALUES (?)', (comment,))

    selectAll = cursor.execute('SELECT text FROM text')
    selectAll = selectAll.fetchall()

    searchQuery = request.args.get('q')

    textArray = []

    for comment in selectAll:
        if searchQuery is None or searchQuery in comment:
            textArray.append(comment)

    newTextArray = [i[0] for i in textArray]

    if searchQuery is not None:
        # encoded_input = html.escape(searchQuery)
        for pattern in xss_patterns:
            if pattern.search(searchQuery):
                flash("retroCTF{r3fl3cT3d_th9R3w_t1M3}", "flash1")

                textArray.clear()
                return render_template('search.html', res=newTextArray, searchQuery=searchQuery)

    return render_template('search.html', res=newTextArray)


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    return render_template("admin.html")


# SSTI Challenge
@app.route('/adminpage')
@login_required
def admin_page():
    try:

        if request.args.get('search'):
            search = request.args.get('search')

        else:
            return render_template("adminpage.html")

       # search2 = search.strip("()")

        if "()" not in search and "self" not in search and "(" not in search or (bool(re.search('^[a-zA-Z0-9]*$', search)) == True):

            template = '''<h2>%s <br>
            Suspicious page?</h2>
            ''' % search
            print(search)
        else:
            search is None

            return render_template("adminpage.html")
    except Exception as e:
        print("problem:" + str(e))
        return render_template("adminpage.html")

    return render_template_string(template)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port, SESSION_COOKIE_SECURE=True)
