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
        console.debug("Favorite unset");

        this.setState({
          favorite: false
        });
      });
    else
      return api.profiles.favorite(this.props.pk)
      .then((data) => {
        console.debug("Favorite set");

        this.setState({
          favorite: true
        });
      });
  }

  render() {
    let starFill = "fa fa-star" + (this.state.favorite ? '' : '-o');

    return <div className="addressbook-favorite" onClick={this.toggleFavorite.bind(this)}>
            <i className={starFill}></i>
            <i className="fa fa-star-half-o"></i>
          </div>;
  }
}