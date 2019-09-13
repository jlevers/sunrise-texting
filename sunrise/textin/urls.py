from django.views.decorators.csrf import csrf_exempt
from django.urls import include, path

from textin.views.surveys import redirects_twilio_request_to_proper_endpoint
from textin.views.surveys import redirect_to_first_results
from textin.views.questions import show_question
from textin.views.surveys import show_survey, show_survey_results
from textin.views.question_responses import save_response

urlpatterns = [
    path('', redirect_to_first_results, name='app_root'),
    path('survey/<int:survey_id>/', show_survey, name='survey'),
    path('survey/<int:survey_id>/results/', show_survey_results, name='survey_results'),
    path('first-survey/',
         csrf_exempt(redirects_twilio_request_to_proper_endpoint),
         name='first_survey'),
    path('survey/<int:survey_id>/question/<int:question_id>/', show_question, name='question'),
    path('survey/<int:survey_id>/question/<int:question_id>/question-response/',
         csrf_exempt(save_response),
         name='save_response')
]
