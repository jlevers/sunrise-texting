from django.views.decorators.csrf import csrf_exempt
from django.urls import include, path

from textin.views.questions import show_question
from textin.views.question_responses import save_response
from textin.views.responders import process_responder, set_responder_attr
from textin.views.surveys import choose_survey, push_survey, show_survey, show_survey_results
from textin.views.surveys import redirects_twilio_request_to_proper_endpoint
from textin.views.surveys import SurveyCreateView, SurveyListView, SurveyUpdateView

app_name = 'textin'
urlpatterns = [
    path('', SurveyListView.as_view(), name='app_root'),
    path('choose-survey/', choose_survey, name='choose_survey'),

    # Responder paths
    path('responder/<int:responder_id>/', csrf_exempt(process_responder), name='process_responder'),
    path('responder/<int:responder_id>/set-attr/', set_responder_attr, name='set_responder_attr'),

    path('sms/', csrf_exempt(redirects_twilio_request_to_proper_endpoint), name='sms'),

    # Survey paths
    path('survey/new/', SurveyCreateView.as_view(), name='survey_new'),
    path('survey/<int:pk>/', show_survey, name='survey'),
    path('survey/<int:pk>/edit/', SurveyUpdateView.as_view(), name='survey_update'),
    path('survey/push/', push_survey, name='push_survey'),
    path('survey/<int:pk>/results/', show_survey_results, name='survey_results'),

    # Question paths
    path('survey/<int:survey_id>/question/<int:question_id>/', show_question, name='question'),
    path('survey/<int:survey_id>/question/<int:question_id>/question-response/',
         csrf_exempt(save_response),
         name='save_response'),
]
