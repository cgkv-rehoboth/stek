import React from "react";
import Time from 'react-time'
import _ from 'underscore';
import api from 'api';
import forms from 'bootstrap/forms';
import $ from "jquery";
import { Table } from 'bootstrap/tables';
import Icon from 'bootstrap/Icon';
import moment from 'moment'

export default class ServiceTableDashboard extends React.Component {

  static get propTypes() {
    return {
      data: React.PropTypes.array,
      is_private: React.PropTypes.bool
    };
  }

  render() {

    let renderServiceRow = (serv) => {
      let starttime = moment(serv.startdatetime).format('H:mm');
      let startdate = moment(serv.startdatetime).format('dddd D MMMM');
      let hiddeninfo = serv.minister + (serv.comments && serv.comments.length > 0 ? " - " +serv.comments : "");
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
        var typeC = file.type;
        var typeI = file.type;

        if (typeC) {
          typeC += '-';
          typeI += ', ';
        }

        return (<a className="service-file-download" href={file.file} target="_blank" title={"Download '" + file.title + "' ("+ typeI + file.filesize + ")"}><i className={"fa fa-file-" + typeC + "o"} aria-hidden="true"></i></a>);
      };

      let renderFilesHidden = (file) => {
        var typeC = file.type;
        var typeI = file.type;

        if (typeC) {
          typeC += '-';
          typeI += ', ';
        }

        return (
          <a className="service-file-download" href={file.file} target="_blank" title={"Download '" + file.title + "' ("+ typeI + file.filesize + ")"}>
            <i className={"fa fa-file-" + typeC + "o fa-fw"} aria-hidden="true"></i>
            {file.title} <small>({file.filesize})</small>
          </a>);
      };

      let files = _.map(serv.files, renderFiles);
      let filesHidden = _.map(serv.files, renderFilesHidden);

      let title = this.props.is_private ? <a href={serv.url}>{serv.title}</a> : serv.title;

      return ([
        <tr key={serv.id} className="serviceRow" onClick={onClick.bind(this)}>
          <td>{title}</td>
          <td><span className="service-starttime">{starttime}</span> - {startdate}</td>
          <td className="serviceHideOnSmallScreen">{serv.minister}</td>
          <td className="serviceInfoIcon">{html}</td>
          <td className="serviceHideOnSmallScreen">{serv.comments}</td>
          <td className="serviceHideOnSmallScreen">{files}</td>
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

    let rows = _.map(this.props.data, renderServiceRow);

    return (
      <Table renderRow={renderServiceRow}>
        <thead>
        <tr>
          <th>Dienst</th>
          <th>Datum</th>
          <th className="serviceHideOnSmallScreen">Voorganger</th>
          <th></th>
          <th className="serviceHideOnSmallScreen"></th>
          <th className="serviceHideOnSmallScreen"></th>
        </tr>
        </thead>
        <tbody>
        {rows}
        </tbody>
      </Table>
    );
  }
}