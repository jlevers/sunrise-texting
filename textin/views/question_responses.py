from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_POST, require_GET
from twilio.twiml.messaging_response import MessagingResponse

from textin.models import Question, QuestionResponse
from textin.util import compose_response

@require_POST
def save_response(request, survey_id, question_id):
    question = Question.objects.get(id=question_id)

    if save_response_from_request(request, question):
        next_question = question.next()
        if not next_question:
            return goodbye(request)
        else:
            return next_question_redirect(next_question.id, survey_id)
    else:
        already_answered_message = "You've already answered that question."
        return HttpResponse(compose_response([already_answered_message]))


def next_question_redirect(question_id, survey_id):
    parameters = {'survey_id': survey_id, 'question_id': question_id}
    question_url = reverse('question', kwargs=parameters)

    twiml_response = MessagingResponse()
    twiml_response.redirect(url=question_url, method='GET')
    return HttpResponse(twiml_response)


def goodbye(request):
    goodbye_message = 'That was the last question. Thank you for taking this survey!'
    return HttpResponse(compose_response([goodbye_message]))


def save_response_from_request(request, question):
    session_id = request.POST['MessageSid']
    request_body = _extract_request_body(request, question.kind)
    phone_number = request.POST['From']

    response = QuestionResponse.objects.filter(question_id=question.id,
                                               message_sid=session_id).first()

    if not response:
        QuestionResponse(message_sid=session_id, phone_number=phone_number, response=request_body,
                         question=question).save()
        return true

    return false  # If they've already answered this question


def _extract_request_body(request, question_kind):
    Question.validate_kind(question_kind)
    key = 'Body'
    return request.POST.get(key)
