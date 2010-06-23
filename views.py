
from glashammer.utils import render_response, redirect, url_for

from gdata import service
import gdata.alt.appengine

import models
import forms

def index(request):
    blogger = service.GDataService()
    gdata.alt.appengine.run_on_appengine(blogger)
    blogger.server = 'www.blogger.com'
    query = service.Query()
    query.feed = '/feeds/4649512382725800133/posts/default'
    query.max_results = 3
    feed = blogger.Get(query.ToUri())
    return render_response('index.html', entries=feed.entry)


def submissions_index(request):
    return render_response('submissions.html')


def faq(request):
    return render_response('faq.html', groups=models.FrequentlyAskedQuestionGroup.all().order('weight'))


def faq_admin_group(request):
    if request.method == 'POST':
        form = forms.GroupForm(request.form)
        if form.validate():
            group = models.FrequentlyAskedQuestionGroup(title=form.title.data, weight=form.weight.data)
            group.put()
            redirect(url_for('admin/faq/group'))
    else:
        form = forms.GroupForm()
    return render_response('faq_admin_group.html', form=form)


def faq_admin_question(request):
    form = forms.QuestionForm(request.form)
