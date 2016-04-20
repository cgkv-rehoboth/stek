import React, {Component, PropTypes} from "react";
import ReactDom from "react-dom";
import * as qs from 'querystring';
import api from "api";
import moment from 'moment';
import { Link, IndexRoute, Router, Route, hashHistory } from 'react-router';
import Calendar from 'containers/Calendar';
import EventForm from 'containers/EventForm';
import Overlay from 'bootstrap/Overlay';

class AddEventOverlay extends Component {
  
  render() {
    let {day} = this.props.params;
    var daym= moment.unix(day);
    if(!daym.isValid()) {
      daym = moment();
    }

    let close = () => hashHistory.push('/');

    return <Overlay width="30%" onClose={close}>
      <h2>Nieuw</h2>
      <EventForm day={daym} onSuccess={close} />
    </Overlay>;
  }
}

class CalendarPage extends Component {

  render() {
    let onMonthChange = (year, month) => {
      let from = moment([year, month]);
      let to = from.clone().add(1, 'months');

      return api.events.list(from.unix(), to.unix());
    };

    let {query} = this.props.location;
    var focus = query && query.year
      ? moment([query.year, query.month || 0, 1])
      : moment();

    // default on invalid parameters
    if(!focus.isValid()) {focus = moment();}

    return <div>
      <Calendar tables={[]}
        onMonthChange={onMonthChange}
        onAddEvent={(day) => hashHistory.push(`/nieuw/${day.unix()}`)}
        initFocus={focus} />
      {this.props.children}
    </div>;
  }
}

export default function calendarMain() {

  let router = <Router history={hashHistory}>
    <Route path="/" component={CalendarPage}>
      <IndexRoute />
      <Route path="nieuw/:day" component={AddEventOverlay} />
    </Route>
  </Router>;
  

  ReactDom.render(router, $("#calendar")[0]);
};
