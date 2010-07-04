from wtforms import Form, TextField, TextAreaField, IntegerField, RadioField, BooleanField, SelectMultipleField, validators

import models


class GroupForm(Form):
    title = TextField(u'Title', validators=[validators.required()])
    weight = IntegerField(u'Weight', validators=[validators.required()])

class QuestionForm(Form):
    question = TextField(u'Question', validators=[validators.required()])
    answer = TextAreaField(u'Answer', validators=[validators.required()])
    weight = IntegerField(u'Weight', validators=[validators.required()])
    group = RadioField(u'Group')
    
    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.group.choices = [(str(group.key().id()), group.title) for group in models.FrequentlyAskedQuestionGroup.all().order('weight')]


category_choices = ['Speculative', 'Literary', 'Dramatic', 'Translated']

class SubmissionForm(Form):
    simultaneous = BooleanField(u'Simultaneous', validators=[validators.required()])
    cover_letter = TextAreaField(u'Cover Letter', validators=[validators.required()])
    title = TextField(u'Title', validators=[validators.required()])
    text = TextAreaField(u'Text', validators=[validators.required(), validators.Length(min=2500)])
    categories = SelectMultipleField(u'Categories', choices=[(category, category) for category in category_choices], validators=[validators.required()])


class ProfileForm(Form):
    full_name = TextField(u'Full Name', validators=[validators.required()])
    alternate_email = TextField(u'Email', validators=[validators.required(), validators.Email()])
