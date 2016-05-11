import React from "react";
import Time from 'react-time'
import _ from 'underscore';
import api from 'api';
import forms from 'bootstrap/forms';
import $ from "jquery";
import { PaginatedTable, SearchTable } from 'bootstrap/tables';
import Icon from 'bootstrap/Icon';

export default class ServiceTable extends React.Component {

  static get propTypes() {
    return {
      listFunc: React.PropTypes.func.isRequired // (searchText, page) => promise<[item]>,
    };
  }

  render() {
    let renderServiceRow = (serv) => {
      let startdate = new Date(serv.startdatetime)

      return (
        <tr key={serv.id}>
          <td>{serv.title}</td>
          <td><Time value={startdate} format="HH:mm YYYY/MM/DD" /></td>
          <td>{serv.minister}</td>
        </tr>
      );
    };
    
    return <SearchTable listFunc={this.props.listFunc} renderRow={renderServiceRow} />;
  }
}
