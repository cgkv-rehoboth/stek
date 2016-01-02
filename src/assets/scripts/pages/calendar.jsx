let ReactDom = require("react-dom");
let React = require("react");
let $ = require("jquery");
let moment = require("moment");

let { Calendar } = require("calendar/calendar");
let actions = require("calendar/actions");
let eventStore = require("calendar/store");

class MainCal extends React.Component {

  onMonthChange(year, month) {
    actions.loadEvents(year, month);
  }

  render() {
    return <Calendar
      tables={[]}
      onMonthChange={this.onMonthChange.bind(this)}
      eventStore={eventStore}
      initFocus={moment()} />;
  }
}

ReactDom.render(<MainCal />, $("#calendar")[0]);
