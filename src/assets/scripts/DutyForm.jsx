let React = require("react");
let _ = require('underscore');
let api = require('api');
let forms = require('forms');

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
  }
}

module.exports = DutyForm;
