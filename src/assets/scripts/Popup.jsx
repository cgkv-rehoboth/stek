import React, {Component, PropTypes} from 'react';
import _ from 'underscore';
import $ from "jquery";
import ReactDom from "react-dom";

class Popup extends React.Component {

  onClick(){
    $(".popup").fadeOut(500);
  }

  componentDidMount(){
    setTimeout(function(){
      $(".popup").fadeIn(900);
    }, 1200);
  }

  render() {
    return <div className="popup">
      <span className="popup-close"><i onClick={this.onClick.bind(this)} className="fa fa-times-circle" ariaHidden="true"></i></span>
      <div className="popup-content">{this.props.children}</div>
    </div>;
  }
}


module.exports = Popup;