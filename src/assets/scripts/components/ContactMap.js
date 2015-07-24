"use strict";
var React = require("react/addons"),

    {GoogleMapsMixin, Map, Marker} = require("react-google-maps");
/*
 * Sample From: https://developers.google.com/maps/documentation/javascript/examples/map-simple
 */
module.exports = React.createClass({
  /*
   * 1. Create a component class that wraps all your map components in it.
   */
  displayName: "ContactMap",
  /*
   * 2. Include GoogleMapsMixin into in its mixins.
   */
  mixins: [GoogleMapsMixin],

  churchLoc: { lat: 52.086383, lng: 4.8653854 },

  render (props, state) {
    return <div style={{height: "600px"}} {...props}>
      <Map 
        style={{height: "600px"}} 
        scrollwheel={false} 
        zoom={16} 
        center={new google.maps.LatLng(this.churchLoc.lat, this.churchLoc.lng)} 
      />
      <Marker position={this.churchLoc} key="Wij zijn hier!" />
    </div>;
  }
});
