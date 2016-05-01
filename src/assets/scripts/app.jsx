import React from "react";
import ReactDom from "react-dom";
import api from "api";
import $ from 'jquery';
import moment from 'moment';
import * as qs from 'querystring';

// localize
import nl from 'moment/locale/nl';

import ProfileSearchTable from "ProfileSearchTable";
import {SearchTable} from "bootstrap/tables";
import * as forms from 'bootstrap/forms';
import {LiveButton, LivePlayer} from "LiveButton";

// bind global jquery instance
window.jQuery = $;
window.$ = $;

// requires needed for ordering of loading
// these depend on the global jQuery
require('jquery.easing');
require('bootstrap/dist/js/bootstrap.min');
require('bootstrap/js/tooltip');
require('lib/grayscale');

window.calendarMain = calendarMain;

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

window.frontpageMain = () => {
  let $form_container = $('#contact-form');

  let formBuilder = <div>
    <div className="row" >
      <div  className="col-sm-6">
        <forms.CharField name="first_name" label="Voornaam" />
      </div>
      <div  className="col-sm-6">
        <forms.CharField name="last_name" label="Achternaam" />
      </div>
    </div>
    <div className="row" >
      <div  className="col-sm-12">
        <forms.CharField name="email" label="E-mail" />
      </div>
    </div>
    <div className="vspace" >
    </div>
    <div className="row" >
      <div  className="col-sm-12">
        <forms.TextField name="message" label="Bericht" />
      </div>
    </div>
    <div className="vspace" ></div>
    <div className="row" >
      <div  className="col-sm-6">
        <forms.CaptchaField sitekey={window.rehoboth.RECAPTCHA_PUBLIC_KEY} />
      </div>
      <div  className="col-sm-6 text-right">
        <forms.SubmitButton label="Verstuur!" />
      </div>
    </div>
  </div>;

  ReactDom.render(
    <forms.Form
      action={api.contact}
      onSuccess={(resp) => {
            alert("Uw email is succesvol verstuurd naar de gemeente! " +
                  "U zult spoedig antwoord ontvangen op " + resp.data.email);
      }}>
      {formBuilder}
    </forms.Form>,
    $form_container[0]
  );


  /* <-- Meeluisteren player */

  $("#content").append('<div id="luisteren-player"></div>');
  let player = ReactDom.render(<LivePlayer></LivePlayer>, $("#luisteren-player")[0]);

  window.playerButton = [];
  // Assign React component to each element with class 'luisteren-button'
  $(".luisteren-button").map(function(value, i){
    window.playerButton[value] = ReactDom.render(
      <LiveButton text={$(i).text()} player={player}></LiveButton>,
      i
    );
  });

  /**
   * Show ListenLive button on top of the front page (next to the logo)
   * Executed by LivePlayer.ondataloaded()
   */
  window.fixicon = function(){
    // Get element with the icon
    var intro = $(".intro .intro-body .container .row:first-of-type div:first-of-type")[0];

    // Fade the picture out for a smooth transition
    $(intro).find('img').fadeOut(500, function(){
      // Change col class
      $(intro).addClass('col-md-4').removeClass('col-md-8');
      // Fade the picture in again
      $(this).fadeIn(500);

      // Add Play button
      $("#listen-in").fadeIn(1000);
    });
  };
  /* --> */
};


//import some main functions
import calendarMain from 'mains/calendar';


window.timetableTeamleader = () => {

};
