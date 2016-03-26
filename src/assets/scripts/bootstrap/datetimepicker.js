import React, {Component, PropTypes} from 'react';
import moment from 'moment';
import _ from 'underscore';
import cn from 'classnames';

import {Row,Col} from 'bootstrap/grid';
import Icon from 'bootstrap/Icon';

import {generateCalendar} from 'containers/Calendar';

export default class DatePicker extends Component {

  static get propTypes() {
    return {
      initial: PropTypes.object.isRequired,
      onChange: PropTypes.func.isRequired
    };
  }

  static get defaultProps() {
    return {
      initial: moment()
    };
  }

  constructor(props) {
    super(props);

    this.state = {
      month: this.props.initial,
      focus: this.props.initial
    };
  }

  setFocus(day) {
    this.setState({ focus: day });
    this.props.onChange(day);
  }

  nextMonth() {
    this.setState({
      month: this.state.month.clone().add(1, 'month')
    });
  }

  prevMonth() {
    this.setState({
      month: this.state.month.clone().subtract(1, 'month')
    });
  }

  render() {
    let {month, focus} = this.state;
    let days = generateCalendar(month.year(), month.month(), (day) => {
      let key = day.format("DDDD");
      if(day.month() == month.month()) {
        let clz = cn({focus: day.format("DDD") == focus.format("DDD")});
        return <td key={key}>
          <button className={clz} type="button" onClick={() => this.setFocus(day)}>
            {day.format("DD")}
          </button>
        </td>;
      } else {
        return <td key={key}></td>;
      }
    });

    let days_by_week = _.groupBy(days, (x, i) => Math.floor(i / 7));

    return <table className="date-picker">
      <thead>
        <tr>
          <td >
            <button type="button" onClick={this.prevMonth.bind(this)}>
              <Icon name="caret-left" />
            </button>
          </td>
          <td colSpan={5}>{month.format("MMMM YYYY")}</td>
          <td >
            <button type="button" onClick={this.nextMonth.bind(this)}>
              <Icon name="caret-right" />
            </button>
          </td>
        </tr>
      </thead>
      <tbody>
        { _.map(days_by_week, (days, i) => <tr key={i}>{days}</tr>) }
      </tbody>
    </table>;
  }
}

export default class TimePicker extends Component {

  static get propTypes() {
    return {
      initial: PropTypes.object.isRequired,
      onChange: PropTypes.func.isRequired
    };
  }

  static get defaultProps() {
    return {
      initial: moment()
    };
  }

  constructor(props) {
    super(props);

    this.state = {
      time: this.props.initial
    };
  }

  onChangeHours(event) {
    let time = this.state.time.clone().hours(parseInt(event.target.value, 10));
    this.setState({
      time: time
    });
    this.props.onChange(time);
  }

  onChangeMins(event) {
    let time = this.state.time.clone().minutes(parseInt(event.target.value, 10));
    this.setState({
      time: time
    });
    this.props.onChange(time);
  }

  render() {
    let {time} = this.state;
    let hour_options = _.map(_.range(0, 23), (i) => <option key={i} value={i}>{i}</option>);
    let minute_options = _.map(_.range(0, 59, 5), (i) => <option key={i} value={i}>{i}</option>);
    return <div className="time-picker">
      <p className="label">Tijd</p>
      <select onChange={this.onChangeHours.bind(this)} value={time.format("H")}>
        {hour_options}
      </select>
      :
      <select onChange={this.onChangeMins.bind(this)} value={time.format("m")} >
        {minute_options}
      </select>
    </div>;
  }
}

export default class DateTimePicker extends Component {

  static get propTypes() {
    return {
      onChange: PropTypes.func.isRequired,
      initial: PropTypes.object
    };
  }

  static get defaultProps() {
    return {
      initial: moment()
    };
  }

  constructor(props) {
    super(props);
    this.state = {
      datetime: props.initial
    };
  }

  onChangeDate(date) {
    let newdt = this.state.datetime.clone();
    newdt.set({
      dayOfYear: date.dayOfYear(),
      year: date.year()
    });
    this.setState({datetime: newdt});
    this.props.onChange(newdt);
  }

  onChangeTime(time) {
    let newdt = this.state.datetime.clone();
    newdt.set({
      hours: time.hours(),
      minutes: time.minutes()
    });
    this.setState({datetime: newdt});
    this.props.onChange(newdt);
  }

  render() {
    let {
      className
    } = this.props;

    let clz = cn(className, "container-fluid");

    return (
      <div className={clz}>
        <Row>
          <Col type="md-6">
            <DatePicker initial={this.state.datetime} onChange={this.onChangeDate.bind(this)}/>
          </Col>
          <Col type="md-6" className="text-center">
            <TimePicker initial={this.state.datetime} onChange={this.onChangeTime.bind(this)} />
          </Col>
        </Row>
      </div>
    );
  }
}
