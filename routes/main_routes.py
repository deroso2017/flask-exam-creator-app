from flask import Blueprint, render_template

# Create a Blueprint named "main" for organizing routes in this module
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")
