import React, {Component, PropTypes} from 'react';
import _ from 'underscore';
import $ from "jquery";
import ReactDom from "react-dom";

/**
 * React component for a Play button to control the React LivePlayer component
 */
export class LiveButton extends React.Component {

  static get propTypes() {
    return {
      text: React.PropTypes.string,
      player: React.PropTypes.instanceOf(LivePlayer).isRequired
    };
  }

  constructor(props) {
    super(props);

    this.props.player.registerButton(this);
  }

  onClick(e){
    let {player} = this.props;
    // Check if browser can play, otherwise let the button be a URL
    if(player.canPlayType('audio/mpeg')) {
      // Prevent URL action
      e.preventDefault();

      // Toggle player
      player.toggle();
    }
  }

  htmlText(html){
    // Render pure HTML
    return {__html: html};
  }

  render() {
    let {player} = this.props;

    // Figure out which icon needs to be displayed
    let html;
    if(player.state.isloading) {
      html = <i className="fa fa-circle-o-notch fa-spin fa-fw luisteren-i" ariaHidden="true"></i>;
    }else if(player.state.isplaying){1
      html = <i className="fa fa-pause fa-fw luisteren-i" ariaHidden="true"></i>;
    }else if(player.state.islive){
      html = <i className="fa fa-play fa-fw luisteren-i" ariaHidden="true"></i>;
    }else{
      html = false
    }

    return (
      <div onClick={this.onClick.bind(this)} className="luisteren-button" >
        {this.props.text}
        {html}
      </div>
    );
  }
}

/**
 * React component to play an audio stream. This player could be controlled by a
 * React LiveButton component
 */
export class LivePlayer extends React.Component {

  static get propTypes() {
    onDataLoaded: PropTypes.func
  }

  constructor(props) {
    super(props);

    this.state = {
      isplaying: false,
      islive: false,
      isloading: false
    };

    this.buttons = [];
  }

  componentDidMount() {
    // Do once the component is rendered:
    // Get player
    var player = this.refs.luisterenObject;

    // Add eventListeners to player
    player.addEventListener('playing', () => this.onplaying());
    player.addEventListener('pause', () => this.onpause());
    player.addEventListener('ended', () => this.onended());
    player.addEventListener('waiting', () => this.onwaiting());
    player.addEventListener('stalled', () => this.onstalled());
    player.addEventListener('suspend', () => this.onstalled());
    player.addEventListener('error', () => this.onerror());
    player.addEventListener('emptied', () => this.onerror());
    player.addEventListener('durationchange', () => this.ondurationchange());
    player.addEventListener('loadstart', () => this.onloadstart());
    player.addEventListener('loadeddata', () => this.onloadeddata());
  }

  /*
   * EventListeners
   */

  onplaying(){
    console.debug("Media is playing...");
    this.setState({
      isplaying: true,
      isloading: false
    });
  }

  onpause(){
    console.debug("Media has been paused...");
    this.setState({
      isplaying: false,
      isloading: false
    });
  }

  onended(){
    console.debug("Media has ended...");
    this.setState({
      isplaying: false
    });
  }

  onwaiting(){
    console.debug("Media is waiting (buffering?)...");
    this.setState({
      isplaying: false
    });
  }

  onstalled(){
    console.debug("Media has stalled...");
    this.setState({
      isplaying: false
    });
  }

  onerror(){
    console.debug("Media has an error...");
    this.setState({
      isplaying: false
    });
  }

  ondurationchange(){
    console.debug("Media length has changed...");

    /* Info:
     *   if(player.duration == 13.212) -> dienst is NIET live
     *   if(player.duration == Infinity) -> dienst is live
     */

    this.setState({
      islive: !(this.duration() < 20)
    });
  }

  onloadstart(){
    console.debug("Media is loading...");

    this.setState({
      isloading: true
    });
  }

  onloadeddata(){
    console.debug("Media is loaded...");

    this.setState({
      isloading: false
    });

    if(this.state.islive) {
      this.props.onDataLoaded();
    }
  }

  /*
   * Actions
   */

  play() {
    this.refs.luisterenObject.play();
  }

  pause() {
    this.refs.luisterenObject.pause()
  }

  load() {
    this.refs.luisterenObject.load();
  }

  canPlayType(type) {
    return this.refs.luisterenObject.canPlayType(type);
  }

  toggle(){
    if(this.state.isplaying){
      this.pause();
    }else{
      this.load();
      this.play();
    }
  }

  duration(){
    return this.refs.luisterenObject.duration;
  }

  componentDidUpdate(){
    // Update play buttons
    $.each(this.buttons, function(i, v){
      v.forceUpdate();
    });
  }

  registerButton(button){
    console.debug("Registering button...");
    this.buttons.push(button);
  }

  render() {
    return (
      <audio id="luisteren-audio" ref="luisterenObject" loop preload="metadata">
        <source src="http://kerkdienstgemist.nl/streams/267.mp3" type="audio/mpeg" />
      </audio>
    );
  }
}
