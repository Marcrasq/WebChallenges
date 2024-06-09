from pydoc import html

from flask import Flask, render_template, request, redirect, make_response, flash, session, Response
import os
import random

app = Flask(__name__)

title = "Forge The Cookie"
cookie_names = ["sprinkles", "cream", "sandwich", "cookie", "sprinkles", "Oreo", "Syrup", "biscuit",
                "Waffles", "peppermint", "jelly", "chocolate", "jelly",
                "strawberry"]
app.secret_key = random.choice(cookie_names)


@app.after_request
def set_csp_header(response):
    csp = "default-src 'self'"
    response.headers["Content-Security-Policy"] = csp
    return response


@app.route("/")
def main():
    return render_template("homepage.html")


@app.route("/search", methods=["POST"])
def search():
    name = html.escape(request.form.get("name"))
    if name in cookie_names:
        response = make_response(redirect("/display"))
        session["auth"] = name
        return response
    else:
        flash("Not quite right..", "error")
        response = make_response(redirect("/"))
        session["auth"] = "empty"
        return response


@app.route("/display", methods=["GET"])
def flag():
    auth = session.get("auth")
    if auth == "admin":
        flash("retroCTF{f0r9e_t0_th3_9uf_utre}", "success")
        return render_template("homepage.html")
    if auth:
        flash("You're getting somewhere..", "success")
        return render_template("homepage.html", title=title, cookie_name=auth)
    else:
        response = make_response(redirect("/"))
        session["auth"] = "empty"
        return response


@app.route("/reset")
def reset():
    flash("page has been reset", "success")
    session.pop("auth", None)
    return render_template("homepage.html")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
