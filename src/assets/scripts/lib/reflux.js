let Q = require("q");
let Reflux = require("reflux");
let RefluxPromise = require("reflux-promise");
Reflux.use(RefluxPromise(Q.Promise));

module.exports = Reflux;
