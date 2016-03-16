import React from "react";
import {Button} from 'bootstrap/buttons';
import Icon from 'bootstrap/Icon';
import _ from 'underscore';

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
        <div className="btn-group">
          {prevButton}
          <Button>{this.props.pageno}</Button>
          {nextButton}
        </div>
      </div>
    </div>;
  }
}

export class SearchTable extends React.Component {

  static get propTypes() {
    return {
      listFunc: React.PropTypes.func.isRequired, // (searchText, page) => promise<[item]>,
      renderRow: React.PropTypes.func.isRequired
    };
  }

  constructor(props) {
    super(props);
    this.state = {
      items: [],
      page: 0,
      hasPrev: false,
      hasNext: false
    };
  }

  loadItems(searchtext="", page=1) {
    // load initial profiles
    return this.props.listFunc(searchtext, page)
      .then((data) => {
        this.setState({
          items: data.data.results,
          page: data.data.pageno,
          hasPrev: data.data.previous !== null,
          hasNext: data.data.next !== null
        });
      });
  }

  componentWillMount() {
    this.loadItems();
  }

  searchChange(e) {
    let text = $(e.target).val();
    this.setState({ query: text, page: 1});
    this.loadItems(text, this.state.page);
  }

  pageChange(page) {
    this.setState({ page: page});
    this.loadItems(this.state.query, page);
  }

  render() {
    let { renderRow } = this.props;
    let rows = _.map(this.state.items, renderRow);

    return (
      <div className="profile-search-table">
        <div>
          <Icon name="search" />
          <input type="text" onChange={_.debounce(this.searchChange.bind(this), 1000)} />
        </div>
        <PaginatedTable
          pageno={this.state.page}
          onPageChange={this.pageChange.bind(this)}
          hasPrev={this.state.hasPrev}
          hasNext={this.state.hasNext}>
          <tbody>
            {rows}
          </tbody>
        </PaginatedTable>
      </div>
    );
  }
}
