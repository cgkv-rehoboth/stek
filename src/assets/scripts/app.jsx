// libs
let $ = require('jquery');
let React = require('react');
let _ = require('underscore');
let Router = require('react-router');
let { Route, DefaultRoute, Link, RouteHandler } = Router;

// bind global jquery instance
window.jQuery = $;
window.$ = $;

// views
let Carousel = require('components/Carousel');
let ContactMap = require('components/ContactMap');

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

/*
    // draw the map, once the google api is loaded
    window.onGoogleReady = () => {
      React.render(
        <ContactMap googleMapsApi={google.maps} />
        , $('section#map')[0]
      );
    };

    // todo: convert to server side
    // draw the carousel in the header
    let slides = new SlideList();
    slides.fetch();
    React.render(
      <Carousel slides={slides} />,
      $('section#slides')[0]
    );

  },*/

Router.run(routes, function (Handler, state) {
  React.render(<Handler {...state.params} />, $('body')[0]);
});
