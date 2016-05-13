import React, {Component, PropTypes} from 'react';
import ReactDom from "react-dom";
import * as forms from 'bootstrap/forms';
import {LiveButton, LivePlayer} from "LiveButton";
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
        alert("Uw email is succesvol verstuurd naar de gemeente! " +
              "U zult spoedig antwoord ontvangen op " + resp.data.email);
      }}>{formBuilder}</forms.Form>;
  }
}

export default function frontpageMain() {
  ReactDom.render(<Popup>Zondagochtend 22 mei begint de dienst om <strong>10:00u</strong>. De dienst wordt gehouden in de <a href="http://www.kerkpleinwoerden.nl/jml33/index.php/kerkgebouwen/kruiskerk" target="_blank" title="Klik hier voor het adres van de Kruiskerk"><strong>Kruiskerk</strong></a> i.v.m. de belijdenis van een aantal jongeren.</Popup>, $('#popup')[0]);

  ReactDom.render(<ContactForm />, $('#contact-form')[0]);

  // Only do this once.
  var loaded = false;
  let onDataLoaded = () => {
    if(!loaded) {
      console.log("Loading");
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

  $("#content").append('<div id="luisteren-player"></div>');
  let player = ReactDom.render(
    <LivePlayer onDataLoaded={onDataLoaded}></LivePlayer>,
    $("#luisteren-player")[0]
  );

  // Assign React component to each element with class 'luisteren-button'
  $(".luisteren-button").map((value, i) => {
    ReactDom.render(<LiveButton text={$(i).text()} player={player}></LiveButton>, i);
  });

};
