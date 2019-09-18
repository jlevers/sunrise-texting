from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET
from twilio.twiml.messaging_response import MessagingResponse

from textin.models import Question
from textin.util import compose_response

@require_GET
def show_question(request, survey_id, question_id):
    question = Question.objects.get(id=question_id)
    twiml = sms_question(question)

    request.session['answering_question_id'] = question.id
    return HttpResponse(twiml, content_type='application/xml')


def sms_question(question):
    twiml_response = compose_response(question.body + ' ' + SMS_INSTRUCTIONS[question.kind])
    return twiml_response

SMS_INSTRUCTIONS = {
    Question.TEXT: None,
    Question.YES_NO: 'Please respond with "Yes" or "No"',
    Question.NUMERIC: 'Please respond with a number'
}
