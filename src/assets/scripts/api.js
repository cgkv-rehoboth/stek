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
    create: (duty) => http.post(`${api}/agenda/duties/`, duty),

    list: (page=1, pagesize=50) => {
      return Q.xhr
        .get(`${api}/agenda/duties/`, {
          params: {page: page, page_size: pagesize}
        });
    },

    get: (pk) => {
      return Q.xhr
        .get(`${api}/agenda/duties/:pk/`, {
          params: {pk: pk}
        });
    }
  },

  profiles: {
    list: (search='', page=1, extra_params={}) => {
      return Q.xhr
        .get(`${api}/profiles`, {
          params: _.extend({search: search, page: page}, extra_params)
        });
    },

    favorite: (pk) => {
      return http.post(`${api}/profiles/${pk}/favorite`);
    },

    defavorite: (pk) => {
      return http.post(`${api}/profiles/${pk}/defavorite`);
    }
  },

  teams: {
    list: (search='', page=1, extra_params={}) => {
      return Q.xhr
        .get(`${api}/agenda/teams/`, {
          params: _.extend({search: search, page: page}, extra_params)
        });
    }
  },

  favorites: {
    list: (search='', page=1, pagesize=30) => {
      return api_obj.profiles.list(search, page, pagesize, true);
    }
  },

  contact: (data) => {
    return http.post(`${api}/contact/`, data);
  },

  timetables: {
    list: (in_calendar, extra) => {
      return Q.xhr.get(`${api}/agenda/timetables/`, _.extend({
        params: {incalendar: in_calendar}
      }, extra));
    }
  },

  events: {
    // from and to should be unix timestamps
    list: (from, to, extra_params) => {
      return Q.xhr
        .get(`${api}/agenda/events/`, _.extend({
          params: {from: from, to: to}
        }, extra_params));
    },

    get: (id) => {
      return Q.xhr
        .get(`${api}/agenda/events/:id/`, {
          params: {
            id: id
          }
        });
    },

    add: (data) => {
      return http.post(`${api}/agenda/events/`, data);
    }
  },

  services: {
    list: (search='', page=1, page_size=8, extra_params={}) => {
      return Q.xhr
        .get(`${api}/agenda/services`, {
          params: _.extend({search: search, page: page, page_size: page_size}, extra_params)
        });
    },

    get: (id) => {
      return Q.xhr
        .get(`${api}/agenda/services/:id/`, {
          params: {
            id: id
          }
        });
    },

    add: (data) => {
      return http.post(`${api}/agenda/services/`, data);
    }
  }
};

window.api = api_obj;

module.exports = api_obj;
