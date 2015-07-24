// libs
var $ = require('jquery');
var Backbone = require('backbone');
Backbone.$ = $;
var React = require('react');
var _ = require('underscore');
var { Router } = require('director');

// bind global jquery instance
window.jQuery = $;
window.$ = $;

// views
var Carousel = require('./components/Carousel');

// api
var { SlideList } = require('./api/slides');
var ContactMap = require('./components/ContactMap');

// determines what page where on
var router = new Router({

  // home page
  "/": () => {
    console.log("Entering home..");

    // draw the map, once the google api is loaded
    window.onGoogleReady = () => {
      React.render(
        <ContactMap googleMapsApi={google.maps} />
        , $('section#map')[0]
      );
    };

    // todo: convert to server side
    // draw the carousel in the header
    var slides = new SlideList();
    slides.fetch();
    React.render(
      <Carousel slides={slides} />,
      $('section#slides')[0]
    );

  },

  // login page
  "/login": () => {
    console.log("Entering login..");
  }

});

router.init("/");
console.debug("Main inited");
