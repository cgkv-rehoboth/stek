let React = require("react");
let _ = require('underscore');

class Table extends React.Component {
  render() {
    return <table className="table table-hover table-striped table-bordered">
       {this.props.children}
    </table>;
  }
}

module.exports = {
  Table, Table
};
