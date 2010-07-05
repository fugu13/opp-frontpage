from glashammer.utils import redirect, url_for, Response, local
from flash import render_response, flash

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
    user = local.gae_user
    account = models.GoogleAccount.gql('WHERE google_user = :1', user).get()
    if account:
        any_submission_key = db.GqlQuery('SELECT __key__ FROM Submission WHERE account = :1', account.key()).get()
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
    return render_response("dashboard.html")

@utils.with_account
def submit(request):
    if request.method == "POST":
        form = forms.SubmissionForm(request.form)
        if form.validate():
            submission = models.Submission(account=local.account,
                                           simultaneous=form.simultaneous.data,
                                           cover_letter=db.Text(utils.text_tidy(form.cover_letter.data)),
                                           title=utils.text_tidy(form.title.data),
                                           text_list=[db.Text(utils.text_tidy(form.text.data))],
                                           categories=form.categories.data)
            submission.put()
            flash("Your submission has been saved.")
            return redirect(url_for('home/preview', submission_id=submission.key().id()))
    else:
        form = forms.SubmissionForm()
    return render_response('submit.html', form=form)


@utils.with_account
def resubmit(request, submission_id):
    submission = models.Submission.get_by_id(submission_id)
    if submission is None or submission.account.key().id() != local.account.key().id():
        logging.warning('Attempt to resubmit submission "%s" by account "%s" with email "%s".' % (submission_id, local.account.key().id(), local.account.email))
        return redirect(url_for('main/index'))
    if request.method == "POST":
        form = forms.ResubmissionForm(request.form)
        if form.validate():
            submission.text_list.append(db.Text(utils.text_tidy(form.text.data)))
            submission.put()
            flash("Your submission has been updated.")
            return redirect(url_for('home/preview', submission_id=submission.key().id()))
    else:
        form = forms.ResubmissionForm(obj=submission)
    return render_response('resubmit.html', form=form, submission=submission)

def render_profile(request, template_name, redirect_url):
    if request.method == "POST":
        form = forms.ProfileForm(request.form)
        if form.validate():
            provided = False
            if form.full_name.data:
                local.account.full_name = form.full_name.data
                provided = True
            if form.alternate_email.data:
                local.account.alternate_email = form.alternate_email.data
                provided = True
            if provided:
                local.account.put()
                flash("Your profile information has been saved.")
            return redirect(redirect_url)
    else:
        form = forms.ProfileForm(obj=local.account)
    return render_response(template_name, form=form)


@utils.with_account
def first(request):
    return render_profile(request, "first.html", url_for('home/submit'))

@utils.with_account
def profile(request):
    return render_profile(request, "profile.html", url_for('home/profile'))

@utils.with_account
def preview(request, submission_id):
    submission = models.Submission.get_by_id(submission_id)
    if submission is None or submission.account.key().id() != local.account.key().id():
        logging.warning('Attempt to retrieve submission "%s" by account "%s" with email "%s".' % (submission_id, local.account.key().id(), local.account.email))
        return redirect(url_for('main/index'))
    return render_response("preview.html", submission=submission)

#TODO: tracking of ads. Maybe some sort of middleware?
