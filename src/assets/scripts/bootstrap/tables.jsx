let React = require("react");
let _ = require('underscore');

class Table extends React.Component {
  render() {
    return <table className="table table-hover table-striped table-bordered">
       {this.props.children}
    </table>;
  }
}

class PaginatedTable extends React.Component {

  static get propTypes() {
    return {
      pageno: React.PropTypes.number,
      hasPrev: React.PropTypes.bool,
      hasNext: React.PropTypes.bool,
      onPageChange: React.PropTypes.func.isRequired
    };
  }

  render() {
    let prevButton = this.props.hasPrev
          ? <button onClick={() => this.props.onPageChange(this.props.pageno-1)}>
              <i className="fa fa-chevron-left" /></button>
          : null;
    let nextButton = this.props.hasNext
          ? <button onClick={() => this.props.onPageChange(this.props.pageno+1)}>
              <i className="fa fa-chevron-right" /></button>
          : null;

    return <div>
      <Table>
        {this.props.children}
      </Table>
      <div>
        {prevButton}
        <button>{this.props.pageno}</button>
        {nextButton}
      </div>
    </div>;
  }
}

module.exports = {
  Table: Table,
  PaginatedTable: PaginatedTable
};
