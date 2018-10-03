import React, {Component, PropTypes} from 'react';
import ReactDom from "react-dom";
import * as forms from 'bootstrap/forms';
import {LiveButton, LivePlayer} from "LiveButton";
import ServiceTable from "ServiceTable";
import {SearchTable} from "bootstrap/tables";
import Popup from "Popup";

class ContactForm extends Component {

  render() {
    let formBuilder = <div>
      <div className="row" >
        <div className="col-sm-6">
          <forms.CharField name="first_name" label="Voornaam" />
        </div>
        <div className="col-sm-6">
          <forms.CharField name="last_name" label="Achternaam" />
        </div>
      </div>
      <div className="row" >
        <div className="col-sm-12">
          <forms.CharField name="email" label="E-mail" />
        </div>
      </div>
      <div className="vspace" >
      </div>
      <div className="row" >
        <div className="col-sm-12">
          <forms.TextField name="message" label="Bericht" />
        </div>
      </div>

      <div className="row" >
        <div className="col-sm-3 col-md-2" style={{marginTop: 10 + "px"}}>
          Versturen naar
        </div>

        <div className="col-sm-7 col-md-10">
          <forms.RadioField name="recipient">
            <forms.RadioButton name="recipient[]" value="scriba" label="Scriba / Overig" checked="checked"/>
            <br/>
            <forms.RadioButton name="recipient[]" value="predikant" label="Predikant (dr. A. Jansen)" />
          </forms.RadioField>
        </div>
      </div>

      <div className="vspace" ></div>
      <div className="row" >
        <div className="col-sm-6">
          <forms.CaptchaField sitekey={window.rehoboth.RECAPTCHA_PUBLIC_KEY} />
        </div>
        <div className="col-sm-6 text-right">
          <forms.SubmitButton label="Verstuur!" />
        </div>
      </div>
    </div>;

    return <forms.Form
      action={api.contact}
      onSuccess={(resp) => {
        alert("Uw email is verstuurd! " +
              "U zult spoedig antwoord ontvangen op " + resp.data.email);
      }}>{formBuilder}</forms.Form>;
  }
}

export default function frontpageMain() {
  /**
   * Popup
   */
  ReactDom.render(
    <Popup>
      Zondag a.s. (7 okt) is de ochtenddienst om <strong>10:00u</strong> in de <strong><a href="http://www.kerkpleinwoerden.nl/jml33/index.php/kerkgebouwen/kruiskerk" title="Website van de Kruiskerk" target="_blank">Kruiskerk</a></strong>.
    </Popup>,
    $('#popup')[0]
  );

  
  /**
   * Contact form
   */
  // Render the contact form
  ReactDom.render(<ContactForm />, $('#contact-form')[0]);
  
  
  /**
   * Service table
   */
  // Create function for retrieving data
  let searchServices = (query, page) => {
    return api.services.list(query, page);
  };

  // Render the service table
  ReactDom.render(
    <ServiceTable listFunc={searchServices} />,
    $("#service-table")[0]
  );
  
  
  /**
   * Broadcast / Meeluisteren
   */
  // Check if the broadcast is live
  var loaded = false; // Only check this once
  let onDataLoaded = () => {
    if(!loaded) {
      // Loading
      loaded = true;

      // Get element with the icon
      var intro = $(".intro .intro-body .container .row:first-of-type div:first-of-type")[0];

      // Fade the picture out for a smooth transition
      $(intro).find('img').fadeOut(500, function(){
        // Change col class
        $(intro).addClass('col-md-4').removeClass('col-md-8');
        // Fade the picture in again
        $(this).fadeIn(500);

        // Add Play button
        $("#listen-in").fadeIn(1000);
      });
    }
  };

  // Add only one player to the page
  $("#content").append('<div id="luisteren-player"></div>');
  
  // Render the buttons to control this player
  let player = ReactDom.render(
    <LivePlayer onDataLoaded={onDataLoaded}></LivePlayer>,
    $("#luisteren-player")[0]
  );

  // Assign React component to each element with class 'luisteren-button'
  $(".luisteren-button").map((value, i) => {
    ReactDom.render(<LiveButton text={$(i).text()} player={player}></LiveButton>, i);
  });
  
  
  /**
   * Jaarthema: show the info of the selected year
   */
  $("#jaarthema-menu a").click(function(){
    let newcontainer = "#jaarthema-" + $(this).data('jaar');
    
    // Check if current jaarthema is already visible
    if ($(newcontainer).css('display') == 'none') {
      // Stop all events on these divs
      $(".jaarthema-archive").stop();
      
      // Hide all jaarthema divs
      $(".jaarthema-archive").slideUp();
      
      // Show new jaarthema div
      $(newcontainer).slideDown();
      
      // Change background, only when a new image is available
      if ($(newcontainer).data('background-img')) {
        $("#jaarthema").css('background-image', 'url(' + $(newcontainer).data('background-img') + ')');
      }
      
      // Select the right menu item
      $("#jaarthema-menu a").removeClass('current');
      $(this).addClass('current')
    }
  })
  
};