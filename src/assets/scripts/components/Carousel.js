var React = require('react');

var Carousel = React.createClass({

  getCollections: function() {
    return [this.props.slides]
  },

  render: function() {
    return <Boot.Carousel>
      {
        this.props.slides.map((x, i) =>
          <Boot.CarouselItem key={i} style={{backgroundImage: 'url(' + x.get('image') + ')'}}>
            <div className="container">
              <div className="carousel-item-text-container">
                <div className="carousel-item-text">
                  <h3>{x.get('title')}</h3>
                  <span>{x.get('description')}</span>
                </div>
              </div>
            </div>
          </Boot.CarouselItem>
        )
      }
    </Boot.Carousel>;
  }
});

module.exports = Carousel;
