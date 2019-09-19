from datetime import date
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from twilio.twiml.messaging_response import MessagingResponse

from textin.models import Question, Responder, Survey
from textin.strings import SurveyStrings
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
    surveys_enum = enumerate(surveys, start=1)

    request.session['active_cookie'] = 'choose_survey'

    if not request.session.get('choose_survey'):
        request.session['choose_survey'] = True
        if not len(surveys):

            return HttpResponse(compose_response(SurveyStrings.no_surveys))
        elif len(surveys) == 1:
            first_survey = surveys.first()
            return redirect('survey', survey_id=first_survey.id)

        return HttpResponse(compose_response(
            SurveyStrings.choose_survey + "\n\n" + SurveyStrings.survey_options(surveys)))

    else:
        survey_num_response = request.POST['Body']
        invalid_survey_message = ""
        try:
            survey_num = int(survey_num_response)
            if survey_num < 1 or survey_num > len(surveys):
                invalid_survey_message = SurveyStrings.invalid_survey_out_of_range(survey_num)
        except ValueError:
            invalid_survey_message = SurveyStrings.invalid_survey_nan(survey_num_response)

        if len(invalid_survey_message):
            return HttpResponse(compose_response(invalid_survey_message))

        del request.session['choose_survey']

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
        twiml_response = compose_response(SurveyStrings.welcome(survey.title))
        twiml_response.redirect(first_question_url, method='GET')
        request.session['active_cookie'] = 'answering_question_id';

    return HttpResponse(twiml_response, content_type='application/xml')
