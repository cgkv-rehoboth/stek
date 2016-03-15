import React from "react";
import ReactDom from "react-dom";
import ProfileSearchTable from "ProfileSearchTable";
import api from "api";
import $ from 'jquery';

// bind global jquery instance
window.jQuery = $;
window.$ = $;

// requires needed for ordering of loading
// these depend on the global jQuery
require('jquery.easing');
require('bootstrap/dist/js/bootstrap.min');
require('bootstrap/js/tooltip');
require('lib/grayscale');

//
// main functions for different pages
//

window.profileListMain = () => {
  let searchProfiles = (query, page) => {
    return api.profiles.list(query, page, 2);
  };

  ReactDom.render(
    <ProfileSearchTable listFunc={searchProfiles} />,
    $("#profile-search-table")[0]
  );
}
