from flask import Blueprint, render_template, redirect, url_for

# Create a Blueprint named "main" for organizing routes in this module
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return redirect(url_for("dashboard.dashboard"))
