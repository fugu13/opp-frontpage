from glashammer.utils import render_response, redirect, url_for

from google.appengine.api import users
from google.appengine.ext import db

from gdata import service
import gdata.alt.appengine

import models
import forms
import utils

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
            return redirect(url_for('main/faq'))
    else:
        form = forms.GroupForm()
    return render_response('faq_admin_group.html', form=form)


def faq_admin_question(request):
    if request.method == 'POST':
        form = forms.QuestionForm(request.form)
        if form.validate():
            group = models.FrequentlyAskedQuestionGroup.get_by_id(int(form.group.data))
            question = models.FrequentlyAskedQuestion(question=form.question.data, answer=form.answer.data, weight=form.weight.data, group=group.key())
            question.put()
            return redirect(url_for('main/faq'))
    else:
        form = forms.QuestionForm()
    return render_response('faq_admin_question.html', form=form)

def home(request):
    user = users.get_current_user()
    account_key = db.GqlQuery('SELECT __key__ FROM GoogleAccount WHERE google_user = :1', user).get()
    if account_key:
        any_submission_key = db.GqlQuery('SELECT __key__ FROM Submission WHERE account = :1', account_key).get()
        if any_submission_key:
            return redirect(url_for('home/dashboard'))
        else:
            return redirect(url_for('home/submit'))
    else:
        account = models.GoogleAccount(google_user=user, email=user.email())
        account.put()
        return redirect(url_for('home/first'))

@utils.with_account
def dashboard(request):
    return ""

@utils.with_account
def submit(request):
    return ""

@utils.with_account
def first(request):
    return ""

@utils.with_account
def profile(request):
    return ""
