let React = require("react");
let ReactDom = require("react-dom");
let FavStar = require('bootstrap/favorites');

$(function(){
  $('.family-list .family-list-item').click(function(){
    $('.family-list .family-list-details[data-family-pk=' + $(this).attr('id') + ']').slideToggle(100);
  });

/*
    // Scroll to the family details div
    $(document.body).animate({
      scrollTop: $('#').offset().top // Todo
    }, 500);
*/

  $('.favstar').each(function(){
    console.log($(this).attr('data-pk'));
    ReactDom.render(<FavStar pk={$(this).data('pk')} favorite={$(this).data('favorite')} />, $(this)[0]);
  });
});
