// jQuery 4 life
let $ = require('jquery');

// bind global jquery instance
window.jQuery = $;
window.$ = $;

// some global injections
let _easing = require('jquery.easing');

// make sure bootstrap is loaded
let _bootstrap = require('bootstrap/dist/js/bootstrap.min');
require('bootstrap/js/tooltip');

// theming thingies
let _theme = require('./lib/grayscale');

function _initForms($form) {
  let data = $form.serializeArray();
  console.log(data);
}

// api
let api = require('api');
api.duties.list().then((data) => console.log(data));

// init bootstrap tooltips
console.log($('[data-toggle="tooltip"]'));
$(() => console.log("HI!"));
$(() => $('[data-toggle="tooltip"]').tooltip());
