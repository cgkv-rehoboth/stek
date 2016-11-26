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

      let renderFiles = (file) => {
        console.log(file)
        var typeC = file.type;
        var typeI = file.type;

        if (typeC) {
          typeC += '-';
          typeI += ', ';
        }

        return (<a className={"service-file-download sf-public-" + file.is_public} href={file.file} target="_blank" title={"Download '" + file.title + "' ("+ typeI + file.filesize + ")"}><i className={"fa fa-file-" + typeC + "o"} aria-hidden="true"></i></a>);
      }

      let renderFilesHidden = (file) => {
        console.log(file)
        var typeC = file.type;
        var typeI = file.type;

        if (typeC) {
          typeC += '-';
          typeI += ', ';
        }

        return (
          <a className={"service-file-download sf-public-" + file.is_public} href={file.file} target="_blank" title={"Download '" + file.title + "' ("+ typeI + file.filesize + ")"}>
            <i className={"fa fa-file-" + typeC + "o fa-fw"} aria-hidden="true"></i>
            {file.title} <small>({file.filesize})</small>
          </a>);
      }

      let files = _.map(serv.files, renderFiles);
      let filesHidden = _.map(serv.files, renderFilesHidden);

      return ([
        <tr key={serv.id} className="serviceRow" onClick={onClick.bind(this)}>
          <td>{serv.title}</td>
          <td><span className="service-starttime">{starttime}</span> - {startdate}</td>
          <td className="serviceHideOnSmallScreen">{serv.minister}</td>
          <td className="serviceHideOnSmallScreen service-table-theme">{serv.theme}</td>
          <td className="serviceInfoIcon">{html}</td>
          <td className="serviceHideOnSmallScreen">{serv.comments}</td>
          <td className="serviceHideOnSmallScreen">{files}</td>
          <td>
            <span className="table-tools">
              <a href={"/roosters/diensten/" + serv.id + "/edit/"} title="Bewerken">
                <i className="fa fa-pencil-square-o fa-fw"></i></a>
              <a href={"/roosters/diensten/" + serv.id + "/delete/"} className="confirm-dialog-button" data-message="Weet je zeker dat je deze dienst wilt verwijderen?<br/><br/>De bijhorende bestanden worden niet automatisch verwijderd!" title="Verwijderen">
                <i className="fa fa-times fa-fw"></i>
              </a>
            </span>
          </td>
        </tr>,
        <tr className="serviceHiddenItems">
          <td colSpan="6">
            <div className="serviceHiddenDiv">
              <i className="fa fa-level-up fa-rotate-90" aria-hidden="true"></i>
              <div>{hiddeninfo}</div>
              <div className="serviceHiddenFiles">{filesHidden}</div>
            </div>
          </td>
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
          <th colSpan="2" className="serviceHideOnSmallScreen">Extra info</th>
          <th className="serviceHideOnSmallScreen"></th>
          <th className="serviceHideOnSmallScreen"></th>
          <th></th>
        </tr>
      </SearchTable>
    );
  }
}