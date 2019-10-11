from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse

from textin.models import Responder, Survey
from textin.strings import ResponderStrings, SurveyStrings
from textin.util import compose_response, create_get_param_string

@csrf_exempt
def process_responder(request, responder_id):
    responder = Responder.objects.get(id=responder_id)
    request.session['active_cookie'] = 'responder_id'
    request.session['responder_id'] = responder_id

    msg = ResponderStrings.existing_details_or_skip_instr
    new_responder = False
    if 'new' in request.GET:
        new_responder = True
        msg = ResponderStrings.new_details_or_skip_instr
    twiml_response = compose_response(msg)

    request.session['responder_attr'] = Responder.USER_SET_ATTRS[0]
    responder_setup_url = reverse('textin:set_responder_attr',
                                  kwargs={'responder_id': responder.id})
    twiml_response.redirect(responder_setup_url, method='GET')
    return HttpResponse(twiml_response)


@csrf_exempt
def set_responder_attr(request, responder_id):
    responder = Responder.objects.get(id=responder_id)
    active_survey = responder.active_survey
    if request.method == 'GET':
        attr = request.session['responder_attr']

        if getattr(responder, attr):
            if attr != Responder.USER_SET_ATTRS[-1]:
                phone_number = create_get_param_string({'From': request.GET['From']})
                return redirect(reverse('textin:survey', kwargs={'pk': active_survey.id}) + \
                    phone_number)
            attr = Responder.USER_SET_ATTRS[Responder.USER_SET_ATTRS.index(attr) + 1]

        return HttpResponse(compose_response(ResponderStrings.get_responder_attr(attr)))
    elif request.method == 'POST':
        attr = request.session['responder_attr']
        value = request.POST['Body']

        print('responder id: ', responder.id)
        print('attr cookie: ', request.session['responder_attr'])
        print('value: ', value)
        print('usr response match: ', SurveyStrings.user_response_matches(value, 'skip'))

        if not SurveyStrings.user_response_matches(value, 'skip'):
            setattr(responder, request.session['responder_attr'], value)
            responder.save()

        if attr == Responder.USER_SET_ATTRS[-1]:
            del request.session['responder_attr']
            phone_number = create_get_param_string({'From': request.POST['From']})
            return redirect(reverse('textin:survey', kwargs={'pk': active_survey.id}) + \
                phone_number)
        else:
            next_attr = Responder.USER_SET_ATTRS[Responder.USER_SET_ATTRS.index(attr) + 1]
            request.session['responder_attr'] = next_attr
            next_attr_url = reverse('textin:set_responder_attr', kwargs={'responder_id': responder.id})
            twiml_response = MessagingResponse()
            twiml_response.redirect(next_attr_url, method='GET')

            return HttpResponse(twiml_response)
