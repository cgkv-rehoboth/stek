import qxhr from 'q-xhr';
import q from 'q';
let Q = qxhr(window.XMLHttpRequest, q);
import Cookies from 'cookies-js';
import _ from 'underscore';

//
// utility functions
//

export function post(url, data, options={}) {
  options.headers = _.defaults(options.headers || {}, {
    'X-CSRFToken': Cookies.get('csrftoken')
  });

  return Q.xhr.post(url, data, options);
}

export function del(url, options={}) {
  options.headers = _.defaults(options.headers || {}, {
    'X-CSRFToken': Cookies.get('csrftoken')
  });

  return Q.xhr.delete(url, options);
}
