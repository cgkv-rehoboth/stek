// jQuery 4 life
let $ = require('jquery');

// bind global jquery instance
window.jQuery = $;
window.$ = $;

// some global injections
let _easing = require('jquery.easing');
let _bootstrap = require('bootstrap');
let _theme = require('./lib/grayscale');

let React = require('react');
let _ = require('underscore');
let Router = require('react-router');
let { Route, DefaultRoute, Link, RouteHandler } = Router;

// api
let api = require('api');

class App extends React.Component {

  render() {
    console.log("Inited app");
    return false;
  }
}

let routes = (
  <Route>
    <Route path="/" handler={App}>
    </Route>
  </Route>
);

window.onGoogleReady = () => {
  console.debug("Loaded google apis...");
}

Router.run(routes, function (Handler, state) {
  React.render(<Handler {...state.params} />, $('#app')[0]);
});
