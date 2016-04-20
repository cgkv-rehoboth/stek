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
      timetables: PropTypes.array.isRequired,
      onSuccess: PropTypes.func.isRequired
    };
  }

  render() {
    let {day, timetables, onSuccess} = this.props;
    let start = day.clone();
    let options = _.map(timetables, (table) =>
                        <option key={table.id} value={table.id}>{table.title}</option>);

    // select an initial timetable
    let initialTable;
    if(timetables.length > 0) {
      initialTable = timetables[0].id;
    } else {
      initialTable = undefined;
    }

    return (
      <forms.Form action={api.events.add} onSuccess={onSuccess}>
        <div className="row">
          <div className="col-md-12 text-center">
            <forms.CharField name="title" label="Titel" />
          </div>
        </div>
        <div className="row">
          <div className="col-md-6">
            <forms.DateTimeField initial={start} name="startdatetime" label="Start om" />
          </div>
          <div className="col-md-6">
            <forms.DateTimeField initial={start.clone().add(1, 'hours')} name="enddatetime" label="Eindigt om" />
          </div>
        </div>
        <div className="row">
          <div className="col-md-12 text-center">
            <forms.SelectField initial={initialTable} name="timetable" label="Agenda">
              {options}
            </forms.SelectField>
          </div>
        </div>
        <div className="vspace"></div>
        <div className="row">
          <div className="col-md-12">
            <forms.TextField name="description" label="Beschrijving" />
          </div>
        </div>
        <div className="row">
          <div className="col-md-12">
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
