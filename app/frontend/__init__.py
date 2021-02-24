from flask import Blueprint

public_bp = Blueprint('public', __name__, template_folder='templates')

from app.frontend import routes