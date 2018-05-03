import React from "react";
import api from 'api';

export default class FavStar extends React.Component {

  static get propTypes() {
    return {
      pk: React.PropTypes.number.isRequired,
      favorite: React.PropTypes.bool.isRequired
    };
  }

  constructor(props) {
    super(props);
    this.state = {
      favorite: props.favorite
    };
  }

  toggleFavorite(){
    if(this.state.favorite)
      return api.profiles.defavorite(this.props.pk)
      .then((data) => {

        this.setState({
          favorite: false
        });
      });
    else
      return api.profiles.favorite(this.props.pk)
      .then((data) => {

        this.setState({
          favorite: true
        });
      });
  }

  render() {
    let starFill = "fa fa-star" + (this.state.favorite ? '' : '-o');
    let title = "Klik hier om als favoriet " + (this.state.favorite ? 'te verwijderen' : 'toe te voegen');

    return <div className="addressbook-favorite" onClick={this.toggleFavorite.bind(this)} title={title}>
            <i className={starFill}></i>
            <i className="fa fa-star-half-o"></i>
          </div>;
  }
}
