let React = require("react");
let _ = require('underscore');
let api = require('api');
import * as forms from 'bootstrap/forms';

class DutyForm extends React.Component {

  static get propTypes() {
    return {
      timetable: React.PropTypes.number.isRequired
    };
  }

  render() {
    let handleSubmit = (data) => {
      data = _.extend(data, {
        timetable: this.props.timetable
      });

      api
        .duties
        .create(data)
        .catch((resp) => console.error(resp.data))
        .then(() =>
          // clear the form to prevent resubmit
          this.refs.dutyForm.clear()
        )
        .done();
    };

    let formBuilder = () => {
      return (
        <div className="duty-form">
          <forms.TextField name="event" />
          <forms.TextField name="responsible" />
          <forms.TextField name="comment" />
          <br />
          <forms.SubmitButton />
        </div>
      );
    };

    return <forms.Form ref="dutyForm" formBuilder={formBuilder} onSubmit={handleSubmit} />;

    /*
    * Volgens mij werkt dit hieronder wel en dat hierboven niet:
    *
    let formBuilder = (
        <div className="duty-form">
          <forms.SelectField name="event">

          </forms.SelectField>
          <forms.SelectField name="responsible">
            <option value="1">1</option>
            <option value="2">2</option>
          </forms.SelectField>
          <forms.TextField name="comment" />
          <br />
          <forms.SubmitButton />
        </div>
      );

    return <forms.Form ref="dutyForm" onSubmit={handleSubmit}>{formBuilder}</forms.Form>;
    */
  }
}

module.exports = DutyForm;
