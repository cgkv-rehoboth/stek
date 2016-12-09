import * as http from 'utils/http';
import $ from 'jquery';
import _ from 'underscore';

function clearErrors($form) {
  $form.find('input, .input-group').removeClass('faulty');
}

export default function initAsyncForm(formElem, onSuccess=(() => {})) {
  let $form = $(formElem);
  let url = $form.attr('action');
  let $errors = $('.errors', $form);
  let $inputs = $('input, textarea, select', $form).filter('[name]');

  $form.submit(() => {
    // collect the data from the form
    let data = {};
    $inputs.each(function() {
      let self = $(this);
      if(self.attr('name') !== undefined) {
        data[self.attr('name')] = self.val();
      }
    });

    // submit the json data to the endoint
    http
      .post(url, data)
      .then((resp) => {
        console.log("Succesfully submitted form: ", resp.data);

        // clear the form
        clearErrors($form);
        $inputs.val('');

        onSuccess(resp);

        return resp;
      })
      .catch((resp) => {
        let errors = resp.data;

        // make sure we don't ruin everything if the dom is not formatted
        // properly and this runs into problems
        try {
          clearErrors($form);

          // mark the inputs that are faulty
          _.each(errors, (err, key) => {
            let $faulty_input = $inputs.filter(`[name=${key}]`);
            let $group = $faulty_input.closest('.input-group');
            if($group.length > 0) {
              $group.addClass('faulty');
            } else {
              $faulty_input.addClass('faulty');
            }
          });
        } catch(err) {
          console.error("Error trying to mark erroneous form fields");
        }
      });

    return false;
  });
}
