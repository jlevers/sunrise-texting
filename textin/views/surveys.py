from datetime import date
import logging
import time

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic.list import ListView
from twilio.twiml.messaging_response import MessagingResponse

from sunrise.settings.common import TWILIO_NOTIFY_SERVICE_SID
from textin.forms import QuestionFormSet, SurveyForm
from textin.models import Question, Responder, Survey
from textin.strings import SurveyStrings
from textin.util import compose_response, get_twilio_client


logger = logging.getLogger(__name__)


class SurveyListView(ListView):
    model = Survey
    context_object_name = 'surveys'


class CreateUpdateSurveyMixin(FormView):
    model = Survey
    form_class = SurveyForm
    template_name = 'textin/survey_form.html'

    def post(self, request, *args, **kwargs):
        above = super().post(request, *args, **kwargs)
        question_formset = QuestionFormSet(request.POST)

        if question_formset.is_valid():
            for form in question_formset:
                if form.cleaned_data != {}:
                    question = form.save(commit=False)
                    question.survey = self.object
                    question.save()
            return above
        else:
            context = {
                'form': SurveyForm(request.POST),
                'question_formset': question_formset,
                'verb': self.verb
            }
            return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        questions = Question.objects.filter(survey=self.object)
        question_formset = QuestionFormSet(queryset=questions)
        context['question_formset'] = question_formset
        context['verb'] = self.verb if self.verb else 'Update'
        return context


class SurveyCreateView(CreateUpdateSurveyMixin, CreateView):
    verb = 'Create'

    def get_success_url(self):
        return reverse('textin:app_root')

class SurveyUpdateView(CreateUpdateSurveyMixin, UpdateView):
    verb = 'Update'

    def get_success_url(self):
        return reverse('textin:survey_update', kwargs={'pk': self.object.id})


@require_POST
def push_survey(request):
    logger.debug("Starting survey push process")
    survey = Survey.objects.get(id=int(request.POST['pk']))
    if not survey.followup:
        return HttpResponse("This survey must be initiated by the user.")
    elif survey.pushed:
        return HttpResponse("This survey has already been started.")

    last_survey_responders = Responder.objects.filter(surveys__id__exact=survey.followup.id)

    logger.info("Adding survey #%d to all responders to survey #%d, which #%d is following up on", survey.id, survey.followup.id, survey.id)

    # This is problematic if we plan on having responders take multiple surveys in close succession
    # TODO: Fix this to work with Responder profile questions
    last_survey_responders.update(active_question=survey.first_question)

    client = get_twilio_client()
    logger.info("Pushing survey #%s...", survey.id)
    for responder in last_survey_responders:

        client.messages.create(
            body=survey.first_message,
            from_=TWILIO_MESSAGING_SERVICE,
            to=responder.phone_number
        )
        # Twilio limits long phone numbers to 1 message per second. We only have one phone number at
        # the moment, but if we buy more phone numbers, this should be changed to reflect that.
        # They recommend sending a max of 200 messages to unique numbers from a single long number
        # in a day. We've hugely exceeded that (3k+ messages with one number in a day), so for the
        # next big event we might need to rethink that. More details here:
        # https://www.twilio.com/blog/twilio-messaging-service-copilot-features
        time.sleep(1)
    logger.info("Done pushing survey #%s", survey.id)

    return redirect()


@require_POST
def redirects_twilio_request_to_proper_endpoint(request):
    active_cookie = request.session.get('active_cookie')
    active_cookie_val = request.session.get(active_cookie)

    if not active_cookie or active_cookie == 'choose_survey':
        return redirect('textin:choose_survey')
    elif active_cookie == 'responder_id':
        responder = Responder.objects.get(id=int(active_cookie_val))
        return redirect('textin:set_responder_attr', responder_id=responder.id)
    elif active_cookie == 'answering_question_id':
        if not active_cookie_val:
            first_survey = Survey.objects.first()
            return redirect('textin:survey', survey_id=first_survey.id)
        else:
            question = Question.objects.get(id=active_cookie_val)
            return redirect('textin:save_response',
                            survey_id=question.survey.id,
                            question_id=question.id)


@csrf_exempt
def choose_survey(request):
    surveys = Survey.objects.filter(start_date__lte=date.today(), end_date__gte=date.today())
    surveys_enum = enumerate(surveys, start=1)

    request.session['active_cookie'] = 'choose_survey'

    if not request.session.get('choose_survey'):
        request.session['choose_survey'] = True
        if not len(surveys):
            return HttpResponse(compose_response(SurveyStrings.no_surveys))
        elif len(surveys) == 1:  # If there's only one active survey
            first_survey = surveys.first()
            twiml_response = compose_response(first_survey.first_message)
            survey_params = {'survey_id': first_survey.id}
            twiml_response.redirect(reverse('textin:survey', kwargs=survey_params), method='POST')
            return HttpResponse(twiml_response)
        else:  # If there are multiple active surveys
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
        twiml_response = compose_response(survey.first_message)
        survey_params = {'survey_id': survey.id}
        twiml_response.redirect(reverse('textin:survey', kwargs=survey_params), method='POST')
        return HttpResponse(twiml_response)


@csrf_exempt
def show_survey(request, pk):
    survey = Survey.objects.get(id=pk)
    request.session['current_survey_id'] = survey.id
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
    first_question_url = reverse('textin:question', kwargs=first_question_ids)

    # If this is a new Responder, or an old Responder with missing data (email or name) that we want
    # them to complete
    if new_responder or survey.complete_responder:
        responder_params = {'responder_id': responder.id, 'new_responder': new_responder }
        new_responder_url = reverse('textin:process_responder', kwargs=responder_params)
        twiml_response = MessagingResponse()

        if survey.start_message:
            twiml_response.message(survey.start_message)

        twiml_response.redirect(new_responder_url, method='GET')
        return HttpResponse(twiml_response, content_type='application/xml')
    else:
        request.session['active_cookie'] = 'answering_question_id';
        return redirect(first_question_url)


@require_GET
def show_survey_results(request, pk):
    survey = Survey.objects.get(id=pk)
    responses_to_render = [response.as_dict() for response in survey.responses]

    context = {
        'responses': responses_to_render,
        'survey_title': survey.title
    }
    return render(request, 'polls/results.html', context)
