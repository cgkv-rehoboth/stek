import React from "react";
import ReactDom from "react-dom";
import api from "api";
import $ from 'jquery';
import moment from 'moment';
import * as qs from 'querystring';

// localize
import nl from 'moment/locale/nl';

import ProfileSearchTable from "ProfileSearchTable";
import ProfileSearchInput from "ProfileSearchInput";
import FamilySearchInput from "FamilySearchInput";
import ServiceTableManagable from "ServiceTableManagable";
import ServiceTableDashboard from "ServiceTableDashboard";
import ServiceTable from "ServiceTable";
import {SearchTable} from "bootstrap/tables";
import AddressForm from "AddressForm";
import ReactImage from "ReactImage";

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
require('lib/jscolor');

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
    let offset = $(`#${focus_id}`).offset();
    // Check if the element + offset exists (otherwise you get an 'undefined' error)
    if (offset) {
      let y = offset.top - $('.navbar').height() - 20;
      $('html, body').animate({
        scrollTop: y
      }, 1000);
    }
  }
}

// Confirmation dialog (mainly used for deletions of table items)
$(document).on('click', ".confirm-dialog-button", function(e){
  e.preventDefault();

  $("#confirm-modal .modal-body").html($(this).attr('data-message'));
  $("#confirm-modal .modal-footer .modal-ok").attr('href', $(this).attr('href'));

  $("#confirm-modal").modal('show');
});
$("#confirm-modal .modal-footer .modal-cancel").click(function(){
  $("#confirm-modal").modal('hide');
});


/*
  Default datepicker settings
*/
$.datepicker.setDefaults( $.datepicker.regional[ "nl" ] );
$.datepicker.setDefaults({
  dateFormat: 'dd-mm-yy',
  nextText: '<i class="fa fa-angle-right"></i>',
  prevText: '<i class="fa fa-angle-left"></i>',
  monthNamesShort: [ "Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dec" ],
  monthNames: [ "Januari", "Februari", "Maart", "April", "Mei", "Juni", "Juli", "Augustus", "September", "Oktober", "November", "December" ],
  dayNames: [ "Zondag", "Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag" ],
  dayNamesMin: [ "Zo", "Ma", "Di", "Wo", "Do", "Vr", "Za" ],
  dayNamesShort: [ "Zon", "Maa", "Din", "Woe", "Don", "Vrij", "Zat" ],
  gotoCurrent: true,
});


/** E mail visualizer

Intern in an <a> tag:
  <a href="yxxoxuxr@xemxaxixlx.cxomx" onmouseover="this.href=this.href.replace(/x/g,'');this.text=this.href.replace(/mailto:/g,'');">link</a>

When using the following global functions:
  <a href="5e2nabe5s4youremailAgmailDcom">this will translate into youremail@gmail.com</a>
 
The emailaddress must be preceeded by one of the codes used in the following three functions:
 */
// Output to href and text
$('a[href^="5e2nabe5s4"]').on('mouseover mouseup', function(){
  var href = decodeMail($(this).attr('href').replace("5e2nabe5s4", ''));
  $(this).text(href);
  $(this).attr('href', 'mailto:' + href);
  
  // Unbind this action
  $(this).unbind('mouseover mouseup');
});
// Output only to href
$('a[href^="p1ec2fx1uz"]').on('mouseover mouseup', function(){
  var href = decodeMail($(this).attr('href').replace("5e2nabe5s4", ''));
  $(this).attr('href', 'mailto:' + href);
  
  // Unbind this action
  $(this).unbind('mouseover mouseup');
});
// Output only to text
$('a[href^="zs39qpz9ti"]').on('mouseover mouseup', function(){
  var href = decodeMail($(this).attr('href').replace("5e2nabe5s4", ''));
  $(this).text(href);
  
  // Unbind this action
  $(this).unbind('mouseover mouseup');
});

function decodeMail(str){
  // Todo: Firefox makes it case insensitive. 2017-07-10: fixed?
  var regA = new RegExp('A', 'g');
  var regD = new RegExp('D', 'g');
  var regRest = new RegExp('[A-Z]', 'g');
  return str.replace(regA, '@').replace(regD, '.').replace(regRest,'');
}


function validatePhone(val, errorelement) {
  val = val.trim();
  // Replace +31 with 0
  val = val.replace(/^(00|\+)31/, '0');
  // Remove non digit chars
  val = val.replace(/[^\+0-9]/g, '');
  
  // Add dash
  if (val.substring(0, 2) == '06') {
    val = val.replace(/^(.{2})/, '$1-');
  }else{
    val = val.replace(/^(.{4})/, '$1-');
  }
  
  if (errorelement){
    if (val.length != 11 && val.length > 0) {
      errorelement.text('Het telefoonnummer moet uit 10 cijfers bestaan.');
    }else {
      errorelement.text('');
    }
  }
  
  return val;
}

/*
  Pad number with zeros in front
 */
function pad(n, width, z) {
  z = z || '0';
  n = n + '';
  return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
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
};

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
};


import FavStar from 'containers/FavStar';

window.familiesMain = () => {
  initListGroupDetail();

  $('.favstar').each(function() {
    let fav = $(this).data('favorite') !== undefined;
    ReactDom.render(<FavStar pk={$(this).data('pk')} favorite={fav} />, $(this)[0]);
  });

  
  // Perform when document is loaded
  $('.family-picture-render').each(function() {
    // Get data from the element
    let src = $(this).data('src');
    let alt = $(this).data('alt');
    let className = $(this).data('class');
    
    // Render React element
    ReactDom.render(<ReactImage src={src} alt={alt} className={className} />, $(this)[0]);
  });
  
};

window.teamListMain = () => {
  initListGroupDetail();
};

window.timetableMain = () => {
  window.timetableRuilrequests();

  // Double scroll bar funtcion
  /*
  $('.scroll-table').on('scroll', function (e) {
      $('.double-scroll-bar').scrollLeft($('.scroll-table').scrollLeft());
  });
  $('.double-scroll-bar').on('scroll', function (e) {
      $('.scroll-table').scrollLeft($('.double-scroll-bar').scrollLeft());
  });

  $(window).on('load', function(e){
    $('.double-scroll-bar div').width($('.scroll-table thead').width());
  });
  */
};

window.timetableRuilrequests = () => {
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

window.frontpageDiensten = () => {
  // Service table
  let searchServices = (query, page, reverseTime) => {
    return api.services.list(query, page, reverseTime);
  };

  ReactDom.render(
    <ServiceTable listFunc={searchServices} />,
    $("#service-table")[0]
  );

  ReactDom.render(
    <ServiceTable listFunc={searchServices} reverseTime={true} />,
    $("#service-table-old")[0]
  );
};

window.timetableTeamleader = () => {
  // Make responsible input form multiple/single input
  $("#switch-multi-user-select input").change(function(){
    if ($(this).prop('checked')) {
      $('.multi-user-select input').attr('type', 'checkbox');
    }else{
      $('.multi-user-select input').attr('type', 'radio');
    }
    updateMultiUser();
  });

  function updateMultiUser(){
    // Combine all selected values
    let r = $(".multi-user-select input:checked")
      .map(function(){
        // Decide which URL to use
        let url;
        if (this.value.substring(0,1) == 'f'){
          url = family_url.replace('1234', this.value.substring(1));
        }else{
          url = profile_url.replace('1234', this.value.substring(1));
        }

        // Get and strip text
        let text = $(this).closest('label').text().trim();

        // Show it
        return '<a href="' + url + '" class="black-url" target="_blank">' + text + '</a>';
      })
      .get()
      .join('; ');
    $("#multi-user-result").html(r);
  }

  updateMultiUser();

  $(".multi-user-select input").change(function(){
    updateMultiUser();
  });
};

window.timetableTeamleaderDuty = () => {};

window.servicePage = () => {
  // Set datepicker for service date
  $("#service-datepicker").datepicker({
    changeMonth: true,
    changeYear: true,
  });

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

  /* Not necessary anymore, since december 2016
   *
    // Switch between summer and wintertime
    checkSummertime();
    $("#services-form input[name='date']").change(function () {
      checkSummertime();
    });
  
    function checkSummertime(){
  
      var month = $("#services-form input[name='date']").val().substring(3,5);
  
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
    }
  */

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
  // Show/hide settingsform
  $("#settings-form-toggle").click(function(){
    $(".settings-container").toggleClass("blue");
    $("#settings-form").slideToggle(100);
  });
  
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

  let searchProfiles = (query) => {
    return api.profiles.list(query);
  };

  ReactDom.render(
    <ProfileSearchInput listFunc={searchProfiles} />,
    $("#profile-search-input")[0]
  );

  let searchFamilies = (query) => {
    return api.families.list(query);
  };

  ReactDom.render(
    <FamilySearchInput listFunc={searchFamilies} />,
    $("#family-search-input")[0]
  );
};

window.profileEdit = (address) => {
  // Set datepicker for birthday
  $("#birthday-datepicker").datepicker({
    changeMonth: true,
    changeYear: true,
    minDate: "-120Y",
    maxDate: 0,
    defaultDate: "-31y",
  });
  
  // Set datepicker for huwdatum
  $("#huwdatum-datepicker").datepicker({
    changeMonth: true,
    changeYear: true,
    minDate: "-90Y",
    maxDate: 0,
    defaultDate: "-10y",
  });
  
  // Format phonenumbers
  $("input[type='phone']").on('change', function(){
    let val = $(this).val();
    val = validatePhone(val, $(this).closest('div').find('.error'));
    
    $(this).val(val);
  });

  /*
    Profile picture
   */
  var maxFileSize = 20; // default: 20M
  // Show a preview of the uploaded image
  $("#pic-input").change(function(){

    if (this.files && this.files[0]) {
      //Creating preview...

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

          var picsize = $('.profile-pic-container').width();
          // access image size here
          if(this.width > this.height){
            var margin = Math.round(picsize*this.width/this.height - picsize);
            // Set image size
            $('.profile-pic').css('max-height', '100%');
            $('.profile-pic').css('max-width', 'none');

            // Align in center
            $('.profile-pic').css('top', '0');
            $('.profile-pic').css('left', Math.round(margin/2) + 'px');

            // Give some space to move
            $('.profile-pic').css('margin', '0 ' + margin*-1 + 'px');
          }else{
            var margin = Math.round(picsize*this.height/this.width - picsize);
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
  });

  // Load adressForm
  let addressList = (query) => {
    return api.address.list(query);
  };

  ReactDom.render(
    <AddressForm listFunc={addressList} address={address} />,
    $("#address-form")[0]
  );

  // Initials
  $("input[name='initials']").change(function(){
    var i = $(this).val();

    // Filter initals (remove whitespaces and add dots)
    i = i.replace(/([\.\s]+)+/gi, ".");
    
    // Check if it's necessary to do something
    if (i.length > 0) {
      i = i.split('.');
      
      // Capitalize each letter (but not the other ones, like in 'Th.')
      for (var a = 0; a < i.length; a++) {
        if (i[a].length > 0) {
          i[a] = i[a][0].toUpperCase() + i[a].slice(1);
        }else {
          // Remove empty element
          i.splice(a, 1);
          a--;
        }
      }
      
      // Add empty on the end for the extra dot when calling join()
      i.push('');
    }
    
    $(this).val(i.join('.'));
  })
};

window.dashboard = (services) => {
  $('.birthday-list-header a').click(function(){
    $('.birthday-list-header').slideUp(300);
    $('.birthday-list-content').slideDown(300);
  });

  window.timetableRuilrequests();

  ReactDom.render(
    <ServiceTableDashboard data={services} is_private={true}  />,
    $("#service-table")[0]
  );
};

window.teamAddPage = () => {
};

window.servicesPage = () => {
  // Service table
  let searchServices = (query, page, reverseTime) => {
    return api.services.list(query, page, reverseTime);
  };

  ReactDom.render(
    <ServiceTable listFunc={searchServices} is_private={true} />,
    $("#service-table")[0]
  );

  ReactDom.render(
    <ServiceTable listFunc={searchServices} is_private={true} reverseTime={true} />,
    $("#service-table-old")[0]
  );
};

window.eventFilesPage = () => {
  // Insert default title
  $('input[name="file"]').change(function(){
    if ($('input[name="title"]').val().length == 0) {
      let name = $(this).val();

      // Remove full path
      let startIndex = (name.indexOf('\\') >= 0 ? name.lastIndexOf('\\') : name.lastIndexOf('/'));
      name = name.substring(startIndex);
      if (name.indexOf('\\') === 0 || name.indexOf('/') === 0) {
          name = name.substring(1);
      }

      // Remove extension
      name = name.substring(0, name.lastIndexOf('.')).replace(/_/g, ' ');

      // Capitalize
      name = name[0].toUpperCase() + name.slice(1);

      $('input[name="title"]').val(name);
    }
  });
};

window.profileMain = (pk, favorite) => {
  ReactDom.render(
    <FavStar pk={pk} favorite={favorite}/>,
    $("#profile-favorite")[0]
  );
  
  $(".delete-profile-options").click(function(){
    $(this).hide();
    $(".delete-profile-delete").show();
  });
};

window.eventPage = () => {
  // Set datepicker for service date
  $(".event-datepicker").datepicker({
    changeMonth: true,
    changeYear: true,
  });

  // Prevent enter from submitting the form
  $(window).keydown(function(event){
    if(event.keyCode == 13) {
      event.preventDefault();
      return false;
    }
  });
  
  // Help with defining the dates, like containing the difference when startdate has changed
  let diffdatetime = 60*60*1000; // One hour
  
  $('#event-form input[name="startdate"]').change(startdatetimechange);
  $('#event-form input[name="starttime"]').change(startdatetimechange);
  
  $('#event-form input[name="enddate"]').change(enddatetimechange);
  $('#event-form input[name="endtime"]').blur(enddatetimechange);
  
  // Help with defining the datetimes, like containing the difference when starttime has changed
  function startdatetimechange(){
    let starttime = $('#event-form input[name="starttime"]').val();
    let startdate = $('#event-form input[name="startdate"]').val();
    
    // Convert to date object
    starttime = starttime.split(':');
    startdate = startdate.split('-');
    let startdatetime = new Date(startdate[2], startdate[1]-1, startdate[0], starttime[0], starttime[1], 0, 0);
    
    // Get difference
    let enddatetime = new Date(startdatetime.valueOf() + diffdatetime);
    
    // Show it
    let enddate = pad(enddatetime.getDate(), 2) + "-" + pad(enddatetime.getMonth()+1, 2) + "-" + enddatetime.getFullYear();
    let endtime = pad(enddatetime.getHours(), 2) + ":" + pad(enddatetime.getMinutes(), 2);
    
    $('#event-form input[name="enddate"]').val(enddate);
    $('#event-form input[name="endtime"]').val(endtime);
  }
  
  // Save new difference
  function enddatetimechange(){
    let starttime = $('#event-form input[name="starttime"]').val();
    let endtime = $('#event-form input[name="endtime"]').val();
    let startdate = $('#event-form input[name="startdate"]').val();
    let enddate = $('#event-form input[name="enddate"]').val();
    
    // Convert to date object
    starttime = starttime.split(':');
    startdate = startdate.split('-');
    let startdatetime = new Date(startdate[2], startdate[1]-1, startdate[0], starttime[0], starttime[1], 0, 0);
    
    endtime = endtime.split(':');
    enddate = enddate.split('-');
    let enddatetime = new Date(enddate[2], enddate[1]-1, enddate[0], endtime[0], endtime[1], 0, 0);
    
    // Get difference
    diffdatetime = enddatetime.valueOf() - startdatetime.valueOf();
    
    // Check for valid difference
    if (diffdatetime < 0) {
      // Change the date
      $('#event-form input[name="enddate"]').val(startdate.join('-'));
  
      // Check if we need to hange the time
      if ((endtime[0]*60 + endtime[1]) < (starttime[0] * 60 + starttime[1])){
        $('#event-form input[name="endtime"]').val(starttime.join(':'));
        
        // Set new difference to zero
        diffdatetime = 0;
      }else{
        // Calculate new difference
        enddatetimechange();
      }
    }
  }
};

window.importCSV = () => {
  /* All the functions we need */
  // Count the amount of checked/selected lines and display this
  function update_checkbox_counter(){
    // Update the counters
    let checked_checkboxes = $('#rooster_csv_table input[type=checkbox]:checked');
    $('.rooster_csv_counter').text(checked_checkboxes.length);

    // Update the form hidden input
    let selected_lines = [];
    $.each(checked_checkboxes, function(k,v){
      selected_lines.push($(v).attr('data-duty-id'));
    });

    $('form input[name=json_selected_lines]').val(JSON.stringify(selected_lines));
  }

  // Update the tr line according to the checked value of the checkbox
  function update_checkbox(checkbox) {
    // Remove any of the not_selected classes
    checkbox.closest('tr').removeClass("not_selected");
    // Add the not_selected class if needed
    if (!checkbox.prop("checked")){
      checkbox.closest('tr').addClass("not_selected");
    }
    update_checkbox_counter();
  }

  // Inital update
  update_checkbox_counter();

  $("#rooster_csv_table").on("click", "tr:not(.roosters_csv_errors_found)", function(e){
    let select = $(this).find('select');
    // Check if this row may be selected
    if (select && select.val() == 0){
      // Cancel click
      return;
    }
    if( $(e.target).is('td') ) {
      let id = $(this).attr('data-duty-id');
      let checkbox = $(this).find('input[data-duty-id=' + id + ']');
      checkbox.prop("checked", !checkbox.prop("checked"));
      update_checkbox(checkbox);
    }
  });

  $("#rooster_csv_table").on("click", "input[type=checkbox]", function(e) {
    let select = $(this).closest('tr').find('select');
    // Check if this row may be selected
    if (select && select.val() == 0){
      // Cancel click
      $(this).prop('checked', false);
    }

    update_checkbox($(this));
  });

  $("#rooster_csv_table").on("change", "select", function() {
    let selected_responsibles = {};

    // Iterate over all select elements
    $('#rooster_csv_table select').each(function (index){
      let selected = $(this).val();
      let checkbox = $(this).closest('tr').find('input[type=checkbox]');
      if (selected > 0) {
        // Add date to the array
        let row_id = $(this).closest('tr').attr('data-duty-id');
        selected_responsibles[row_id] = $(this).attr('name') + '_' + selected;

        // Select row
        checkbox.prop('checked', true);
      }else{
        // Deselect this row because it's invalid
        checkbox.prop('checked', false);
      }
      update_checkbox(checkbox);
    });

    // Add the data to the form, ready for submit
    $('form input[name=json_selected_responsibles]').val(JSON.stringify(selected_responsibles));
  });

};

// Add Fibers CKEditor styling sheet
import "fiber/admin-extra"