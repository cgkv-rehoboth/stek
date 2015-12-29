let React = require("react");
let ReactDom = require("react-dom");
let ProfileSearchTable = require("ProfileSearchTable");

/**
 * Created by Samuel-Anton on 29 dec 2015.
 */
$(function(){
  $('.family-list .family-list-item').click(function(){
    $('.family-list .family-list-details[data-family-pk=' + $(this).attr('id') + ']').slideToggle(100);
  });

  $('.favorite div').click(function(){
    alert('Gonna add them to ya favorites! Yeah-yeah jingle-yeah! Btw, the id is: ' + $(this).attr('data-user-pk'));

    // Submit a request to make that user a favorite (or not)
    $.ajax({
      data: {id: $(this).attr('data-user-pk')},
      type: 'GET',
      url: 'adresboek/favorites/submit',
    }).done(function(m){
      if(m.hasErrors === false) {
        // Reload page, because I'm to lazy to reload the table
        location.reload();
      }else{
        console.log("Something went a little bit wrong :/");
      }
    });
  });
/*
    // Scroll to the family details div
    $(document.body).animate({
      scrollTop: $('#').offset().top // Todo
    }, 500);
*/
  // Search form

});

ReactDom.render(<ProfileSearchTable />, $("#profile-search-table")[0]);
