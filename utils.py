from functools import wraps

from google.appengine.api import users
from google.appengine.ext import db

from glashammer.utils import local
from glashammer.utils import redirect, url_for

import models

def get_current_account():
    user = users.get_current_user()
    if user:
        return models.GoogleAccount.gql('WHERE google_user = :1', user).get()
    else:
        return None


def with_account(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        account = get_current_account()
        if account:
            local.account = account
            return view(*args, **kwargs)
        else:
            return redirect(url_for('main/index'))
    return wrapper


