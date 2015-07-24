var { Model, Collection } = require('backbone');
var constants = require('../constants');

var Timetable = Model.extend({
  url: constants.api.timetables
});

var TimetableList = Collection.extend({
  model: Timetable,
  url: constants.api.timetables
});

var Timetables = new TimetableList();

module.exports = {
  TimetableList: TimetableList,
  Timetables: Timetables
};
