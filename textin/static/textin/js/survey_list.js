$(document).ready(function() {
  $('.push-survey:enabled').click(function(event) {
    event.preventDefault();
    const surveyId = event.target.dataset.surveyId;
    const csrfToken = getCookie('csrftoken');
    $.ajax({
      type: 'GET',
      url: PUSH_SURVEY_TEMPLATE_URL.replace(/\d/, surveyId),
      data: JSON.stringify({ pk: surveyId }),
      dataType: 'json',
    }).done(data => {
      $(event.target)
        .prop('disabled', true)
        .removeAttr('data-survey-id')
        .removeAttr('type')
        .addClass('btn-success')
        .text('Sent')
        .append(`<span class="pushed">&nbsp;&nbsp;${PUSH_SUCCESS_ICON}</span>`);
    }).fail((request, err) => {
      $(event.target)
        .addClass('btn-danger')
        .text('Send')
        .append(`<span class="push-failed">&nbsp;&nbsp;${PUSH_FAILURE_ICON}</span>`);
    });
  });
});
