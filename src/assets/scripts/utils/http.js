let Q = require('q-xhr')(window.XMLHttpRequest, require('q'));
let Cookies = require('cookies-js');
let _ = require('underscore');

//
// utility functions
//

function post(url, data, options={}) {
  options.headers = _.defaults(options.headers || {}, {
    'X-CSRFToken': Cookies.get('csrftoken')
  });

  return Q.xhr.post(url, data, options);
}

function del(url, options={}) {
  options.headers = _.defaults(options.headers || {}, {
    'X-CSRFToken': Cookies.get('csrftoken')
  });

  return Q.xhr.delete(url, options);
}
