from datetime import date
from django.db import models
from django.core.exceptions import ValidationError

class Survey(models.Model):
    title = models.CharField(max_length=255, unique=True)
    end_message = models.CharField(max_length=500,
                                   default="That was the last question. Thank you for taking this survey!")
    start_date = models.DateField(default=date.today)
    end_date = models.DateField()

    @property
    def responses(self):
        return QuestionResponse.objects.filter(question__survey__id=self.id)

    @property
    def responder_count(self):
        return len(Responder.objects.filter(surveys__responder_set__contains=self.id))

    @property
    def first_question(self):
        return Question.objects.filter(survey__id=self.id).order_by('id').first()

    def __str__(self):
        return '%s' % self.title


class Question(models.Model):
    TEXT = 'text'
    YES_NO = 'yes-no'
    NUMERIC = 'numeric'

    QUESTION_KIND_CHOICES = (
        (TEXT, 'Text'),
        (YES_NO, 'Yes or no'),
        (NUMERIC, 'Numeric')
    )

    body = models.CharField(max_length=255)
    kind = models.CharField(max_length=255, choices=QUESTION_KIND_CHOICES)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)

    @classmethod
    def validate_kind(cls, kind):
        if kind not in [cls.TEXT, cls.YES_NO, cls.NUMERIC]:
            raise ValidationError("Invalid question kind")

    def next(self):
        survey = Survey.objects.get(id=self.survey_id)
        next_questions = survey.question_set.order_by('id').filter(id__gt=self.id)
        return next_questions[0] if next_questions else None

    def __str__(self):
        return '%s' % self.body


class Responder(models.Model):
    phone_number = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    surveys = models.ManyToManyField(to=Survey)

    def __str__(self):
        stringified = "<%s" % self.phone_number
        stringified = ("%s\nphone: " % self.name if self.name is not None else "") + stringified
        stringified += ("\nemail: %s" % self.email if self.email is not None else "")
        return stringified + ">"


class QuestionResponse(models.Model):
    response = models.CharField(max_length=255)
    message_sid = models.CharField(max_length=255)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    responder = models.ForeignKey(Responder, on_delete=models.CASCADE)

    def __str__(self):
        return '%s' % self.response

    def as_dict(self):
        return {
            'body': self.question.body,
            'kind': self.question.kind,
            'response': self.response,
            'message_sid': self.message_sid,
        }

    @classmethod
    def valid_response(cls, kind, response):
        if kind == Question.NUMERIC:
            try:
                int(response)
            except ValueError:
                return False
        elif kind == Question.YES_NO:
            first_letter = response[0].lower()
            if first_letter != 'y' and first_letter != 'n':
                return False
        return True
