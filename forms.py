from wtforms import Form, TextField, TextAreaField, IntegerField, RadioField, BooleanField, SelectMultipleField, validators

import models
import utils

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


category_choices = [('Speculative', 'Speculative (Science Fiction &amp; Fantasy)'),
                    ('Literary', 'Literary'),
                    ('Dramatic', 'Dramatic'),
                    ('Translated', 'Translated')
                   ]

class SubmissionForm(Form):
    title = TextField(u'Title', validators=[validators.required(message="Please enter a title for your submission.")])
    cover_letter = TextAreaField(u'Cover Letter', validators=[validators.required("Please provide a cover letter to go with your submission.")])
    text = TextAreaField(u'Text', validators=[validators.required("Please enter the text of your submission."), validators.Length(min=2500, message="A submission must be at least 2500 characters. Make sure your copy/paste included everything.")])
    simultaneous = BooleanField(u'Simultaneous?')
    categories = SelectMultipleField(u'Categories',
                                        choices=category_choices,
                                        validators=[validators.required("Please select at least one category.")],
                                        widget=utils.select_multi_checkbox,
                                        id="category_select")


class ResubmissionForm(Form):
    text = TextAreaField(u'Text', validators=[validators.required("Please enter the text of your submission."), validators.Length(min=2500, message="A submission must be at least 2500 characters. Make sure your copy/paste included everything.")])

class ProfileForm(Form):
    full_name = TextField(u'Full Name')
    alternate_email = TextField(u'Alternate Email', validators=[validators.Email(), validators.optional()])
