from google.appengine.ext import db


class FrequentlyAskedQuestionGroup(db.Model):
    title = db.StringProperty(required=True)
    weight = db.IntegerProperty(required=True)
    
    def _get_faqs(self):
        return sorted(self.faq_set, key=lambda x: x.weight)
    
    faqs = property(_get_faqs)

class FrequentlyAskedQuestion(db.Model):
    question = db.StringProperty(required=True)
    answer = db.StringProperty(required=True)
    group = db.ReferenceProperty(FrequentlyAskedQuestionGroup, collection_name='faq_set', required=True)
    weight = db.IntegerProperty(required=True)
    
    
