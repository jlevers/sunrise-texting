$(document).ready(function() {
  const questionFormClass = '.question-formset-form';
  let numForms = parseInt($('#id_form-TOTAL_FORMS').val());
  let lastForm = loadLastForm(questionFormClass);

  removeHiddenIdField(lastForm);  // Remove the hidden ID input field from the extra (last) form
  // Remove `questionFormClass` so that $(questionFormClass) doesn't select `copyForm`
  const hidden = $(lastForm).clone().removeClass(questionFormClass.substring(1));
  $('#form-template').html(hidden);
  const copyForm = $('#form-template').contents(); // Template form to copy later

  $('#add-question').click(function() {
    const cloned = $(copyForm).clone()
      .css('display', 'block')
      .addClass(questionFormClass.substring(1))
      .attr('id', 'clone');

    updateAttrs($(cloned), numForms);
    lastForm = loadLastForm(questionFormClass);
    $(lastForm).after(cloned);
    numForms++;
  });
});

const removeHiddenIdField = element => {
  $(element).find('input[id^="id_form-"][id$="-id"]').remove();
}

const loadLastForm = formClass => {
  const forms = $(formClass);
  return forms[forms.length - 1];
}

const updateAttrs = (element, numForms) => {
  const regex = /.*form-(\d)-.*/;
  $($(element).find('.question-header')).text('Question ' + (numForms + 1));
  $(element).find('input').not('[type="hidden"]').each(function() {  // Reset any visible inputs
    $(this).val(null);
  });
  $(element).find('select').prop('selectedIndex', -1);  // Reset select element(s)
  updateAttrsRecur(element, regex, numForms);
}

const updateAttrsRecur = (element, regex, numForms) => {
  const children = $(element).children();
  if (children.length) {
    // Update attributes of child elements
    children.each((idx, el) => { updateAttrsRecur(el, regex, numForms); });
  }

  if (element.attributes) {
    const attrs = element.attributes;
    for (var i = 0; i < attrs.length; i++) {
      const attr = attrs[i];
      if (attr.nodeValue.match(regex)) {
        $(element).attr(attr.nodeName, attr.nodeValue.replace(/-\d-/, `-${numForms}-`));
      }
    }
  }
}
