from wtforms import Form, TextField, TextAreaField, IntegerField, RadioField, validators

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
