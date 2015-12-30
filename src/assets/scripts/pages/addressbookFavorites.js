let React = require("react");
let ReactDom = require("react-dom");
let ProfileSearchTable = require("ProfileSearchTable");
let api = require("api");

let f = (searchtext, page) => {
  return api.profiles.list(searchtext, page);
};

ReactDom.render(<ProfileSearchTable listFunc={f} />, $("#profile-search-table")[0]);
