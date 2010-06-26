# -*- coding: utf-8 -*-

from glashammer import make_app
from glashammer.bundles import gae
from glashammer.utils import local

from google.appengine.api import users

import wtforms

import views


TEMPLATES_DIRECTORY = 'templates'

# Main application setup
def setup(app):
    # add the gae init function
    app.add_setup(gae.setup_gae)

    # setup templates
    app.add_template_searchpath(TEMPLATES_DIRECTORY)
    app.add_template_global('login', users.create_login_url("/home/"))
    app.add_template_global('session', local('session'))

    app.add_url('/', 'main/index', view=views.index)
    app.add_url('/home/', 'home', view=views.home)
    app.add_url('/submissions/', 'submissions/index', view=views.submissions_index)
    app.add_url('/faq/', 'main/faq', view=views.faq)
    app.add_url('/admin/faq/group/', 'admin/faq/group', view=views.faq_admin_group)
    app.add_url('/admin/faq/question/', 'admin/faq/question', view=views.faq_admin_question)

def main():
    gae.make_and_run_gae_app(setup)

if __name__ == '__main__':
    main()
