import React from "react";
import _ from 'underscore';
import api from 'api';
import forms from 'forms';
import $ from "jquery";
import { PaginatedTable, SearchTable } from 'bootstrap/tables';
import FavStar from 'containers/FavStar';
import Icon from 'bootstrap/Icon';

export default class ProfileSearchTable extends React.Component {

  static get propTypes() {
    return {
      listFunc: React.PropTypes.func.isRequired // (searchText, page) => promise<[item]>,
    };
  }

  render() {
    let renderProfileRow = (prof) => {
     // render some nested optional properties
     let family = prof.family
      ? <a href={"/adresboek/families/" + prof.family.id + "/"}>{prof.user.last_name}</a>
      : family = <span></span>;
     let address = prof.address
      ? <td>prof.address.street + <small>({prof.address.zip})</small></td>
      : <td></td>;
     let city = prof.address
      ? <td>prof.address.city</td>
      : <td></td>;

     return (
      <tr key={prof.id}>
        <td><a href={"/profiel/" + prof.id + "/"}>{prof.user.first_name}</a></td>
        <td>{family}</td>
        {address}
        {city}
        <td>{prof.phone}</td>
        <td>{prof.user.email}</td>
        <td><FavStar pk={prof.id} favorite={prof.is_favorite}></FavStar></td>
      </tr>
     );
    };
    
    return <SearchTable listFunc={this.props.listFunc} renderRow={renderProfileRow} />;
  }
}
