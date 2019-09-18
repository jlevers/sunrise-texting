from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse

from textin.models import Responder, Survey
from textin.util import compose_response

@csrf_exempt
def process_responder(request, responder_id):
    responder = Responder.objects.get(id=responder_id)
    request.session['active_cookie'] = 'responder_id'
    request.session['responder_id'] = responder_id

    skip_howto_message = """
    We'd appreciate it if you'd tell us a little bit about yourself.
To skip any of the following questions, please respond with SKIP.
    """
    twiml_response = compose_response(skip_howto_message)

    request.session['responder_attr'] = Responder.USER_SET_ATTRS[0]
    responder_setup_url = reverse('set_responder_attr', kwargs={'responder_id': responder.id})
    twiml_response.redirect(responder_setup_url, method='GET')
    return HttpResponse(twiml_response)


@csrf_exempt
def set_responder_attr(request, responder_id):
    if request.method == 'GET':
        attr = request.session['responder_attr']
        return HttpResponse(compose_response("What is your %s?" % attr))
    elif request.method == 'POST':
        responder = Responder.objects.get(id=responder_id)
        attr = request.session['responder_attr']
        value = request.POST['Body']

        if value != 'SKIP':
            setattr(responder, request.session['responder_attr'], value)
            responder.save()

        if attr == Responder.USER_SET_ATTRS[-1]:
            del request.session['responder_attr']
            return redirect('survey', survey_id=responder.surveys.all()[0].id)
        else:
            next_attr = Responder.USER_SET_ATTRS[Responder.USER_SET_ATTRS.index(attr) + 1]
            request.session['responder_attr'] = next_attr
            next_attr_url = reverse('set_responder_attr', kwargs={'responder_id': responder.id})
            twiml_response = MessagingResponse()
            twiml_response.redirect(next_attr_url, method='GET')

            return HttpResponse(twiml_response)
