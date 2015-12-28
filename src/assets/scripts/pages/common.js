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
let _theme = require('lib/grayscale');
