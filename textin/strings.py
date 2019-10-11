# This is necessary to initialize strings (which are class variables) that depend on other class variables
def init_with_class_methods(cls):
    cls.class_methods_init()
    return cls

@init_with_class_methods
class SurveyStrings():

    # Predefined user responses
    # The preferred response (i.e., the one we tell them to respond with) should be first in array
    predefined_user_responses = {
        'stop': ["STOP"],
        'skip': ["SKIP"],
        'yes': ["YES", "Y"],
        'no': ["NO", "N"]
    }

    choose_survey = "Please choose the event you're checking into, by responding with the number "\
        "of that event:"
    no_surveys = "There are no surveys available at this time. Sorry!"
    stop_msg = "We will stop contacting you. Sorry for any inconvenience!"
    push_survey_msg = None

    # Any strings that depend on class methods or variables should be set to None above, and then
    # set to their actual value inside this method.
    @classmethod
    def class_methods_init(cls):
        cls.push_survey_msg = f"Please reply with {cls.preferred_response('yes')} to continue, "\
            f"or {cls.preferred_response('stop')} to opt out."

    @classmethod
    def preferred_response(cls, key):
        return cls.predefined_user_responses[key][0]

    @classmethod
    def user_response_matches(cls, user_response, response_type):
        return user_response.upper() in cls.predefined_user_responses[response_type]

    @staticmethod
    def invalid_survey_out_of_range(cls, num):
        return f"{survey_num} does not correspond to one of the available events. "\
            "Please respond with a valid event number:"

    @staticmethod
    def invalid_survey_nan(input):
        return f"{input} is not a number. Please respond with a valid event number:"

    @staticmethod
    def survey_options(surveys):
        return '\n'.join(
            [f'{index}: {survey.title}'
            for index, survey
            in enumerate(surveys, start=1)])

    @staticmethod
    def welcome(survey_name):
        return f"Thanks for texting in to let us know you're at the {survey_name}!"


class QuestionStrings():
    TEXT = None
    YES_NO = f"Please respond with {SurveyStrings.preferred_response('yes')} or \
{SurveyStrings.preferred_response('no')}"
    NUMERIC = "Please respond with a number"


class QuestionResponseStrings():
    already_answered = "You've already answered that question."

    @staticmethod
    def invalid_response(kind):
        return f"Your response to a {kind} question was invalid. Please enter a valid {kind} "\
            "response:"


class ResponderStrings():
    skip_instr = f"To skip any of the following questions, please respond with "\
        f"{SurveyStrings.preferred_response('skip')}."
    new_details_or_skip_instr = "We'd appreciate it if you'd tell us a little bit about yourself."\
        "\n\n" + skip_instr
    existing_details_or_skip_instr = "We're missing some of your contact information. We'd really "\
        "appreciate it if you'd be willing to answer a couple questions to help us best reach you "\
        "in the future.\n\n" + skip_instr
    name_attr_display = "first and last name"
    email_attr_display = "email"

    @staticmethod
    def get_responder_attr(attr):
        return f"What is your {getattr(ResponderStrings, f'{attr}_attr_display')}?"
