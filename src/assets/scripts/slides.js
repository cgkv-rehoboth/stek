var { Model, Collection } = require('backbone');
var constants = require('../constants');

var Slide = Model.extend({
  url: constants.api.slides
});


var SlideList = Collection.extend({
  model: Slide,
  url: constants.api.slides
});

var Slides = new SlideList();

module.exports = {
  SlideList: SlideList,
  Slides: Slides
};
