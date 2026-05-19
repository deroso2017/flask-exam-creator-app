from flask import Flask
from database import db
from routes.main_routes import main_bp
from routes.upload_routes import upload_bp
from routes.exam_routes import exam_bp
from routes.dashboard_routes import dashboard_bp
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///exam.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Instead of: db = SQLAlchemy(app) modern Flask apps prefer:
# db = SQLAlchemy() and then: db.init_app(app)
db.init_app(app)

app.register_blueprint(main_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(exam_bp)
app.register_blueprint(dashboard_bp)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
