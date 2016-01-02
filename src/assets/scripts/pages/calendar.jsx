let ReactDom = require("react-dom");
let React = require("react");
let $ = require("jquery");
let { Calendar } = require("calendar/calendar");
let moment = require("moment");

ReactDom.render(<Calendar tables={[]} initFocus={moment()} />, $("#calendar")[0]);
