from google.appengine.ext import db
from google.appengine.ext.db import polymodel


class FrequentlyAskedQuestionGroup(db.Model):
    title = db.StringProperty(required=True)
    weight = db.IntegerProperty(required=True)
    
    def _get_faqs(self):
        return sorted(self.faq_set, key=lambda x: x.weight)
    
    faqs = property(_get_faqs)

class FrequentlyAskedQuestion(db.Model):
    question = db.TextProperty(required=True)
    answer = db.TextProperty(required=True)
    group = db.ReferenceProperty(FrequentlyAskedQuestionGroup, collection_name='faq_set', required=True)
    weight = db.IntegerProperty(required=True)
    

class Account(polymodel.PolyModel):
    email = db.EmailProperty(required=True)
    full_name = db.StringProperty()
    alternate_email = db.EmailProperty()

class GoogleAccount(Account):
    user = db.UserProperty(required=True)

#class FacebookAccount(Account):
#    pass
#    work on this later; google accounts first.

class Submission(db.Model):
    account = db.ReferenceProperty(Account, collection_name='submissions', required=True)
    simultaneous = db.BooleanProperty()
    cover_letter = db.TextProperty()
    title = db.StringProperty()
    text = db.TextProperty()
    categories = db.StringListProperty()
