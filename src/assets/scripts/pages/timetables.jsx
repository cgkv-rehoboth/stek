let DutyForm = require("DutyForm");
let ReactDom = require("react-dom");
let React = require("react");
let $ = require("jquery");

ReactDom.render(<DutyForm timetable={1} />, $("#duty-form")[0]);
