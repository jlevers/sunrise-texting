from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_POST, require_GET
from twilio.twiml.messaging_response import MessagingResponse

from textin.models import Question, QuestionResponse

@require_POST
def save_response(request, survey_id, question_id):
    question = Question.objects.get(id=question_id)

    save_response_from_request(request, question)

    next_question = question.next()
    if not next_question:
        return goodbye(request)
    else:
        return next_question_redirect(next_question.id, survey_id)


def next_question_redirect(question_id, survey_id):
    parameters = {'survey_id': survey_id, 'question_id': question_id}
    question_url = reverse('question', kwargs=parameters)

    twiml_response = MessagingResponse()
    twiml_response.redirect(url=question_url, method='GET')
    return HttpResponse(twiml_response)


def goodbye(request):
    goodbye_message = 'That was the last question. Thank you for taking this survey!'
    response = MessagingResponse()
    response.message(goodbye_message)

    return HttpResponse(response)


def save_response_from_request(request, question):
    session_id = request.POST['MessageSid']
    request_body = _extract_request_body(request, question.kind)
    phone_number = request.POST['From']

    response = QuestionResponse.objects.filter(question_id=question.id,
                                               message_sid=session_id).first()

    if not response:
        QuestionResponse(message_sid=session_id, phone_number=phone_number, response=request_body,
                         question=question).save()
    else:
        response.response = request_body
        response.save()


def _extract_request_body(request, question_kind):
    Question.validate_kind(question_kind)
    key = 'Body'
    return request.POST.get(key)
