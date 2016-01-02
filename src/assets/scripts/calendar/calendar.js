let React = require("react");
let moment = require("moment");
require("moment-range"); // moment plugin
let _ = require("underscore");
let cn = require("classnames");

class CalEvent extends React.Component {
  static get propTypes() {
    return {
      event: React.PropTypes.object.isRequired
    };
  }

  render() {
    return <div className="cal-event"><span>{event.title}</span></div>;
  }
}

class CalDay extends React.Component {
  static get propTypes() {
    return {
      day: React.PropTypes.object, // moment or null for dummy day
      events: React.PropTypes.array,
      focus: React.PropTypes.bool
    };
  }

  static get defaultProps() {
    return {
      events: [],
      focus: false
    };
  }

  render() {
    return <td className={cn('cal-day', {focus: this.props.focus})}>
      <span className={cn('day-no')}>
        {this.props.day.format("D")}
      </span>
      {
        _.map(this.props.events, (event) => 
          <CalEvent event={event}>
          </CalEvent>
        )
      }
    </td>;
  }
}

class CalMonth extends React.Component {
  static get propTypes() {
    return {
      month: React.PropTypes.number.isRequired, // 1-12
      year: React.PropTypes.number.isRequired,
      tables: React.PropTypes.array.isRequired
    };
  }
  
  render() {
    let month_start = moment([this.props.year, this.props.month, 1]);
    let month = moment.range(month_start, month_start.clone().endOf("month"));
    let days = [];
    let today = moment().format("YYYY-DDD");

    month.by("days", (moment) => {
      let focus = moment.format("YYYY-DDD") == today;
      days.push(<CalDay focus={focus} key={moment.format("D")+1} day={moment} events={[]}></CalDay>);
    });

    // fill start and end week
    let start_fill = parseInt(month.start.format("d"));
    let end_fill = (6-parseInt(month.end.format("d"))) % 6;
    _.each(_.range(start_fill), (i) => days.unshift(<td key={i}></td>));
    _.each(_.range(end_fill), (i) => days.push(<td key={35-i}></td>));
    let days_by_week = _.groupBy(days, (x, i) => Math.floor(i / 6))

    return <table>
      <tbody>
        { _.map(days_by_week, (days, i) => <tr key={i}>{days}</tr>) }
      </tbody>
    </table>;
  }
}

class Calendar extends React.Component {
  static get propTypes() {
    return {
      initFocus: React.PropTypes.object,
      tables: React.PropTypes.array.isRequired
    };
  }

  constructor(props) {
    super(props);
    this.state = {
      year: this.props.initFocus.year(),
      month: this.props.initFocus.month()
    };
  }

  prevMonth() {
    let prev = this.month().subtract(1, 'months');
    this.setState({
      year: prev.year(),
      month: prev.month()
    })
  }

  nextMonth() {
    let next = this.month().add(1, 'months');
    this.setState({
      year: next.year(),
      month: next.month()
    })
  }

  month() {
    return moment([this.state.year, this.state.month]);
  }

  render() {
    return <div className="calendar">
      <div className="calendar-head">
        <button className="prev blue btn-circle" onClick={this.prevMonth.bind(this)}>
          <i className="fa fa-chevron-left"></i>
        </button>
        <div>
          <p className="calendar-month">{this.month().format("MMMM")}</p>
          <p className="calendar-year">{this.month().format("YYYY")}</p>
        </div>
        <button className="next blue btn-circle" onClick={this.nextMonth.bind(this)}>
          <i className="fa fa-chevron-right"></i>
        </button>
      </div>

      <CalMonth tables={this.props.tables} month={this.state.month} year={this.state.year} />
    </div>;
  }
}

module.exports = {
  Calendar: Calendar
};
