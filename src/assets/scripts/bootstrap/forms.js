import React, {Component, PropTypes} from 'react';
import _ from 'underscore';
import cn from 'classnames';
import ReCAPTCHA from 'react-google-recaptcha';
import moment from 'moment';

import {Modal, ModalBody, ModalFooter} from 'bootstrap/Modal';
import Icon from 'bootstrap/Icon';
import DateTimePicker from 'bootstrap/datetimepicker';

export class Label extends Component {

  static get propTypes() {
    return {
      errors: PropTypes.array
    };
  }

  static get defaultProps() {
    return {
      errors: []
    };
  }

  render() {
    return <span {...this.props}>{ this.props.children }</span>;
  }
}

export class LabeledInput extends Component {
  static get propTypes() {
    return {
      errors: PropTypes.array,
      label: PropTypes.string,
      name: PropTypes.string
    };
  }

  static get defaultProps() {
    return {errors: []};
  }

  static get contextTypes() {
    return { form: React.PropTypes.object.isRequired };
  }

  render() {
    let {label, type, name, value, errors, onChange} = this.props;
    let clz = cn("input-group", { faulty: errors.length > 0 });

    return <div className={clz}>
      <Label
         errors={errors}
         className="input-group-addon" id={`${name}-addon`}>{ label || name }</Label>
      {this.props.children}
    </div>;
  }
}

export class Form extends React.Component {

  static get propTypes() {
    return {
      // custom submit handler
      onSubmit: React.PropTypes.func,

      // api action function, alternative to onSubmit
      action: React.PropTypes.func,
      // called if action completes succesfully
      onSuccess: React.PropTypes.func
    };
  }

  static get defaultProps() {
    return {
      onSuccess: () => {},
      onSubmit: () => {}
    };
  }

  static get childContextTypes() {
    return {
      form: React.PropTypes.object.isRequired
    };
  }

  constructor(props) {
    super(props);

    this.fields = {};
  }

  // register a field with the form
  // (this is required for the form to be able to control the children directly)
  register(name, field) {
    if(this.fields[name] !== undefined)
      console.warn(`A field with name ${name} is already registered on this form`);

    this.fields[name] = field;
  }

  getChildContext() {
    return {
      form: this
    };
  }

  clear() {
    _.each(this.fields, (field) => field.clear());
  }

  clearErrors() {
    _.each(this.fields, (field) => field.setErrors([]));
  }

  collectInput() {
    return _.chain(this.fields)
      .map((field, name) => {
        return [name, field.getValue()];
      })
      .object()
      .value();
  }

  submit() {
    this.clearErrors();

    if(this.props.action) {
      this.props
        .action(this.collectInput())
        .then((resp) => {
          this.clear();
          this.props.onSuccess(resp);
        })
        .catch((resp) => {
          _.each(resp.data, (errs, name) => {
            this.fields[name].setErrors(errs);
          });
        });
    } else if(this.props.onSubmit) {
      this.props.onSubmit(this.state.data);
    }

    // after submission, we notify the fields
    _.map(this.fields, (field) => field.onSubmit());
  }

  render() {
    return <form>{this.props.children}</form>;
  }
}

/**
 * Abstract over some boilerplate that is common in all fields of a form.
 */
export class Field extends React.Component {

  static get contextTypes() {
    return { form: React.PropTypes.object.isRequired };
  }

  constructor(props) {
    super(props);
    this.state = {
      value: props.initial,
      errors: []
    };
  }

  static get propTypes() {
    return {
      name: React.PropTypes.string.isRequired,
      label: React.PropTypes.string,
      initial: React.PropTypes.any
    };
  }

  static get defaultProps() {
    return {
      label: "",
      initial: undefined
    };
  }

  clear() {
    this.setValue(this.props.initial);
  }

  onSubmit() {}

  setErrors(errors=[]) {
    this.setState({errors: errors});
  }

  setValue(value) {
    this.setState({value: value});
  }

  getValue() {
    return this.state.value;
  }

  componentWillMount() {
    this.context.form.register(this.props.name, this);
  }
}

export class CharField extends Field {

  static get defaultProps() {
    return _.extend(Field.defaultProps, {
      initial: ""
    });
  }

  onChange(e) {
    this.setValue(e.target.value);
  }

  render() {
    let { label, name } = this.props;
    let { value } = this.state;

    return (
      <LabeledInput name={name} errors={this.state.errors} label={label} >
        <input
          value={value}
          onChange={this.onChange.bind(this)}
          type="text" name={name} className="form-control" aria-describedby={`${name}-addon`} />
      </LabeledInput >
    );
  }
}

export class SelectField extends Field {

  onChange(event) {
    this.setValue(event.target.value);
  }

  render() {
    let {name, label} = this.props;
    let {value} = this.state;

    return <LabeledInput name={name} label={label}>
      <select className="form-control"
        value={value}
        name={name}
        onChange={this.onChange.bind(this)}>
        {this.props.children}
      </select>
    </LabeledInput>;
  }
}

/* Saves the value as an moment object, returns it as a ISO-8601 string
 */
export class DateTimeField extends Field {

  static get defaultProps() {
    return _.extend({}, Field.defaultProps, {
      initial: moment().format()
    });
  }

  constructor(props) {
    super(props);

    this.state = _.extend({}, this.state, {
      pickerOpen: false
    });
  }

  getValue() {
    return this.state.value.format();
  }

  onChange(date) {
    this.setValue(date);
  }

  openPicker() {
    this.setState({ pickerOpen: true });
  }

  closePicker() {
    this.setState({ pickerOpen: false });
  }

  render() {
    let { value, pickerOpen } = this.state;
    let { label, name } = this.props;

    return (
      <LabeledInput name={name} errors={this.state.errors} label={label} >
        <Modal open={pickerOpen} title="Kies een datum en tijd">
          <ModalBody>
            <DateTimePicker initial={value} onChange={this.onChange.bind(this)}/>
          </ModalBody>
          <ModalFooter>
            <button type="button" onClick={this.closePicker.bind(this)}><Icon name="check" /></button>
          </ModalFooter>
        </Modal>
        <input
          value={value.format("lll")}
          onChange={this.onChange.bind(this)}
          onClick={this.openPicker.bind(this)}
          type="text" name={name} className="form-control" aria-describedby={`${name}-addon`} />
      </LabeledInput >
    );
  }
}

export class PasswordField extends CharField {

  render() {
    let { label, name } = this.props;
    let { value } = this.state;

    return (
      <LabeledInput name={name} errors={this.state.errors} label={label} >
        <input
          value={value}
          onChange={this.onChange.bind(this)}
          type="password" name={name} className="form-control" aria-describedby={`${name}-addon`} />
      </LabeledInput >
    );
  }
}

export class TextField extends CharField {

  clear() {
    this.setValue("");
  }

  render() {
    let {name, label} = this.props;

    return (
      <div>
        <Label errors={this.state.errors}>
          {label || name}
        </Label>
        <textarea
          name={name}
          onChange={this.onChange.bind(this)}
          value={this.state.value}
          className={cn({faulty: this.state.errors.length > 0})}
        ></textarea>
      </div>
    );
  }
}

export class CaptchaField extends Field {

  static get propTypes() {
    return Object.assign({}, Field.propTypes, {
      sitekey: PropTypes.string.isRequired
    });
  }

  static get defaultProps() {
    return _.extend({}, Field.defaultProps, {
      name: "recaptcha"
    });
  }

  onSubmit() {
    // make sure we don't send the same thing twice
    this.clear();
  }

  clear() {
    this.refs.recaptcha.reset();
  }

  setErrors(errs) {
    if(errs.length > 0)
      alert("Om ons tegen spam te beschermen moet u het vinkje in de witte box aanvinken.");
  }
  
  onChange(e) {
    this.setValue(e);
  }

  render() {
    return <ReCAPTCHA
      ref="recaptcha"
      sitekey={this.props.sitekey}
      onChange={this.onChange.bind(this)} />;
  }
}

export class SubmitButton extends React.Component {

  static get propTypes() {
    return {
      label: PropTypes.string
    };
  }

  static get defaultProps() {
    return {
      label: "OK"
    };
  }

  static get contextTypes() {
    return { form: React.PropTypes.object.isRequired };
  }

  submitForm(e) {
    this.context.form.submit();
    e.preventDefault();
    return false;
  }

  render() {
    let {label} = this.props;

    return <input className="btn btn-rounded dark" type="submit" onClick={this.submitForm.bind(this)} value={label}/>;
  }
}
