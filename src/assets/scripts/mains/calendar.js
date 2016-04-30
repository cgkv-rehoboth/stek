import React, {Component, PropTypes} from "react";
import ReactDom from "react-dom";
import * as qs from 'querystring';
import api from "api";
import moment from 'moment';
import { Link, IndexRoute, Router, Route, hashHistory } from 'react-router';
import Calendar from 'containers/Calendar';
import EventForm from 'containers/EventForm';
import Overlay from 'bootstrap/Overlay';
import Async from 'containers/Async';

class AddEventOverlay extends Component {
  
  render() {
    let {day} = this.props.params;
    var daym= moment.unix(day);
    if(!daym.isValid()) {
      daym = moment();
    }

    let close = () => hashHistory.push('/');

    return <Overlay width="30%" minWidth={600} onClose={close}>
      <h2>Nieuw</h2>
      <EventForm day={daym} onSuccess={close} />
    </Overlay>;
  }
}

class EventDetail extends Component {
  
  static get propTypes() {
    return {
      event: PropTypes.object.isRequired
    };
  }

  render() {
    let {event} = this.props;
    const FMT = "D MMM YYYY hh:mm"

    return <div>
      <h4>{moment(event.startdatetime).format(FMT)}-
          {moment(event.enddatetime).format(FMT)}</h4>
      <h2>{event.title}</h2>
      <p>{event.description}</p>
    </div>;
  }
}

class EventDetailOverlay extends Component {
  
  render() {
    let {id} = this.props.params;
    let close = () => hashHistory.push('/');

    return <Overlay width="30%" minWidth={600} onClose={close}>
      <Async promise={api.events.get(id).then((resp) => resp.data)}
        then={(e) => <EventDetail event={e} />}
      />
    </Overlay>
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
      <Route path="event/:id" component={EventDetailOverlay} />
    </Route>
  </Router>;
  

  ReactDom.render(router, $("#calendar")[0]);
};
