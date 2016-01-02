let moment = require("moment");
let api = require("api");
let Reflux = require("lib/reflux");

let actions = Reflux.createActions({
  loadEvents: {asyncResult: true}
});

actions.loadEvents.listenAndPromise((year, month) => {
  let from = moment([year, month]);
  let to = from.clone().add(1, 'months');

  return api.events.list(from.unix(), to.unix());
});

module.exports = actions;
