import React, {Component, PropTypes} from 'react';
import moment from 'moment';
import cn from 'classnames';

export class Row extends Component {
  render() {
    return <div {...this.props} className="row">{this.props.children}</div>;
  }
}

export class Col extends Component {
  static get propTypes() {
    return {
      type: PropTypes.string.isRequired
    };
  }

  render() {
    let {type, className} = this.props;
    let clz = cn(`col-${type}`, className);
    return <div {...this.props} className={clz}>{this.props.children}</div>;
  }
}
