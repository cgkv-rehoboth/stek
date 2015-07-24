// libs
let $ = require('jquery');
let React = require('react');
let _ = require('underscore');
let Router = require('react-router');
let { Route, DefaultRoute, Link, RouteHandler } = Router;

// bind global jquery instance
window.jQuery = $;
window.$ = $;

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
