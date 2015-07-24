var React = require('react');
var _ = require('underscore');

/**
 * Expects a property data=[{}]
 */
module.exports = React.createClass({


  getDefaultProps: function() {
    return {
      // by default use identity
      transform: (x) => x,
    };
  },

  render: function() {
    var data = this.props.transform(this.props.data);
    if(data.length > 0) {
      // map the first row's keys to a tr
      var heads = _.chain(data[0]).keys().map((k) => <td>{k}</td>);

      // map the data to a table
      return (
        <Table>
          <thead>
            <tr>
            { heads }
            </tr>
          </thead>
          <tbody>
          {
            // maps the rows to the trs
            data.map((row, i) =>
              <tr>
              {
                _(row).map((value, key) => <td key={key}>{value}</td>)
              }
              </tr>
            )
          }
          </tbody>
        </Table>
      );
    } else {
      return <div></div>;
    }
  }
});
