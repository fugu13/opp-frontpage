import re
from functools import wraps

from google.appengine.api import users
from google.appengine.ext import db

from glashammer.utils import local
from glashammer.utils import redirect, url_for

import models

from wtforms.widgets import html_params


paragraph_regex = re.compile("\\n\\s*\\n")


def preview(text):
    return "<p>" + "</p><p>".join(paragraph_regex.split(text)) + "</p>"

normalizations = [
    (unichr(8218), "'"), #baseline single quote
    #unichr(402), ""), #florin
    (unichr(8222), '"'), #baseline double quote
    (unichr(8230), "..."), #ellipsis
    #unichr(8224), ""), #dagger
    #unichr(8225), ""), #double dagger
    (unichr(710), "^"), #circumflex accent
    #unichr(8240), ""), #per mile
    #unichr(352), ""), #S Hacek
    (unichr(8249), "<"), #left single guillemet
    (unichr(338), "OE"), #OE ligature
    (unichr(8216), "'"), #left single quote
    (unichr(8217), "'"), #right single quote
    (unichr(8220), '"'), #left double quote
    (unichr(8221), '"'), #right double quote
    (unichr(8226), "*"), #bullet
    #unichr(8211), "-"), #endash
    #unichr(8212), "--"), #emdash
    (unichr(732), "~"), #tilde accent
    (unichr(8482), " (TM)"), #trademark superscript
    #unichr(353), ""), #s Hacek
    (unichr(8250), ">"), #right single guillemet
    (unichr(339), "oe"), #oe ligature
    #unichr(376), ""), #Y dieresis
    ('\r\n', '\n'), #windows newlines
    ('\r', '\n'), #returns without newlines
]



def text_tidy(text):
    for value, replacement in normalizations:
        text = text.replace(value, replacement)
    return text.strip()

def select_multi_checkbox(field, ul_class='', **kwargs):
    kwargs.setdefault('type', 'checkbox')
    field_id = kwargs.pop('id', field.id)
    html = [u'<ul %s>' % html_params(id=field_id, class_=ul_class)]
    for value, label, checked in field.iter_choices():
        choice_id = u'%s-%s' % (field_id, value)
        options = dict(kwargs, name=field.name, value=value, id=choice_id)
        if checked:
            options['checked'] = 'checked'
        html.append(u'<li><input %s /> ' % html_params(**options))
        html.append(u'<label %s>%s</label></li>' % (html_params(for_=field.name), label))
    html.append(u'</ul>')
    return u''.join(html)




def get_current_account():
    user = local.gae_user
    if user:
        return models.GoogleAccount.gql('WHERE google_user = :1', user).get()
    else:
        return None


def with_account(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        account = get_current_account()
        if account:
            local.account = account
            return view(request, *args, **kwargs)
        else:
            return redirect(users.create_login_url(request.path))
    return wrapper

#later do something with glashammer sessions, which are stored client-side. Need some way to prevent cookies from being stolen and used; have secret key include some request information every time? Do a full check for the user when anything with changes is involved?
