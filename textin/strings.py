class QuestionStrings():
    TEXT = None
    YES_NO = "Please respond with \"Yes\" or \"No\""
    NUMERIC = "Please respond with a number"


class QuestionResponseStrings():
    already_answered = "You've already answered that question."

    @staticmethod
    def invalid_response(kind):
        return f"Your response to a {kind} question was invalid. Please enter a valid {kind}\
response:"


class ResponderStrings():
    new_responder_details_title = "Responder details (INTERNAL)"
    update_responder_details_title = "Responder details update (INTERNAL)"
    skip_instr = "To skip any of the following questions, please respond with SKIP."
    new_details_or_skip_instr = "We'd appreciate it if you'd tell us a little bit about yourself.\
\n\n" + skip_instr
    existing_details_or_skip_instr = "We're missing some of your contact information. We'd really\
appreciate it if you'd be willing to answer a question or two that would help us best reach you in\
the future.\n\n" + skip_instr
    name_attr_display = "first and last name"
    email_attr_display = "email"

    @staticmethod
    def get_responder_attr(attr):
        return f"What is your {getattr(ResponderStrings, f'{attr}_attr_display')}?"


class SurveyStrings():
    choose_survey = "Please choose the event you're checking into, by responding with the number \
of that event:"
    no_surveys = "There are no surveys available at this time. Sorry!"

    @staticmethod
    def invalid_survey_out_of_range(cls, num):
        return f'{survey_num} does not correspond to one of the available events.\
                                  Please respond with a valid event number:'

    @staticmethod
    def invalid_survey_nan(input):
        return f'{input} is not a number. Please respond with a valid event number:'

    @staticmethod
    def survey_options(surveys):
        return "\n".join(
            [f'{index}: {survey.title}'
            for index, survey
            in enumerate(surveys, start=1)])

    @staticmethod
    def welcome(survey_name):
        return f"Thanks for texting in to let us know you're at the {survey_name}!"
