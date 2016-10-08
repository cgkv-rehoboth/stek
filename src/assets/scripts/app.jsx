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
import AddressForm from "AddressForm";

// bind global jquery instance
window.jQuery = $;
window.$ = $;

// requires needed for ordering of loading
// these depend on the global jQuery
require('jquery.easing');
require('jquery-ui/jquery-ui.min.js');
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
        detail.slideToggle(100, function(){
          $('.list-group-head').css('font-weight', 'inherit');
          $('.list-group-detail:visible').closest('.family-list-item').find('.list-group-head').css('font-weight', 'bold');
        });
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

// Confirmation dialog (mainly used for deletions of table items)
$(document).on('click', ".confirm-dialog-button", function(e){
  e.preventDefault();

  $("#confirm-modal .modal-body").text($(this).attr('data-message'));
  $("#confirm-modal .modal-footer .modal-ok").attr('href', $(this).attr('href'));

  $("#confirm-modal").modal('show');
});
$("#confirm-modal .modal-footer .modal-cancel").click(function(){
  $("#confirm-modal").modal('hide');
});

/* E mail visualizer

Intern in an <a> tag:
  <a href="yxxoxuxr@xemxaxixlx.cxomx" onmouseover="this.href=this.href.replace(/x/g,'');this.text=this.href.replace(/mailto:/g,'');">link</a>

Global:
 */
// Output to href and text
$('a[href^="5e2nabe5s4"]').on('mouseover mouseup', function(){
    $(this).attr('href', 'mailto:' + decodeMail($(this).attr('href')));
    $(this).text(decodeMail($(this).attr('href')));
});
// Output only to href
$('a[href^="p1ec2fx1uz"]').on('mouseover mouseup', function(){
    $(this).attr('href', 'mailto:' + decodeMail($(this).attr('href')));
});
// Output only to text
$('a[href*="zs39qpz9ti"]').on('mouseover mouseup', function(){
    $(this).text(decodeMail($(this).text()));
});

function decodeMail(str){
  return str.replace(/A/g, '@').replace(/D/g, '.').replace(/[A-Z]/g,'').substr(10);
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
      .attr('action', `/roosters/ruilverzoek/new/${pk}/`);
    modal.find(".modal-event-content")
      .text(elem.attr("title"));
    modal.modal('show');
  });

  $(".timetable-undo-ruilen").click(function(){
    let elem = $(this);
    let modal = $("#undoRuilModal");
    let pk = elem.data('request-pk');
    modal.find('form')
      .attr('action', `/roosters/ruilverzoek/${pk}/intrekken/`);
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

window.timetableTeamleaderDuty = () => {};

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

window.teamPage = () => {
  // Zoom in/out profile pics
  $(".zoomin").click(function(){
    var width = parseInt($(".team-usersquare").css('width')) + 20;
    var height = parseInt($(".team-userimage-div").css('max-height')) + 23;

    $(".team-usersquare").css('width', width + 'px');
    $(".team-userimage-div").css('max-height', height + 'px');

    var fontsize = parseInt($(".team-userinfo").css('font-size')) + 1;
    $(".team-userinfo").css('font-size', fontsize);
  });

  $(".zoomout").click(function(){
    var width = parseInt($(".team-usersquare").css('width')) - 20;
    var height = parseInt($(".team-userimage-div").css('max-height')) - 23;

    if(width > 0) {
      $(".team-usersquare").css('width', width + 'px');
      $(".team-userimage-div").css('max-height', height + 'px');

      var fontsize = parseInt($(".team-userinfo").css('font-size')) - 1;
      $(".team-userinfo").css('font-size', fontsize);
    }
  });
};

window.profileEdit = (address) => {
  var maxFileSize = 20; // default: 20M
  // Show a preview of the uploaded image
  $("#pic-input").change(function(){

    if (this.files && this.files[0]) {
      console.log("Creating preview... ");

      // Checkt filesize
      if (this.files[0].size > maxFileSize * 1024 * 1024) { // x MB = x * 1024 * 1024
        $("#pic-info").text("Maximale bestandsgrootte is 3 MB");

        // Clear input
        $(this).val('');

        // Show current saved pic
        $(".profile-pic").attr('src', $(".profile-pic").attr('data-src'));

        // Set default cursor back
        $('.profile-pic').css('cursor', 'default');

        return false;
      }else{
        $("#pic-info").text("");
      }

      //// Load image
      var reader = new FileReader();

      // Show loading thing
      $("#pic-loader").css('visibility', 'visible');

      reader.onload = function (e) {
        var image = new Image();
        image.src = e.target.result;

        image.onload = function() {

          // access image size here
          if(this.width > this.height){
            var margin = Math.round(325*this.width/this.height - 325);
            // Set image size
            $('.profile-pic').css('max-height', '100%');
            $('.profile-pic').css('max-width', 'none');

            // Align in center
            $('.profile-pic').css('top', '0');
            $('.profile-pic').css('left', Math.round(margin/2) + 'px');

            // Give some space to move
            $('.profile-pic').css('margin', '0 ' + margin*-1 + 'px');
          }else{
            var margin = Math.round(325*this.height/this.width - 325);
            // Set image size
            $('.profile-pic').css('max-height', 'none');
            $('.profile-pic').css('max-width', '100%');

            // Align in center
            $('.profile-pic').css('top', Math.round(margin/2) + 'px');
            $('.profile-pic').css('left', '0');

            // Give some space to move
            $('.profile-pic').css('margin', margin*-1 + 'px 0');
          }

          // Make it visible
          $('.profile-pic').attr('src', this.src);

          // Set move cursor
          $('.profile-pic').css('cursor', 'move');

          $("#pic-loader").css('visibility', 'hidden');
        };
      }

      reader.readAsDataURL(this.files[0]);
    }
  });

  // Being able to move the picture around
  $('.profile-pic').draggable({containment: ".profile-pic-container", scroll: false});

  $("#profile-pic-form").submit(function(e){
    // Check file size
    if ($("#pic-input").prop('files')[0].size > maxFileSize * 1024 * 1024){
      e.preventDefault();
      $("#pic-info").text("Maximale bestandsgrootte is 3 MB");
      return;
    }

    // Get center
    var x = 0.5;
    var y = 0.5;

    var left = parseInt($(".profile-pic").css('left'));
    var mleft = parseInt($(".profile-pic").css('margin-left'));
    var top = parseInt($(".profile-pic").css('top'));
    var mtop = parseInt($(".profile-pic").css('margin-top'));

    // Prevent end of the world by preventing dividing by zero
    if (mleft != 0) {
      x = 1 + left / mleft;
    }
    if (mtop != 0) {
      y = 1 + top / mtop;
    }

    $('#profile-pic-form input[name="center"]').val(x + ',' + y);
  })

  // Load adressForm
  let addressList = (query) => {
    return api.address.list(query);
  };

  ReactDom.render(
    <AddressForm listFunc={addressList} address={address} />,
    $("#address-form")[0]
  );
}