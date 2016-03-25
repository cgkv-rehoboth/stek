import React, {Component, PropTypes} from 'react';
import moment from 'moment';
import moment_range from 'moment-range';
import _ from 'underscore';
import cn from 'classnames';
import api from 'api';

import Icon from "bootstrap/Icon";
import * as forms from 'bootstrap/forms';

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
    return <li className="cal-event" style={{backgroundColor: `#${event.timetable.color}`}}>
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
      <span className={cn('day-no')}>
        <span className={cn('day-name')}>
          {day.format("dd")}
        </span>
        {day.format("D")}
      </span>
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
    let month_start = moment([this.props.year, this.props.month, 1]);
    let month = moment.range(month_start, month_start.clone().endOf("month"));
    let days = [];
    let today = moment().format("YYYY-DDD");

    month.by("days", (day) => {
      let focus = day.format("YYYY-DDD") == today;
      let dayOfWeek = day.format("D");
      days.push(
        <CalDay
          focus={focus}
          addEvent={this.props.addEvent}
          key={dayOfWeek+1}
          day={day.clone()}
          events={this.props.events[dayOfWeek] || []}></CalDay>
      );
    });

    // fill start and end week
    let start_fill = parseInt(month.start.format("d")) % 6;
    let end_fill = (6-parseInt(month.end.format("d"))) % 6;
    _.each(_.range(start_fill), (i) => days.unshift(<td key={i}></td>));
    _.each(_.range(end_fill), (i) => days.push(<td key={35-i}></td>));
    let days_by_week = _.groupBy(days, (x, i) => Math.floor(i / 7));

    return <table>
      <tbody>
        { _.map(days_by_week, (days, i) => <tr key={i}>{days}</tr>) }
      </tbody>
    </table>;
  }
}

export class EventForm extends Component {
  static get propTypes() {
    return {
      onCancel: PropTypes.func.isRequired,
      day: PropTypes.object.isRequired
    };
  }

  render() {
    let {onCancel, day} = this.props;

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
            <forms.CharField initial={day.format()} name="start_datetime" label="Start om" />
          </div>
          <div className="col-md-3">
            <forms.CharField name="end_datetime" label="Eindigt om" />
          </div>
        </div>
        <div className="row">
          <div className="col-md-6 col-md-offset-3 text-center">
            <forms.CharField name="timetable" label="Agenda" />
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
            <button className="btn btn-rounded black" onClick={onCancel}>Annuleren</button>
            <forms.SubmitButton label="Voeg toe"/>
          </div>
        </div>
      </forms.Form>
    );
  }
}

export default class Calendar extends Component {
  static get propTypes() {
    return {
      initFocus: React.PropTypes.object,
      onMonthChange: React.PropTypes.func
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
      events: {},

      showEventForm: false,
      eventFormDate: null
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
          let key = moment(event.startdatetime).format("D");
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
    this.setState({
      eventFormDate: day,
      showEventForm: true
    });
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
