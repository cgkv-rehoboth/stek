import React from "react";
import _ from 'underscore';
import api from 'api';
import $ from "jquery";

export default class ProfileSearchInput extends React.Component {

  static get propTypes() {
    return {
      listFunc: React.PropTypes.func.isRequired // (searchText) => promise<[item]>, // todo: add specific filter (i.e. certain teammembers
    };
  }

  constructor(props){
    super(props);
    this.state = {
      items: [],
      selectedid: 0,
      inputvalue: "",
      openlist: false
    };

    // bind event handlers
    // this is way convoluted because react pools events...
    // ...so we have to persist the event before we pass it to the debounced function
    let debouncedSearchChange = _.debounce(this.searchChange.bind(this), 300);
    this.onSearchChange = (e) => { e.persist(); return debouncedSearchChange(e); };
    let debouncedDivBlur = _.debounce(this.divBlur.bind(this), 200);
    this.onDivBlur = () => { return debouncedDivBlur() };

    this.onHandleChange = this.handleChange.bind(this);
    this.onDivFocus = this.divFocus.bind(this);
  }

  divBlur(){
    this.setState({
      openlist: false
    });
  }

  divFocus(e){
    this.setState({
      openlist: true
    });
  }

  handleChange(e){
    let inputvalue = e.target.value.replace(/"/g, ''); // Change value

    // Get items from server
    this.onSearchChange(e);

    // Save and display the current value
    this.setState({
      selectedid: 0,
      inputvalue: inputvalue,
    });
  }

  itemClick(prof) {
    let name = prof.first_name + " " + ( prof.prefix.length > 0 ? prof.prefix + " " : "") + prof.last_name;

    // Set selected value
    this.setState({
      selectedid: prof.id,
      inputvalue: '"' + name + '"',
      openlist: false
    })
  }

  loadItems(searchtext="", page=1) {
    // load initial profiles
    return this.props.listFunc(searchtext, page)
      .then((data) => {
        this.setState({
          items: data.data.results,
          openlist: true
        });
      });
  }

  searchChange(e) {
    let text = $(e.target).val();

    this.setState({
      query: text,
      items: <span><i className="fa fa-refresh fa-spin"></i> Gegevens ophalen</span>,
      openlist: true
    });

    // Load items
    this.loadItems(text, this.state.page);
  }

  render() {

    let renderItem = (prof) => {
      return (
        <li key={prof.id} onClick={this.itemClick.bind(this, prof)}>
          {prof.first_name} {prof.prefix} {prof.last_name}
        </li>
      )
    };

    // Add rows / items to the itemlist
    let rows = "";
    if(this.state.items.constructor === Array) {
      rows = _.map(this.state.items, renderItem);
    }else {
      // ... or just text
      rows = <li>{this.state.items}</li>;
    }

    // Determine whether or not the itemlist should be visible or not
    let toggleclass = 'open';
    if(!this.state.openlist || rows == '')
      toggleclass = '';

    return (
      <div className={toggleclass} onBlur={this.onDivBlur} onFocus={this.onDivFocus}>
        <input type="hidden"
               name="profile"
               value={this.state.selectedid} />
        <input type="text"
               onChange={this.onHandleChange}
               value={this.state.inputvalue}
               placeholder="Naam"
               className="form-control" />
        <ul className="dropdown-menu">
          {rows}
        </ul>
      </div>
    );
  }
}
