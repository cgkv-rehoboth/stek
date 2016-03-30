import React, {Component, PropTypes} from 'react';

export default class Async extends Component {

  static get propTypes() {
    return {
      promise: PropTypes.object.isRequired,
      then: PropTypes.func.isRequired
    };
  }

  constructor(props) {
    super(props);

    this.state = {value: undefined};

    props.promise
      .then((value) => {this.setState({value: value});})
      .done();
  }

  render() {
    if(this.state.value) {
      return this.props.then(this.state.value);
    } else {
      return false;
    }
  }
}
