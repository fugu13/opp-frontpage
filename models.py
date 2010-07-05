from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from glashammer.utils import url_for, local

class FrequentlyAskedQuestionGroup(db.Model):
    title = db.StringProperty(required=True)
    weight = db.IntegerProperty(required=True)
    
    def get_faqs(self):
        return sorted(self.faq_set, key=lambda x: x.weight)
    
    faqs = property(get_faqs)

class FrequentlyAskedQuestion(db.Model):
    question = db.TextProperty(required=True)
    answer = db.TextProperty(required=True)
    group = db.ReferenceProperty(FrequentlyAskedQuestionGroup, collection_name='faq_set', required=True)
    weight = db.IntegerProperty(required=True)
    

class Account(polymodel.PolyModel):
    email = db.EmailProperty(required=True)
    full_name = db.StringProperty()
    alternate_email = db.EmailProperty()

    def nickname(self):
        if self.full_name:
            return self.full_name
        return self.email
    
    def get_ordered_submissions(self):
        return sorted(self.submissions, key=lambda i: i.created)

    ordered_submissions = property(get_ordered_submissions)

class GoogleAccount(Account):
    google_user = db.UserProperty(required=True)

#class FacebookAccount(Account):
#    pass
#    work on this later; google accounts first.

class Submission(db.Model):
    account = db.ReferenceProperty(Account, collection_name='submissions', required=True)
    simultaneous = db.BooleanProperty(required=True)
    cover_letter = db.TextProperty(required=True)
    title = db.StringProperty(required=True)
    text_list = db.ListProperty(item_type=db.Text)
    categories = db.StringListProperty()
    status = db.StringProperty(default="Submitted")
    created = db.DateTimeProperty(auto_now_add=True)
    altered = db.DateTimeProperty(auto_now=True)

    def get_preview_url(self):
        return url_for("home/preview", submission_id=self.key().id())

    preview_url = property(get_preview_url)

    def get_text(self):
        return self.text_list[-1]

    text = property(get_text)
