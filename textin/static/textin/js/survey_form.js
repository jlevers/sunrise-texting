$(document).ready(function() {
  $('#add-question').click(function() {
    const formset = $('.question-formset-form');
    const lastForm = $(formset[formset.length - 1]);
    const cloned = lastForm.clone();
    updateAttrs(cloned);
    lastForm.after(cloned);
  });
});

const updateAttrs = element => {
  const regex = /.*form-(\d)-.*/;
  const totalFormsId = '#id_form-TOTAL_FORMS';
  const numForms = parseInt($(totalFormsId).attr('value'));
  $(totalFormsId).attr('value', numForms + 1);  // Increment management form's TOTAL_FORMS count

  $(element).find('.question-header').text('Question ' + (numForms + 1));
  $(element).find('input').not('[type="hidden"]').each(function() {  // Reset any visible inputs
    $(this).val(null);
  });
  $(element).find('select').prop('selectedIndex', -1);  // Reset select element(s)
  $(element).find(`#id_form-${numForms - 1}-id`).remove(); // Remove hidden ID input, if it exists
  updateAttrsRecur(element, regex, numForms);
}

const updateAttrsRecur = (element, regex, numForms) => {
  const children = $(element).children();
  if (children.length) {
    // Update attributes of child elements
    children.each((idx, el) => { updateAttrsRecur(el, regex, numForms); });
  }

  const attrs = $(element)[0].attributes;
  for (var i = 0; i < attrs.length; i++) {
    const attr = attrs[i];
    if (attr.nodeValue.match(regex)) {
      $(element).attr(attr.nodeName, attr.nodeValue.replace(/-\d-/, `-${numForms}-`));
    }
  }
}
