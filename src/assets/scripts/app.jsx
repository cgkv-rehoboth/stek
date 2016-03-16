import React from "react";
import ReactDom from "react-dom";
import {ProfileSearchTable} from "ProfileSearchTable";
import {SearchTable} from "bootstrap/tables";
import api from "api";
import $ from 'jquery';
import moment from 'moment';

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
  $('.family-list-item', '.family-list')
    .each(function() {
      let self = $(this);
      self.find('.family-name').click(() => {
        $('.family-list-details').slideUp(100);
        self.find('.family-list-details')
          .slideToggle(100);
      });
    });

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
  let searchTeams = (query, page) => {
    return api.teams.list(query, page, 2);
  };

  let renderTeamRow = (team) => {
    return <tr><td>{team.name}</td></tr>;
  };

  ReactDom.render(
      <SearchTable renderRow={renderTeamRow} listFunc={searchTeams} />,
    $("#team-table")[0]
  );
};
