import React, {Component, PropTypes} from "react";

export class Button extends Component {
  render() {
    return (
      <button {...this.props} className={`btn btn-default`}>
        {this.props.children}
      </button>
    );
  }
}
