$(document).ready(function() {
  const questionFormClass = '.question-formset-form';
  const totalFormsId = '#id_form-TOTAL_FORMS';
  let numForms = parseInt($(totalFormsId).val());
  let lastForm = loadLastWithSelector(questionFormClass);

  // Remove the hidden ID input field from the extra formset form
  removeHiddenIdField(lastForm);
  // Remove `questionFormClass` so that $(questionFormClass) doesn't select `copyForm`
  const hidden = $(lastForm).clone().removeClass(questionFormClass.substring(1));
  $('#form-template').html(hidden);
  const copyForm = $('#form-template').contents(); // Template form to copy later

  // Add another form to the Question formset
  $('#add-question').click(() => {
    const cloned = $(copyForm).clone()
      .css('display', 'block')
      .addClass(questionFormClass.substring(1))
      .attr('id', 'clone');

    updateAttrs($(cloned), numForms);
    lastForm = loadLastWithSelector(questionFormClass);
    $(lastForm).after(cloned);

    // Update the number of forms in the formset
    numForms++;
    $(totalFormsId).val(numForms);
  });
});

/**
 * Removes any hidden formset input field that contains a Django object ID.
 * @param  {Node} element A form to search for hidden ID inputs.
 * @return {undefined}
 */
const removeHiddenIdField = element => {
  $(element).find('input[id^="id_form-"][id$="-id"]').remove();
}

/**
 * Gets the last element in the DOM matching the selector.
 * @param  {String} selector The jQuery selector to search for
 * @return {Node}            The last element matching `selector`
 */
const loadLastWithSelector = selector => {
  const elements = $(selector);
  return elements[elements.length - 1];
}

/**
 * Updates all Question formset-related element attributes on an element.
 * @param  {Node}    element The element to update
 * @param  {Integer} formNum The index of this form in the formset (0-indexed)
 * @return {undefined}
 */
const updateAttrs = (element, formNum) => {
  const regex = /.*form-(\d)-.*/;
  $($(element).find('.question-header')).text('Question ' + (formNum + 1));
  $(element).find('input').not('[type="hidden"]').each(function() {  // Reset any visible inputs
    $(this).val(null);
  });
  $(element).find('select').prop('selectedIndex', -1);  // Reset select element(s)
  updateAttrsRecur(element, regex, formNum);
}

/**
 * Recursively updates the formset-related attributes of the given element, and its child elements.
 * @param  {Node}    element The element whose attributes need updating
 * @param  {RegExp}  regex   The regex to use to determine if an attribute is formset-related
 * @param  {Integer} formNum The index of this form in the formset (0-indexed)
 * @return {undefined}
 */
const updateAttrsRecur = (element, regex, formNum) => {
  const children = $(element).children();
  if (children.length) {
    // Update attributes of child elements
    children.each((idx, el) => { updateAttrsRecur(el, regex, formNum); });
  }

  if (element.attributes) {
    const attrs = element.attributes;
    for (var i = 0; i < attrs.length; i++) {
      const attr = attrs[i];
      if (attr.nodeValue.match(regex)) {
        $(element).attr(attr.nodeName, attr.nodeValue.replace(/-\d-/, `-${formNum}-`));
      }
    }
  }
}
