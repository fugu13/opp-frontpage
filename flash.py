from glashammer.utils import local
import glashammer.utils
import sys


def flash(message):
    if 'flash' in local.session:
        local.session['flash'].append(message)
    else:
        local.session['flash'] = [message]


def get_flash():
    if 'flash' in local.session:
        flash_message = local.session['flash']
        del local.session['flash']
        return flash_message
    return None


def render_response(template, **kwargs):
    return glashammer.utils.render_response(template, flash=get_flash(), **kwargs)
