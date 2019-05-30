from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

bp = Blueprint('oai', __name__)

@bp.route('/')
def index():
    return 'Index Page'