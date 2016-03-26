import React, {Component, PropTypes} from 'react';
import $ from 'jquery';
import _ from 'underscore';

export function Modal(props) {
  let {open, actions, title} = props;

  let buttons = _.map(actions, (action, name) =>
                      <button type="button" onClick={action} class="btn btn-default">{name}</button>);

  let style = {
    display: open ? 'block' : 'none'
  };

  return (
    <div className="modal fade in" tabIndex="-1" role="dialog" style={style}>
      <div className="modal-dialog">
        <div className="modal-content">
          <div className="modal-header">
            <button type="button" className="close"
              data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
            <h4 className="modal-title">{title}</h4>
          </div>
          {props.children}
        </div>
      </div>
    </div>
  );
}

export function ModalBody(props) {
  return <div className="modal-body">
    {props.children}
  </div>;
}

export function ModalFooter(props) {
  return <div className="modal-footer">
    {props.children}
  </div>;
}
