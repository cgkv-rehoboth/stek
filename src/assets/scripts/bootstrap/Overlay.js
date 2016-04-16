import React, {Component, PropTypes} from 'react';
import Icon from 'bootstrap/Icon';

export default class Overlay extends Component {
  
  static get propTypes() {
    return {
      width: PropTypes.any,
      onClose: PropTypes.func.isRequired
    }
  }

  static get defaultProps() {
    return {
      width: '50%'
    };
  }

  render() {
    let {width} = this.props;
    return <div className="overlay" onClick={this.props.onClose}>
      <div className="overlay-content" style={{width: width}}
           onClick={(e) => e.stopPropagation()}>
        <button onClick={this.props.onClose} className="btn-trans overlay-close">
          <Icon name="close" className="fa-2x"/>
        </button>
        {this.props.children}
      </div>
    </div>;
  }
}
