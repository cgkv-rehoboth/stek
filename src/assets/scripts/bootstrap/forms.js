import React, {Component, PropTypes} from 'react';
import _ from 'underscore';
import cn from 'classnames';
import ReCAPTCHA from 'react-google-recaptcha';

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

export class InputGroup extends Component {
  static get propTypes() {
    return {
      errors: PropTypes.array,
      label: PropTypes.string,
      name: PropTypes.string.isRequired,
      onChange: PropTypes.func.isRequired,
      type: PropTypes.string.isRequired
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
      <input
        value={value}
        onChange={onChange}
        type={type} name={name} className="form-control" aria-describedby={`${name}-addon`} />
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
    this.setValue(undefined);
  }

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

    return (
      <InputGroup
        errors={this.state.errors}
        name={name}
        label={label}
        value={this.state.value}
        onChange={this.onChange.bind(this)}
        type="text" />
    );
  }
}

export class PasswordField extends CharField {

  render() {
    let { label, name } = this.props;

    return (
      <InputGroup
        errors={this.state.errors}
        name={name}
        label={label}
        onChange={this.onChange.bind(this)}
        value={this.state.value}
        type="password" />
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
        ></textarea>
      </div>
    );
  }
}

export class CaptchaField extends Field {

  static get defaultProps() {
    return Object.assign({}, Field.defaultProps, {
      name: "recaptcha"
    });
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
      sitekey="6LdTEBsTAAAAAEGoRs_P10MVgylFKuxHnKZzB-m1"
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
