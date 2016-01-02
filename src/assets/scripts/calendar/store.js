let Reflux = require("lib/reflux");
let actions = require("./actions");
let _ = require("underscore");
let moment = require("moment");

let eventStore = Reflux.createStore({

  init: function() {
    this.listenTo(actions.loadEvents.completed, this.onLoadEvents);
  },

  onLoadEvents: function(data) {
    this.trigger(data.data);
  }
});

module.exports = eventStore;
