from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from twilio.twiml.messaging_response import MessagingResponse

from textin.models import Question
from textin.strings import QuestionStrings
from textin.util import compose_response

@csrf_exempt
def show_question(request, survey_id, question_id):
    question = Question.objects.get(id=question_id)
    twiml = sms_question(question)

    request.session['answering_question_id'] = question.id
    return HttpResponse(twiml, content_type='application/xml')


def sms_question(question):
    return compose_response(question.body + ' ' + SMS_INSTRUCTIONS[question.kind])

SMS_INSTRUCTIONS = {
    Question.TEXT: QuestionStrings.TEXT,
    Question.YES_NO: QuestionStrings.YES_NO,
    Question.NUMERIC: QuestionStrings.NUMERIC
}
