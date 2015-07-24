var { Model, Collection } = require('backbone');
var constants = require('../constants');

var Duty = Model.extend({
  url: constants.api.duties
});


var DutyList = Collection.extend({
  model: Duty,
  url: constants.api.duties
});

var Duties = new DutyList();

module.exports = {
  DutyList: DutyList,
  Duties: Duties
};
