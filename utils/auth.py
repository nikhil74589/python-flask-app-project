from flask import *
from functools import wraps

def login_required(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        if "user_id" not in session:
            return redirect(url_for("user_login"))
        return func(*args,**kwargs)
    return wrapper