# -*- coding: utf-8 -*-

import logging


from glashammer import make_app
from glashammer.bundles import gae
from glashammer.bundles import sessions
from glashammer.utils import local

from google.appengine.api import users
from google.appengine.ext.appstats.recording import appstats_wsgi_middleware

import wtforms

import views
import utils

from google.appengine.ext import ereporter

ereporter.register_logger()

TEMPLATES_DIRECTORY = 'templates'

# Main application setup
def setup(app):
    logging.getLogger().setLevel(logging.DEBUG)

    # add the gae init function
    app.add_setup(gae.setup_gae)
    app.add_setup(sessions.setup_app)
    #app.conf.change_single('sessions/cookie_name', 'flash_message')
    #app.conf.change_single('sessions/secret', 'c00kie_m0nster')

    app.add_middleware(appstats_wsgi_middleware)

    # setup templates
    app.add_template_searchpath(TEMPLATES_DIRECTORY)
    app.add_template_global('login', users.create_login_url("/home/"))
    app.add_template_global('logout', users.create_logout_url("/"))
    app.add_template_global('user', local('gae_user'))
    app.add_template_global('account', local('account'))

    app.add_template_filter('preview', utils.preview)

    app.add_url('/', 'main/index', view=views.index)
    app.add_url('/home/', 'home', view=views.home)
    app.add_url('/home/dashboard/', 'home/dashboard', view=views.dashboard)
    app.add_url('/home/submit/', 'home/submit', view=views.submit)
    app.add_url('/home/first/', 'home/first', view=views.first)
    app.add_url('/home/profile/', 'home/profile', view=views.profile)
    app.add_url('/home/preview/<int:submission_id>/', 'home/preview', view=views.preview)
    app.add_url('/home/resubmit/<int:submission_id>/', 'home/resubmit', view=views.resubmit)
    app.add_url('/submissions/', 'submissions/index', view=views.submissions_index)
    app.add_url('/faq/', 'main/faq', view=views.faq)
    app.add_url('/admin/faq/group/', 'admin/faq/group', view=views.faq_admin_group)
    app.add_url('/admin/faq/question/', 'admin/faq/question', view=views.faq_admin_question)

def main():
    gae.make_and_run_gae_app(setup)

if __name__ == '__main__':
    main()
