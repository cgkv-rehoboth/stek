import React from "react";

export default class ReactImage extends React.Component {

  static get propTypes() {
    return {
      src: React.PropTypes.string.isRequired,
      alt: React.PropTypes.string,
      className: React.PropTypes.string
    };
  }

  constructor(props) {
    super(props);
    
    this.state = {
      status: 'pending'
    };
    
    this.handleLoad=this.handleLoad.bind(this);
  }
  
  componentDidMount(){
    // Load image in memory
    if (this.state.status !== 'loading'){
      this.img = new Image();
      this.img.onload = this.handleLoad;
      this.img.src = this.props.src;
      
      this.setState({status: 'loading'});
    }
  }
  
  handleLoad(e){
    // Update HTML when image is loaded
    this.setState({status: 'loaded'});
  }

  render() {
    // Start with default loading spinner + text
    let el = <span><i className="fa fa-refresh fa-spin"></i><br/><br/><small>Afbeelding laden...</small></span>;
    
    // If picture is loaded, show it
    if (this.state.status === 'loaded'){
      el = <img src={this.props.src} className={this.props.className} alt={this.props.alt} />;
    }
    
    return (
      <div>
        {el}
      </div>
    );
  }
}
