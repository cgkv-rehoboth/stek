import React from "react";
import {Button} from 'bootstrap/buttons';
import Icon from 'bootstrap/Icon';
import _ from 'underscore';
import $ from 'jquery';

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
      onPageChange: React.PropTypes.func.isRequired,
      reverseTime: React.PropTypes.bool
    };
  }

  render() {
    let prevButton =
          <Button
            onClick={() => this.props.onPageChange(this.props.pageno + 1 * (this.props.reverseTime ? +1 : -1))}
            disabled ={!this.props.hasPrev}
          ><Icon name="chevron-left" /></Button>;
    let nextButton =
          <Button
             onClick={() => this.props.onPageChange(this.props.pageno - 1 * (this.props.reverseTime ? +1 : -1))}
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
      renderRow: React.PropTypes.func.isRequired,
      search: React.PropTypes.bool,
      reverseTime: React.PropTypes.bool
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

    // bind event handlers
    // this is way convoluted because react pools events...
    // ...so we have to persist the event before we pass it to the debounced function
    let debouncedSearchChange = _.debounce(this.searchChange.bind(this), 300);
    this.onSearchChange = (e) => { e.persist(); return debouncedSearchChange(e); }
  }

  loadItems(searchtext="", page=1) {
    // load initial profiles
    return this.props.listFunc(searchtext, page, this.props.reverseTime)
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
    let ev = e.nativeEvent;
    console.log("Made", ev);
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

    var search = ""
    if (!(this.props.search === false)) {
      search = (
        <div>
          <Icon name="search"/>
          <input type="text" onChange={this.onSearchChange}/>
        </div>
      );
    }


    return (
      <div className="profile-search-table">
        {search}
        <PaginatedTable
          pageno={this.state.page}
          onPageChange={this.pageChange.bind(this)}
          hasPrev={this.state.hasPrev}
          hasNext={this.state.hasNext}
          reverseTime={this.props.reverseTime}>
          <tbody>
            {this.props.children}
            {rows}
          </tbody>
        </PaginatedTable>
      </div>
    );
  }
}