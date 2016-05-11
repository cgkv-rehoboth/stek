import React, {Component, PropTypes} from 'react';
import _ from 'underscore';
import $ from "jquery";
import ReactDom from "react-dom";

class Popup extends React.Component {

  static get propTypes() {
    return {
      text: React.PropTypes.string
    };
  }

  onClick(e){
    $(".popup").fadeOut(500)
  }

  createMarkup() {
    return {__html: this.props.text};
  };

  componentDidMount(){
    $(".popup").fadeIn(900)
  }

  render() {
    return <div className="popup">
      <span className="popup-close"><i onClick={this.onClick.bind(this)} className="fa fa-times-circle" ariaHidden="true"></i></span>
      <div className="popup-content" dangerouslySetInnerHTML={this.createMarkup()}></div>
    </div>;
  }
}


module.exports = Popup;