from datetime import date
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from twilio.twiml.messaging_response import MessagingResponse

from textin.models import Question, Responder, Survey
from textin.util import compose_response


@require_GET
def show_survey_results(request, survey_id):
    survey = Survey.objects.get(id=survey_id)
    responses_to_render = [response.as_dict() for response in survey.responses]

    template_context = {
        'responses': responses_to_render,
        'survey_title': survey.title
    }

    return render(request, 'results.html', context=template_context)


@require_POST
def redirects_twilio_request_to_proper_endpoint(request):
    active_cookie = request.session.get('active_cookie')
    active_cookie_val = request.session.get(active_cookie)

    if not active_cookie or active_cookie == 'choose_survey':
        return redirect('choose_survey')
    elif active_cookie == 'responder_id':
        responder = Responder.objects.get(id=int(active_cookie_val))
        return redirect('set_responder_attr', responder_id=responder.id)
    elif active_cookie == 'answering_question_id':
        if not active_cookie_val:
            first_survey = Survey.objects.first()
            return redirect('survey', survey_id=first_survey.id)
        else:
            question = Question.objects.get(id=active_cookie_val)
            return redirect('save_response',
                            survey_id=question.survey.id,
                            question_id=question.id)


@require_GET
def redirect_to_first_results(request):
    first_survey = Survey.objects.first()
    return redirect('survey_results', survey_id=first_survey.id)


@csrf_exempt
def choose_survey(request):
    surveys = Survey.objects.filter(start_date__lte=date.today(), end_date__gte=date.today())
    surveys_enum = enumerate(surveys)

    request.session['active_cookie'] = 'choose_survey'

    if not request.session.get('choose_survey'):
        request.session['choose_survey'] = True
        if not len(surveys):
            no_surveys_msg = "There are no surveys available at this time. Sorry!"
            return HttpResponse(compose_response(no_surveys_msg))
        elif len(surveys) == 1:
            first_survey = surveys.first()
            return redirect('survey', survey_id=first_survey.id)

        choose_message = "Please choose the event you're checking into, by responding with the number of that event:"
        options_message = "\n".join(["%f: %s" % (index + 1, survey.title) for index, survey in surveys_enum])
        return HttpResponse(compose_response(choose_message + "\n\n" + options_message))

    else:
        survey_num_response = request.POST['Body']
        invalid_survey_message = ""
        try:
            survey_num = int(survey_num_response)
            if survey_num < 1 or survey_num > len(surveys_enum):
                invalid_survey_message = "%s does not correspond to one of the available events.\
                                          Please respond with a valid event number:" % survey_num
        except ValueError:
            invalid_survey_message = "%s is not a number. Please respond with a valid event number:" % survey_num_response

        if len(invalid_survey_message):
            return HttpResponse(compose_response(invalid_survey_message))

        del session['choose_survey']

        survey = surveys[survey_num - 1]
        return redirect('survey', survey_id=survey.id)


@csrf_exempt
def show_survey(request, survey_id):
    survey = Survey.objects.get(id=survey_id)
    phone_number = request.POST['From']
    new_responder = False

    try:
        responder = Responder.objects.get(phone_number=phone_number)
    except Responder.DoesNotExist:
        responder = Responder(phone_number=phone_number)
        responder.save()
        new_responder = True

    responder.surveys.add(survey)

    first_question = survey.first_question
    first_question_ids = {
        'survey_id': survey.id,
        'question_id': first_question.id
    }
    first_question_url = reverse('question', kwargs=first_question_ids)

    if new_responder:  # If this is a new Responder
        new_responder_url = reverse('process_responder', kwargs={'responder_id': responder.id})
        twiml_response = MessagingResponse()
        twiml_response.redirect(new_responder_url, method='GET')
    else:
        welcome = "Thanks for texting in to let us know you're at the %s!" % survey.title
        twiml_response = compose_response(welcome)
        twiml_response.redirect(first_question_url, method='GET')
        request.session['active_cookie'] = 'answering_question_id';

    return HttpResponse(twiml_response, content_type='application/xml')
