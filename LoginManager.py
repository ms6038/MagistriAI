# auth.py
from flask_login import LoginManager

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return Teacher.query.get(int(user_id))
