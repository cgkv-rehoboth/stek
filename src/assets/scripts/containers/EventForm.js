import React, {Component, PropTypes} from 'react';
import moment from 'moment';
import moment_range from 'moment-range';
import _ from 'underscore';
import cn from 'classnames';
import api from 'api';

import Icon from "bootstrap/Icon";
import * as forms from 'bootstrap/forms';
import Async from 'containers/Async';

function loadTimetables() {
  return api.timetables
    .list(true)
    .then(resp => resp.data);
}

class EventForm extends Component {
  static get propTypes() {
    return {
      day: PropTypes.object.isRequired,
      timetables: PropTypes.array.isRequired
    };
  }

  render() {
    let {day, timetables} = this.props;
    let start = day.clone();
    let options = _.map(timetables, (table) => <option value={table.title}>{table.title}</option>);

    return (
      <forms.Form action={api.events.add}>
        <div className="row">
          <div className="col-md-6 col-md-offset-3 text-center">
            <h2>Nieuw Agenda item</h2>
            <forms.CharField name="title" label="Titel" />
          </div>
        </div>
        <div className="row">
          <div className="col-md-3 col-md-offset-3">
            <forms.DateTimeField initial={start} name="start_datetime" label="Start om" />
          </div>
          <div className="col-md-3">
            <forms.DateTimeField initial={start.clone().add(1, 'hours')} name="end_datetime" label="Eindigt om" />
          </div>
        </div>
        <div className="row">
          <div className="col-md-6 col-md-offset-3 text-center">
            <forms.SelectField name="timetable" label="Agenda">
              {options}
            </forms.SelectField>
          </div>
        </div>
        <div className="vspace"></div>
        <div className="row">
          <div className="col-md-6 col-md-offset-3">
            <forms.TextField name="description" label="Beschrijving" />
          </div>
        </div>
        <div className="row">
          <div className="col-md-6 col-md-offset-3">
            <forms.SubmitButton label="Voeg toe"/>
          </div>
        </div>
      </forms.Form>
    );
  }
}

export default function (props) {
  return <Async
    promise={loadTimetables()}
    then={(tables) => <EventForm {...props} timetables={tables} />}
  />;
}
