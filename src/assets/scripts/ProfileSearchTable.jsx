import React from "react";
import _ from 'underscore';
import api from 'api';
import forms from 'bootstrap/forms';
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
    ? <a href={"/adresboek/families/" + prof.family.id + "/"}>{prof.prefix} {prof.last_name}</a>
    : family = <span></span>;

    let phone = prof.phone
        ? <span>{prof.phone} <a href={"tel:" + prof.phone} className="make-contact-icon" title={"Bel " + prof.first_name}><i className="fa fa-phone" aria-hidden="true"></i></a></span>
        : <span></span>;

    let email = prof.email
        ? <span>{prof.email} <a href={"mailto:" + prof.email} className="make-contact-icon" title="Verstuur een e-mail"><i className="fa fa-envelope-o" aria-hidden="true"></i></a></span>
        : <span></span>;

    return (
    <tr key={prof.id}>
      <td>{prof.initials}</td>
      <td><a href={"/profiel/" + prof.id + "/"}>{prof.first_name}</a></td>
      <td>{family}</td>
      <td>{phone}</td>
      <td>{email}</td>
      <td><FavStar pk={prof.id} favorite={prof.is_favorite}></FavStar></td>
    </tr>
    );
  };

  return <SearchTable listFunc={this.props.listFunc} renderRow={renderProfileRow} />;
  }
}
