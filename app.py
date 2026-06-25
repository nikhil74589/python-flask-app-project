from flask import *
from models import *
from flask_migrate import *
from sqlalchemy import text
from config import Config
from db import *
from flask_bcrypt import Bcrypt
from utils.auth import login_required
from routes.students_routes import student_bp
from routes.authors_routes import author_bp

app = Flask(__name__)
app.secret_key="this-is-mylibrary-app"
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
bcrypt=Bcrypt(app)

@app.route("/db-health")
def db_health():
    try:
        db.session.execute(text("SELECT 1"))
        return {"status":"ok","database":"Connected"}
    except Exception as e:
        return {"status":str(e)}


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/user-login",methods=["GET","POST"])
def user_login():
    if request.method == "POST":
        email = request.form.get("user_email")
        password = request.form.get("user_pass")

        if not email and password:
            return "Please provide valid Credentials"

        user = Student.query.filter_by(stu_email=email).first()

        if user and bcrypt.check_password_hash(user.stu_password, password):

            session["user_id"] = user.id
            session["role"] = user.role
            session["name"]= user.stu_name

            return redirect(url_for('home'))

        else:
            return "Invalid credentials"

    return render_template("login.html")

@app.route("/logout")
def user_logout():
    session.clear()
    return redirect(url_for("home"))

app.register_blueprint(student_bp, url_prefix="/student")
app.register_blueprint(author_bp, url_prefix="/author")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)