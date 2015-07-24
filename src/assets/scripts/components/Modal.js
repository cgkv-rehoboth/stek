var React = require('react');

var Carousel = React.createClass({

  mixins: [BackboneComponent],

  getCollections: function() {
    return [this.props.slides]
  },

  render: function() {
    return <Boot.Carousel>
      {
        this.props.slides.map((x, i) =>
          <Boot.CarouselItem key={i}>
            <img src={x.get('image')}/>
            <div className="carousel-caption">
              <h3>{x.get('title')}</h3>
              <p>{x.get('description')}</p>
            </div>
          </Boot.CarouselItem>
        )
      }
    </Boot.Carousel>;
  }
});

module.exports = Carousel;

