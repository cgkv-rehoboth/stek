import React, {Component, PropTypes} from 'react';

export default class Icon extends Component {

  static get propTypes() {
    return {
      name: PropTypes.string.isRequired
    };
  }

  render() {
    return <i className={`fa fa-${this.props.name} ${this.props.className}`}></i>;
  }
}
