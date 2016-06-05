import React from "react";
import Time from 'react-time'
import _ from 'underscore';
import api from 'api';
import forms from 'bootstrap/forms';
import $ from "jquery";
import { PaginatedTable, SearchTable } from 'bootstrap/tables';
import Icon from 'bootstrap/Icon';
import moment from 'moment'

export default class ServiceTable extends React.Component {

  static get propTypes() {
    return {
      listFunc: React.PropTypes.func.isRequired // (searchText, page) => promise<[item]>,
    };
  }

  render() {
    let renderServiceRow = (serv) => {
      let starttime = moment(serv.startdatetime).format('H:mm');
      let startdate = moment(serv.startdatetime).format('dddd D MMMM');

      return (
        <tr key={serv.id}>
          <td>{serv.title}</td>
          <td><span className="service-starttime">{starttime}</span> - {startdate}</td>
          <td>{serv.minister}</td>
          <td>{serv.comments}</td>
        </tr>
      );
    };
    
    return (
      <SearchTable listFunc={this.props.listFunc} renderRow={renderServiceRow} search={false}>
        <tr>
          <th>Dienst</th>
          <th>Datum</th>
          <th>Voorganger</th>
          <th></th>
        </tr>
      </SearchTable>
    );
  }
}
