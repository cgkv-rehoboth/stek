let apiurl = "http://localhost:8000/api/v1/";
let Q = require('q-xhr')(window.XMLHttpRequest, require('q'));
let Cookies = require('cookies-js');
let _ = require('underscore');
let http = require('utils/http');

let api = '/api/v1';
let static_url = '/static';

Q.xhr.interceptors = [
  // interceptor to load the url parameters into the url
  // while keeping track of them in the 'params' field of the config.
  // this is useful to be able to recover the url parameters easily from the response
  // in the listeners
  {
    request: (config) => {
      config.urlparams = {};

      _.each(config.params, (param, name) => {
        if(config.url.indexOf(`:${name}`) !== -1) {
          config.url = config.url.replace(`:${name}`, param.toString());

          // prevent it from showing up in the get params
          delete config.params[name];
          // back the value up
          config.urlparams[name] = param;
        }
      });

      return config;
    },

    response: (resp) => {
      // put the urlparams back in the params
      _.extend(resp.config.params, resp.config.urlparams);
      return resp;
    }
  }
];

let api_obj = {
  duties: {
    create: (duty) => post(`${api}/agenda/duties/`, data),

    list: (page=1, pagesize=50) => {
      return Q.xhr
        .get(`${api}/agenda/duties/`, {
          params: {page: page, pagesize: pagesize}
        });
    },

    get: (pk) => {
      return Q.xhr
        .get(`${api}/agenda/duties/:pk/`, {
          params: {pk: pk}
        });
    }
  }
};

module.exports = api_obj;
