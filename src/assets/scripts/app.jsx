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
import Calendar from 'containers/Calendar';
import EventForm from 'containers/EventForm';

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

window.calendarMain = () => {
  let query = qs.parse(window.location.search.replace("?", ""));
  var focus = moment([query.year, query.month || 0, 1]);
  if(!focus.isValid())
    focus = moment();

  class MainCal extends React.Component {

    render() {
      let onMonthChange = (year, month) => {
        let from = moment([year, month]);
        let to = from.clone().add(1, 'months');

        return api.events.list(from.unix(), to.unix());
      };

      return <Calendar
      tables={[]}
      onMonthChange={onMonthChange}
      initFocus={focus} />;
    }
  }

  ReactDom.render(<MainCal />, $("#calendar")[0]);
};

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
};

window.addEventMain = () => {
  let timestamp = qs.parse(window.location.search.replace("?", "")).datetime;
  var day = moment.unix(timestamp);
  if(!day.isValid()) {
    day = moment();
  }

  ReactDom.render(<EventForm day={day} />, $('#add-event-form')[0]);
};
