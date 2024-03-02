# quiz.py
from flask import Blueprint, render_template

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/quiz', methods=['GET', 'POST'])
def quiz():
    # Quiz logic here
    return render_template('quiz.html')
