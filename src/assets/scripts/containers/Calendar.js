import React, {Component, PropTypes} from 'react';
import moment from 'moment';
import moment_range from 'moment-range';
import _ from 'underscore';
import cn from 'classnames';
import api from 'api';
import * as qs from 'querystring';

import Icon from "bootstrap/Icon";
import * as forms from 'bootstrap/forms';

export function generateCalendar(yearno, monthno, f) {
  let month_start = moment([yearno, monthno, 1]);
  let month_end = month_start.clone().endOf("month");
  let start_fill = parseInt(month_start.format("d")) % 6;
  let end_fill = (6-parseInt(month_end.format("d"))) % 6;
  let month = moment.range(
    month_start.subtract(start_fill, 'days'),
    month_end.add(end_fill, 'days')
  );

  let days = [];

  month.by("days", (day) => {
    days.push(f(day));
  });

  return days;
}

class CalEvent extends React.Component {
  static get propTypes() {
    return {
      event: React.PropTypes.object.isRequired,
      day: React.PropTypes.object.isRequired
    };
  }

  eventTimeRange() {
    return moment
      .range(moment(this.props.event.startdatetime), moment(this.props.event.enddatetime))
      .intersect(
        moment.range(
          this.props.day.clone().startOf('day'),
          this.props.day.clone().endOf('day')));
  }

  render() {
    let {event} = this.props;
    let eventTime = this.eventTimeRange();
    return <li className="cal-event" style={{backgroundColor: `#${event.timetable_info.color}`}}>
      <span className="cal-event-timing">
        {eventTime.start.format("HH:mm")}
      </span>
      <span className="cal-event-title">{this.props.event.title}</span>
    </li>;
  }
}

class CalDay extends React.Component {
  static get propTypes() {
    return {
      day: React.PropTypes.object.isRequired,
      events: React.PropTypes.array,
      focus: React.PropTypes.bool,
      addEvent: React.PropTypes.func.isRequired
    };
  }

  static get defaultProps() {
    return {
      events: [],
      focus: false
    };
  }

  render() {
    let { addEvent, day } = this.props;
    let clz = cn('cal-day', {
      focus: this.props.focus,
      hoverable: this.props.events.length != 0
    });

    return <td className={clz}>
      <div className="content">
      <ul>
      {
        _.map(this.props.events, (event, i) => 
          <CalEvent key={i} event={event} day={day.clone()} />
        )
      }
      </ul>
      <button
        className="add-event btn btn-circle tiny black"
        onClick={() => addEvent(day)}
        ><Icon name="plus" /></button>
      </div>
    </td>;
  }
}

class CalMonth extends React.Component {
  static get propTypes() {
    return {
      month: React.PropTypes.number.isRequired, // 1-12
      year: React.PropTypes.number.isRequired,
      addEvent: React.PropTypes.func.isRequired
    };
  }
  
  render() {
    let { year, month } = this.props;
    let today = moment().format("YYYY-DDD");

    let days = generateCalendar(year, month, (day) => {
      let key = day.format("DDDD");
      if(day.month() == month) {
        let focus = day.format("YYYY-DDD") == today;
        let dayOfMonth = day.format("D");
        return <CalDay
          focus={focus}
          addEvent={this.props.addEvent}
          key={key}
          day={day.clone()}
          events={this.props.events[dayOfMonth] || []}></CalDay>;
      } else {
        return <td className="cal-day" key={key}><div className="content"></div></td>;
      }
    });

    let days_by_week = _.groupBy(days, (x, i) => Math.floor(i / 7));

    return <table className="calendar-table">
      <tbody>
        { _.map(days_by_week, (days, i) => <tr key={i}>{days}</tr>) }
      </tbody>
    </table>;
  }
}

export default class Calendar extends Component {
  static get propTypes() {
    return {
      initFocus: React.PropTypes.object,
      onMonthChange: React.PropTypes.func,
      onAddEvent: PropTypes.func
    };
  }

  static get defaultProps() {
    return {
      initFocus: moment(),
      onMonthChange: () => {}
    };
  }

  constructor(props) {
    super(props);
    this.state = {
      year: this.props.initFocus.year(),
      month: this.props.initFocus.month(),
      events: {}
    };

  }

  loadEvents(year, month) {
    this.props
      .onMonthChange(year, month)
      .then((resp) => this.handleEvents(resp.data));
  }

  handleEvents(events) {
    let eventsByDay = {};
    _.each(events, (event) => {
      moment
        .range(moment(event.startdatetime), moment(event.enddatetime))
        .by('days', (day) => {
          let key = moment(day).format("D");
          let evs = (eventsByDay[key] || []);
          evs.push(event);
          eventsByDay[key] = evs;
        });
    });

    this.setState({ events: eventsByDay });
  }

  componentWillMount() {
    this.loadEvents(this.month().year(), this.month().month());
  }

  prevMonth() {
    let prev = this.month().subtract(1, 'months');
    this.setState({
      year: prev.year(),
      month: prev.month(),
      events: {}
    });

    this.loadEvents(prev.year(), prev.month());
  }

  nextMonth() {
    let next = this.month().add(1, 'months');
    this.setState({
      year: next.year(),
      month: next.month(),
      events: {}
    });

    this.loadEvents(next.year(), next.month());
  }

  month() {
    return moment([this.state.year, this.state.month]);
  }

  addEvent(day) {
    // set the default time
    day.hour(12);
    day.minute(0);
    this.props.onAddEvent(day);
  }

  render() {
    let {showEventForm, eventFormDate} = this.state;

    let onCancel = () => this.setState({ showEventForm: false });

    return <div className="calendar">
      <div className="calendar-head">
        <div>
          <p className="calendar-month">{this.month().format("MMMM")}</p>
          <p className="calendar-year">{this.month().format("YYYY")}</p>
        </div>
        <span className="prev btn" onClick={this.prevMonth.bind(this)}>
          <i className="fa fa-chevron-left"></i>
        </span>
        <span className="next btn" onClick={this.nextMonth.bind(this)}>
          <i className="fa fa-chevron-right"></i>
        </span >
      </div>

      { showEventForm
          ? <EventForm day={eventFormDate} onCancel={onCancel}/>
          : <CalMonth
              events={this.state.events}
              addEvent={this.addEvent.bind(this)}
              month={this.state.month}
              year={this.state.year} /> }
    </div>;
  }
}
