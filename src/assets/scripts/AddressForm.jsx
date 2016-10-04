import React, {Component, PropTypes} from 'react';
import _ from 'underscore';
import $ from "jquery";
import ReactDom from "react-dom";

export default class AddressForm extends React.Component {

  static get propTypes() {
    return {
      listFunc: React.PropTypes.func,
      address: React.PropTypes.object,
    };
  }

  // done: zip retrieval
  // done: phone retrieval by house number
  // done: when address change, show extra question
  // done: zip fill in fields

  checkChanges(e){
    // Check if address isn't the same as the saved address
    let fields = ['zip', 'number', 'street', 'city', 'country'];  // Fields to compare
    let c = true;
    let address = this.state.address;
    let item = this.state.item;

    fields.forEach(function(f){
      c &= item[f].toUpperCase() == address[f].toUpperCase();
    });

    this.setState({
      verhuizing: !c,
    });
  }

  constructor(props) {
    super(props);

    // Default address
    let address = {
      zip : '',
      number : '',
      street : '',
      city : 'Woerden',
      country: 'Nederland',
      phone: ''
    };

    // Deep copy 0_o
    let items = [ jQuery.extend([], address) ]; // Make this one array like

    if (this.props.address) {
      // Override default address
      address = this.props.address;

      items = [ jQuery.extend([], address) ]; // Make this one array like

      // Seperate streetname and number
      let str = address.street.split(' ');
      address.number = str.pop();
      address.street = str.join(' ');
    }

    // Deep copy 0_o
    let item = jQuery.extend([], address);

    this.checkChanges = this.checkChanges.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.handleChangeRestricted = this.handleChangeRestricted.bind(this);
    this.onBlur = this.onBlur.bind(this);
    this.onPhoneBlur = this.onPhoneBlur.bind(this);
    this.onNumberBlur = this.onNumberBlur.bind(this);
    this.onZipBlur = this.onZipBlur.bind(this);

    // Load current zip addresses
    this.loadItems(item.zip);

    this.state = {
      items: items,
      item: item,
      address: address,
      verhuizing: false,
      newzip: (address.zip == ''),  // Check if zip already is filled in
    };
  }

  handleChange(e){
    let item = this.state.item;
    item[e.target.name] = e.target.value; // Change value

    // Save and display it
    this.setState({
      item: item,
    });
  }

  handleChangeRestricted(e){
    // Only edittable if permitted
    if (this.state.newzip){
      this.handleChange(e);
    }
  }

  loadItems(zip){
    // Display loading icon
    $("#zip-input-field").addClass('input-group');
    $("#loading-addon").css('display', 'table-cell');

    // Retrieve addresses
    this.props.listFunc(zip)
      .then((data) => {

        // Remove loading icon
        $("#loading-addon").css('display', 'none');
        $("#zip-input-field").removeClass('input-group');


        let items = data.data.results;  // Load al items from the server into this var
        let item = this.state.item;     // Get current item
        let newzip = false;             // Make restricted fields non-editable

        if (items.length == 1){
          // Fill in everything
          item = jQuery.extend([], items[0]);

          // Seperate streetname and number
          let str = item.street.split(' ');
          item.number = str.pop();
          item.street = str.join(' ');
        }else if(items.length > 1){
          // Got a whole bunch of them, get only the streetname
          let val = jQuery.extend([], items[0]);

          // Seperate streetname and number
          let str = val.street.split(' ');
          val.number = str.pop();
          val.street = str.join(' ');

          // Save values to Item
          item.zip = val.zip;
          item.street = val.street;
          item.city = val.city;
          item.country = val.country;
        }else{
          // Nothing found
          // Make restricted fields editable
          newzip = true;
        }

        this.setState({
          items: items,
          item: item,
          newzip: newzip,
        });

        this.checkChanges(e);
      });
  }

  onBlur(e){
    this.checkChanges(e);
  }

  onPhoneBlur(e){
    // Remove all whitespaces (because they're unnecessary)
    e.target.value = e.target.value.replace(/\s/g, "");
    this.handleChange(e);
  }

  onNumberBlur(e){
    // Remove all whitespaces (because they're unnecessary)
    e.target.value = e.target.value.replace(/\s/g, "").toUpperCase();
    this.handleChange(e);

    let str = e.target.value;

    // Find address with this numer in itmes list
    let r = this.state.items.find(function(i){
      // Get house number
      let number = i.street.split(' ').pop();

      // Compare
      return (str == number);
    });

    // Fill in fields
    let item = this.state.item;

    if(r && !(r.phone == null)) {
      item.phone = r.phone;
    }// else do nothing

    this.setState({
      item: item,
    });

    this.checkChanges(e);
  }

  onZipBlur(e){
    // Remove all whitespaces (because they're unnecessary)
    e.target.value = e.target.value.replace(/\s/g, "").toUpperCase();
    this.handleChange(e);

    this.checkChanges(e);

    let zip = e.target.value;

    // Retrieve list of matching addresses
    this.loadItems(zip);
  }

  render() {
    if (this.state.verhuizing){
      $("#profile-verhuizing").slideDown(300);
    }else{
      $("#profile-verhuizing").slideUp(300);
    }

    // Use readOnly, because disabled inputs don't send POST data!
    let readonly = !this.state.newzip;

    return (<div>
      <div className="form-group">
        <label className="col-sm-3">Postcode</label>
        <div className="col-sm-9">
          <div id="zip-input-field">
            <input
              value={this.state.item.zip}
              onChange={this.handleChange}
              onBlur={this.onZipBlur}
              placeholder="bijv. 3443BZ"
              name="zip"
              type="text"
              className="form-control" />
            <span className="input-group-addon" id="loading-addon"><i className="fa fa-circle-o-notch fa-spin fa-fw"></i> Gegevens ophalen...</span>
          </div>
        </div>
      </div>
      <div className="form-group">
        <label className="col-sm-3">Huisnummer</label>
        <div className="col-sm-9">
          <input
            value={this.state.item.number}
            onChange={this.handleChange}
            onBlur={this.onNumberBlur}
            placeholder="bijv. 130"
            name="number"
            type="text"
            className="form-control" />
        </div>
      </div>
      <div className="form-group">
        <label className="col-sm-3">Straat</label>
        <div className="col-sm-9">
          <input
            value={this.state.item.street}
            onChange={this.handleChange}
            onBlur={this.onBlur}
            placeholder="bijv. Leidsestraatweg"
            name="street"
            type="text"
            className="form-control" readOnly={readonly} />
        </div>
      </div>
      <div className="form-group">
        <label className="col-sm-3">Stad</label>
        <div className="col-sm-9">
          <input
            value={this.state.item.city}
            onChange={this.handleChange}
            onBlur={this.onBlur}
            placeholder="bijv. Woerden"
            name="city"
            type="text"
            className="form-control" readOnly={readonly} />
        </div>
      </div>
      <div className="form-group">
        <label className="col-sm-3">Land</label>
        <div className="col-sm-9">
          <input
            value={this.state.item.country}
            onChange={this.handleChange}
            onBlur={this.onBlur}
            placeholder="bijv. Nederland"
            name="country"
            type="text"
            className="form-control" readOnly={readonly} />
        </div>
      </div>
      <div className="form-group">
        <label className="col-sm-3">Huistelefoon</label>
        <div className="col-sm-9">
          <input
            value={this.state.item.phone}
            onChange={this.handleChange}
            onBlur={this.onPhoneBlur}
            placeholder="bijv. 0348-411830"
            name="phone"
            type="phone"
            className="form-control" />
        </div>
      </div>

      <div className="form-group profile-hidden" id="profile-verhuizing">
        <label className="col-sm-3">Wie verhuist mee?</label>
        <div className="col-sm-9">
          <input type="hidden" name="verhuizing" value={this.state.verhuizing} />
          <select
            name="verhuizing-options"
            className="form-control" >
            <option value="1">Alleen ik</option>
            <option value="2">Ook familieleden</option>
          </select>
        </div>
      </div>
    </div>);
  }
}
