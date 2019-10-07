from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_POST, require_GET
from twilio.twiml.messaging_response import MessagingResponse

from textin.models import Question, QuestionResponse, Responder
from textin.strings import QuestionResponseStrings
from textin.util import compose_response

@require_POST
def save_response(request, survey_id, question_id):
    question = Question.objects.get(id=question_id)

    # If they haven't yet answered this question
    if not already_answered(request.POST['From'], question.id):

        # Process invalid answers
        valid = save_response_from_request(request, question)
        if not valid:
            twiml_response = compose_response(invalid_response_message)
            question_params = {'survey_id': question.survey.id, 'question_id': question.id}
            twiml_response.redirect(reverse('textin:question', question_params))
            return HttpResponse(twiml_response)

        next_question = question.next()
        if not next_question:
            return goodbye(request, question)
        else:
            return next_question_redirect(next_question.id, survey_id)
    else:
        return HttpResponse(compose_response(QuestionResponseStrings.already_answered))


def next_question_redirect(question_id, survey_id):
    next_question_params = {'survey_id': survey_id, 'question_id': question_id}
    question_url = reverse('textin:question', kwargs=next_question_params)

    twiml_response = MessagingResponse()
    twiml_response.redirect(url=question_url, method='GET')
    return HttpResponse(twiml_response)


def goodbye(request, question):
    goodbye_message = question.survey.end_message
    if goodbye_message:
        return HttpResponse(compose_response(goodbye_message))
    return HttpResponse(status=204)


def save_response_from_request(request, question):
    request_body = _extract_request_body(request, question.kind)
    phone_number = request.POST['From']

    if not QuestionResponse.valid_response(question.kind, request_body):
        return False

    QuestionResponse(message_sid=request.POST['MessageSid'],
                     response=request_body,
                     question=question,
                     responder=Responder.objects.get(phone_number=phone_number)).save()
    return True


def already_answered(phone_number, question_id):
    return len(QuestionResponse.objects.filter(question_id=question_id,
                                               responder__phone_number=phone_number))


def _extract_request_body(request, question_kind):
    Question.validate_kind(question_kind)
    return request.POST['Body']
