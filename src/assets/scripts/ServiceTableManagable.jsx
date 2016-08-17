import React from "react";
import Time from 'react-time'
import _ from 'underscore';
import api from 'api';
import forms from 'bootstrap/forms';
import $ from "jquery";
import { PaginatedTable, SearchTable } from 'bootstrap/tables';
import Icon from 'bootstrap/Icon';
import moment from 'moment'

export default class ServiceTableManagable extends React.Component {

  static get propTypes() {
    return {
      listFunc: React.PropTypes.func.isRequired // (searchText, page) => promise<[item]>,
    };
  }

  render() {
    let renderServiceRow = (serv) => {
      let starttime = moment(serv.startdatetime).format('H:mm');
      let startdate = moment(serv.startdatetime).format('dddd D MMMM');
      let hiddeninfo = serv.minister + (serv.theme && serv.theme.length > 0 ? " - " +serv.theme : "") + (serv.comments && serv.comments.length > 0 ? " - " +serv.comments : "");
      let html = serv.comments && serv.comments.length > 0 ? <i className="fa fa-info-circle" ariaHidden="true"></i> : "";

      function onClick(e){
        // Get serviceHiddenItems row
        var tr = $(e.target).closest('tr').next();

        /* Toggle serviceHiddenItems */

        // (A) Only show one at a time
        if($(tr).css('display') == "none"){
          $(".serviceHiddenItems").hide();
          $(tr).show();
        }else{
          $(".serviceHiddenItems").hide();
        }

        /*
        // (B) Don't bother how many are shown at a time
        $(tr).toggle();
        */
      }

      return ([
        <tr key={serv.id} className="serviceRow" onClick={onClick.bind(this)}>
          <td>{serv.title}</td>
          <td><span className="service-starttime">{starttime}</span> - {startdate}</td>
          <td className="serviceHideOnSmallScreen">{serv.minister}</td>
          <td className="serviceHideOnSmallScreen service-table-theme">{serv.theme}</td>
          <td className="serviceInfoIcon">{html}</td>
          <td className="serviceHideOnSmallScreen">{serv.comments}</td>
          <td>
            <span className="table-tools">
              <a href={"/roosters/diensten/" + serv.id + "/edit/"} title="Bewerken">
                <i className="fa fa-pencil-square-o fa-fw"></i></a>
              <a href={"/roosters/diensten/" + serv.id + "/delete/"} className="confirm-dialog-button" data-message="Weet je zeker dat je dit rooster wilt verwijderen?" title="Verwijderen">
                <i className="fa fa-times fa-fw"></i>
              </a>
            </span>
          </td>
        </tr>,
        <tr className="serviceHiddenItems">
          <td colSpan="5"><div>{hiddeninfo}</div></td>
        </tr>
      ]);
    };
    
    return (
      <SearchTable listFunc={this.props.listFunc} renderRow={renderServiceRow} search={false}>
        <tr>
          <th>Dienst</th>
          <th>Datum</th>
          <th className="serviceHideOnSmallScreen">Voorganger</th>
          <th className="serviceHideOnSmallScreen">Thema</th>
          <th></th>
          <th></th>
          <th className="serviceHideOnSmallScreen"></th>
        </tr>
      </SearchTable>
    );
  }
}