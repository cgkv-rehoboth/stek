var React = require('react');

var BackboneComponent = {

  componentDidMount: function() {
    this.getCollections().forEach(
      (col) => { col.on('add remove change', this.forceUpdate.bind(this, null)) },
      this
    );
  },

  componentWillUnmount: function() {
    this.getCollections().forEach((col) => col.off(null, null, this), this)
  }

};

module.exports = BackboneComponent;
