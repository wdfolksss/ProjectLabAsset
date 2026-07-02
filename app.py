from flask import Flask, render_template, request, redirect, flash, session
import pymysql
from pymysql.cursors import DictCursor

app = Flask(__name__)
app.secret_key = "labasset123"

#database
def get_db():
    return pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="lab_asset",
        cursorclass=DictCursor
    )

#login
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            conn = get_db()
            cursor = conn.cursor()
            sql = "SELECT * FROM users WHERE username=%s AND password=%s"
            cursor.execute(sql, (username, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
                session["id"] = user["id"]
                session["username"] = user["username"]
                session["role"] = user["role"]
                
                if user["role"] == "admin":
                    return redirect("/admin/dashboard")
                elif user["role"] == "asisten":
                    return redirect("/asisten/dashboard")
            else:
                flash("Username atau Password salah!")
        except Exception as e: flash(f"Error: {e}")
    return render_template("login.html")

#dashboard admin
@app.route("/admin/dashboard")
def dashboard_admin():
    return render_template("admin/dashboard.html")


#dashboard asisten
@app.route("/asisten/dashboard")
def dashboard_asisten():
    return render_template("asisten/dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)