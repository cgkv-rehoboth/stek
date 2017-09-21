/**
 * Created by samuel on 20-9-17.
 */

/*
  Override default CKEditor settings of Fiber
  */

window.CKEDITOR_CONFIG_FORMAT_TAGS = 'p;h1;h2;h3;h4';

// Allow also <div> with [attributes], {styles} and (classes)
window.CKEDITOR_CONFIG_EXTRA_ALLOWED_CONTENT = 'a[*]{*}(*);img[*]{*}(*);iframe[*];object[*];param[*];embed[*];div[*]{*}(*);small';

// Add some bootstrap grid styles
window.CKEDITOR_CONFIG_STYLES_SET = [
    { name: 'Streepje', element: '&shy;' },
    { name: 'Subtitle', element: 'small' },
    { name: 'Grid - row', element: 'div', attributes: { 'class': 'row' } },
    { name: 'Grid - col-md-1', element: 'div', attributes: { 'class': 'col-md-1' } },
    { name: 'Grid - col-md-2', element: 'div', attributes: { 'class': 'col-md-2' } },
    { name: 'Grid - col-md-3', element: 'div', attributes: { 'class': 'col-md-3' } },
    { name: 'Grid - col-md-4', element: 'div', attributes: { 'class': 'col-md-4' } },
    { name: 'Grid - col-md-6', element: 'div', attributes: { 'class': 'col-md-6' } },
    { name: 'Grid - col-md-8', element: 'div', attributes: { 'class': 'col-md-8' } },
    { name: 'Grid - col-md-10', element: 'div', attributes: { 'class': 'col-md-10' } },
    { name: 'Grid - col-md-12', element: 'div', attributes: { 'class': 'col-md-12' } }
];


// Check if Fiber is live on this page
if (document.getElementById('wpr-body')) {
  // Use jQuery as $ variable
  (function ($) {
    /*
     Disable some Fiber functions when all functions (the whole document) is loaded
     */
    $(document).ready(function(){
      // Prevent element dragging
      $('.ui-draggable').draggable("destroy");
      
      // Create variable to improve page speed
      var contentdiv =$("div[data-fiber-data].content");
  
      // Prevent from adding new elements
      if ((2 * contentdiv.length) == $("div[data-fiber-data]").length) {
        // Remove completely if all elements contain valid contents
        $("#df-wpr-layer").remove();
        
      } else {
        // If still some elements are empty, only show the add-buttons on those elements
        // and NOT on the already existing content items
        contentdiv.mouseenter(function () {
          $("#df-wpr-layer").css('display', 'none');
        });
        contentdiv.mouseleave(function () {
          $("#df-wpr-layer").css('display', 'block');
        });
        
        // Create a tooltip on the add-buttons, to inform the user which block they're going to edit
        $("div[data-fiber-data]:not(.content)").mouseenter(function () {
          if($(this).children().length == 0){
            // Get JSON data from the div and put it in an object
            var json = $(this).attr('data-fiber-data');
            json = JSON.parse(json);
            
            // Set a tooltip on those add-buttons by setting the tile of the div containing the buttons
            $("#df-wpr-layer").attr('title', "Add " + json.block_name);
          }
        });
        
      }
    });
  })(window.jQuery);
}