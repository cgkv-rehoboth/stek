import React from "react";
import ReactDom from "react-dom";
import ProfileSearchTable from "ProfileSearchTable";
import {SearchTable} from "bootstrap/tables";
import api from "api";
import $ from 'jquery';
import moment from 'moment';
import initAsyncForm from 'utils/asyncForm';

// bind global jquery instance
window.jQuery = $;
window.$ = $;

// requires needed for ordering of loading
// these depend on the global jQuery
require('jquery.easing');
require('bootstrap/dist/js/bootstrap.min');
require('bootstrap/js/tooltip');
require('lib/grayscale');

function initAsyncForms() {
  let $forms = $('.async-form');

  $forms.each(function() {initAsyncForm(this);});
}

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

import { Calendar } from 'containers/Calendar';

window.calendarMain = () => {
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
      initFocus={moment()} />;
    }
  }

  ReactDom.render(<MainCal />, $("#calendar")[0]);
};

import FavStar from 'containers/FavStar';

window.familiesMain = () => {
  initListGroupDetail();

  /*
    // Scroll to the family details div
    $(document.body).animate({
    scrollTop: $('#').offset().top // Todo
    }, 500);
    */

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
  /*$(".timetable-ruilen").click(function(){
    $("#ruilModal .modal-event-name").text($(this).closest("tr").find(".duty-title").text());
    $("#ruilModal .modal-event-date").text($(this).closest("tr").find(".duty-date").text());
    $("#ruilModal input[name=modal-duty-pk]").val($(this).closest("tr").attr("data-duty-pk"));
    $("#ruilModal").modal('show');
  });*/

  // ReactDom.render(<DutyForm timetable={1} />, $("#duty-form")[0]);
};

window.frontpageMain = () => {
  initAsyncForms();
}
