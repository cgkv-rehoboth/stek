import React from "react";
import ReactDom from "react-dom";
import api from "api";
import $ from 'jquery';
import moment from 'moment';
import * as qs from 'querystring';

// localize
import nl from 'moment/locale/nl';

import ProfileSearchTable from "ProfileSearchTable";
import ServiceTableManagable from "ServiceTableManagable";
import {SearchTable} from "bootstrap/tables";

// bind global jquery instance
window.jQuery = $;
window.$ = $;

// requires needed for ordering of loading
// these depend on the global jQuery
require('jquery.easing');
require('bootstrap/dist/js/bootstrap.min');
require('bootstrap/js/tooltip');
require('lib/grayscale');

function initListGroupDetail() {
  $('.list-group-item', '.list-group-hide-detail')
    .each(function() {
      let self = $(this);
      self.find('.list-group-head').click(() => {
        let detail = self.find('.list-group-detail');

        // close all others
        $('.list-group-detail')
          .not(detail)
          .slideUp(100);

        // open detail
        detail.slideToggle(100);
      });
    });

  let focus_id = $('.list-group-hide-detail').data('focus');
  if(focus_id) {
    let y = $(`#${focus_id}`).offset().top - $('.navbar').height() - 20;
    $('html, body').animate({
      scrollTop: y
    }, 1000);
  }
}

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

window.favoriteListMain = () => {
  let favoriteProfiles = (query, page) => {
    return api.profiles.list(query, page, {
      favorites_only: true
    });
  };

  ReactDom.render(
      <ProfileSearchTable listFunc={favoriteProfiles} />,
    $("#profile-search-table")[0]
  );
}


import FavStar from 'containers/FavStar';

window.familiesMain = () => {
  initListGroupDetail();

  $('.favstar').each(function() {
    let fav = $(this).data('favorite') !== undefined;
    ReactDom.render(<FavStar pk={$(this).data('pk')} favorite={fav} />, $(this)[0]);
  });
};

window.teamListMain = () => {
  initListGroupDetail();
};

window.timetableMain = () => {
  console.debug("Init timetables");

  $(".timetable-ruilen").click(function(){
    let elem = $(this);
    let modal = $("#ruilModal");
    let pk = elem.data('duty-pk');
    modal.find('form')
      .attr('action', `/roosters/ruilen/${pk}/`);
    modal.find(".modal-event-content")
      .text(elem.attr("title"));
    modal.modal('show');
  });

  $(".timetable-undo-ruilen").click(function(){
    let elem = $(this);
    let modal = $("#undoRuilModal");
    let pk = elem.data('request-pk');
    modal.find('form')
      .attr('action', `/roosters/ruilen-intrekken/${pk}/`);
    modal.find(".modal-event-content")
      .text(elem.attr("title"));
    modal.modal('show');
  });
};

// Let the window scroll 1px up
// (not down, because the menu bar will render in the wrong way),
// so the menu bar loads correctly
window.scrollBy(0, -1);

//import some main functions
import calendarMain from 'mains/calendar';
window.calendarMain = calendarMain;

import frontpageMain from 'mains/frontpage';
window.frontpageMain = frontpageMain;

window.timetableTeamleader = () => {};

window.servicePage = () => {
  // Disable input if checkbox is unchecked
  $(".service-second-trigger").click(function(){
    if($(this).prop('checked'))
      $(".service-second input").attr('disabled', false);
    else
      $(".service-second input").attr('disabled', true);
  });

  // Prevent enter from submitting the form
  $(window).keydown(function(event){
    if(event.keyCode == 13) {
      event.preventDefault();
      return false;
    }
  });

  // Switch between summer and wintertime
  checkSummertime();
  $("#services-form input[name='date']").change(function () {
    checkSummertime();
  });

  function checkSummertime(){
    var month = $("#services-form input[name='date']").val().substring(5,7);

    // If month is in the summer months:
    if(month > 6 && month < 9) {
      $('#services-form input[name="title2"]').attr('value', 'Avonddienst');
      $('#services-form input[name="starttime2"]').attr('value', '18:30');
      $('#services-form input[name="endtime2"]').attr('value', '19:45');
    }else{
      $('#services-form input[name="title2"]').attr('value', 'Middagdienst');
      $('#services-form input[name="starttime2"]').attr('value', '16:30');
      $('#services-form input[name="endtime2"]').attr('value', '17:45');
    }
  };

  // Service table
  let searchServices = (query, page) => {
    return api.services.list(query, page);
  };

  ReactDom.render(
    <ServiceTableManagable listFunc={searchServices} />,
    $("#service-page-table")[0]
  );
};