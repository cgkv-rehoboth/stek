import React from "react";
import _ from 'underscore';
import $ from "jquery";
import ReactDom from "react-dom";

/**
 * React component for a Play button to control the React LivePlayer component
 */
export class LiveButton extends React.Component {

  constructor() {
    // Check if player exists
    if(!$("#luisteren-player")[0]){
      // Render player and make it global accessible
      $("#content").append('<div id="luisteren-player"></div>');
      window.player = ReactDom.render(<LivePlayer></LivePlayer>, $("#luisteren-player")[0]);
    }
  }

  onClick(e){
    // Check if browser can play, otherwise let the button be a URL
    if(window.player.canPlayType('audio/mpeg')) {
      // Prevent URL action
      e.preventDefault();

      // Toggle player
      window.player.toggle();
    }
  }

  htmlText(html){
    // Render pure HTML
    return {__html: html};
  }

  render() {
    // Figure out which icon needs to be displayed
    var html = "";
    if(window.player.state.isloading) {
      html = '<i class="fa fa-circle-o-notch fa-spin fa-fw luisteren-i" aria-hidden="true"></i>';
    }else if(window.player.state.isplaying){
      html = '<i class="fa fa-pause fa-fw luisteren-i" aria-hidden="true"></i>';
    }else if(window.player.state.islive){
      html = '<i class="fa fa-play fa-fw luisteren-i" aria-hidden="true"></i>';
    }

    return (
      <div onClick={this.onClick.bind(this)} className="luisteren-button" >
        {this.props.text}
        <span dangerouslySetInnerHTML={this.htmlText(html)} />
      </div>
    );
  }
}

/**
 * React component to play an audio stream. This player could be controlled by a
 * React LiveButton component, or via console commands
 */
export class LivePlayer extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      isplaying: false,
      islive: false,
      isloading: false
    };
  }

  componentDidMount() {
    // Do once the component is rendered:
    // Get player
    var player = this.refs.luisterenObject;

    // Add eventListeners to player
    player.addEventListener('playing', this.onplaying);
    player.addEventListener('play', this.onplay);
    player.addEventListener('pause', this.onpause);
    player.addEventListener('ended', this.onended);
    player.addEventListener('waiting', this.onwaiting);
    player.addEventListener('stalled', this.onstalled);
    player.addEventListener('suspend', this.onstalled);
    player.addEventListener('error', this.onerror);
    player.addEventListener('emptied', this.onerror);
    player.addEventListener('durationchange', this.ondurationchange);
    player.addEventListener('loadstart', this.onloadstart);
    player.addEventListener('loadeddata', this.onloadeddata);
  }

  /** EventListeners **/
  onplaying(){
    console.debug("Media is playing...");
    window.player.setState({
      isplaying: true,
      isloading: false
    });
  }

  onpause(){
    console.debug("Media has been paused...");
    window.player.setState({
      isplaying: false,
      isloading: false
    });
  }

  onended(){
    console.debug("Media has ended...");
    window.player.setState({
      isplaying: false
    });
  }

  onwaiting(){
    console.debug("Media is waiting (buffering?)...");
    window.player.setState({
      isplaying: false
    });
  }

  onstalled(){
    console.debug("Media has stalled...");
    window.player.setState({
      isplaying: false
    });
  }

  onerror(){
    console.debug("Media has an error...");
    window.player.setState({
      isplaying: false
    });
  }

  ondurationchange(){
    console.debug("Media length has changed...");

    /* Info:
     *   if(player.duration == 13.212) -> dienst is NIET live
     *   if(player.duration == Infinity) -> dienst is live
     */

    window.player.setState({
      islive: !(window.player.duration() < 20)
    });
  }

  onloadstart(){
    console.debug("Media is loading...");

    window.player.setState({
      isloading: true
    });
  }

  onloadeddata(){
    console.debug("Media is loaded...");

    window.player.setState({
      isloading: false
    });
  }

  /** (callable) Events **/
  play(){
    console.debug("Event play triggered...");
    this.refs.luisterenObject.play();
  }

  pause(){
    console.debug("Event pause triggered...");
    this.refs.luisterenObject.pause()
  }

  load(){
    console.debug("Event load triggered...");
    this.refs.luisterenObject.load();
  }

  canPlayType(type){
    return this.refs.luisterenObject.canPlayType(type);
  }

  toggle(){
    console.debug("Event toggle triggered...");
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
    $.each(window.playerButton, function(i, v){
      v.forceUpdate();
    });
  }

  render(){
    return (
      <audio id="luisteren-audio" ref="luisterenObject" loop preload="metadata">
        <source src="http://kerkdienstgemist.nl/streams/267.mp3" type="audio/mpeg" />
      </audio>
    );
  }
}