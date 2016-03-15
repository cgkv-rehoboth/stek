import React from "react";
import {Button} from 'bootstrap/buttons';
import Icon from 'bootstrap/Icon';

export class Table extends React.Component {
  render() {
    return <table className="table table-hover table-striped table-bordered">
       {this.props.children}
    </table>;
  }
}

export class PaginatedTable extends React.Component {

  static get propTypes() {
    return {
      pageno: React.PropTypes.number,
      hasPrev: React.PropTypes.bool,
      hasNext: React.PropTypes.bool,
      onPageChange: React.PropTypes.func.isRequired
    };
  }

  render() {
    let prevButton = 
          <Button
            onClick={() => this.props.onPageChange(this.props.pageno-1)}
            disabled ={!this.props.hasPrev}
          ><Icon name="chevron-left" /></Button>;
    let nextButton =
          <Button
             onClick={() => this.props.onPageChange(this.props.pageno+1)}
             disabled={!this.props.hasNext}
          ><Icon name="chevron-right" /></Button>;

    return <div className="paginated-table">
      <Table>
        {this.props.children}
      </Table>
      <div className="pages">
        <div>
          {prevButton}
          <Button>{this.props.pageno}</Button>
          {nextButton}
        </div>
      </div>
    </div>;
  }
}
