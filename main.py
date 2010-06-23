# -*- coding: utf-8 -*-

from glashammer import make_app
from glashammer.bundles import gae

import wtforms

from views import *


TEMPLATES_DIRECTORY = 'templates'

# Main application setup
def setup(app):
    # add the gae init function
    app.add_setup(gae.setup_gae)

    # setup templates
    app.add_template_searchpath(TEMPLATES_DIRECTORY)
    app.add_url('/', 'main/index', view=index)
    app.add_url('/submissions/', 'submissions/index', view=submissions_index)
    app.add_url('/faq/', 'main/faq', view=faq)
    app.add_url('/admin/faq/group/', 'admin/faq/group', view=faq_admin_group)
    app.add_url('/admin/faq/question/', 'admin/faq/question', view=faq_admin_question)    

def main():
    gae.make_and_run_gae_app(setup)

if __name__ == '__main__':
    main()
