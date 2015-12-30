let React = require("react");
let _ = require('underscore');
let api = require('api');
let forms = require('forms');
let $ = require("jquery");
let FavStar = require('bootstrap/favorites');
let { PaginatedTable } = require('bootstrap/tables');

class ProfileSearchTable extends React.Component {

  static get propTypes() {
    return {
      listFunc: React.PropTypes.func.isRequired // (searchText, page) => promise<[profile]>
    };
  }

  constructor(props) {
    super(props);
    this.state = {
      profiles: [],
      pageno: 0,
      hasPrev: false,
      hasNext: false
    };
  }

  loadProfiles(searchtext="", page=1) {
    // load initial profiles
    return this.props.listFunc(searchtext, page)
      .then((data) => {
        console.debug("Loading profiles complete");

        this.setState({
          profiles: data.data.results,
          pageno: data.data.pageno,
          hasPrev: data.data.previous !== null,
          hasNext: data.data.next !== null
        });
      });
  }

  componentWillMount() {
    this.loadProfiles();
  }

  searchChange(e) {
    let text = $(e.target).val();
    this.loadProfiles(text);
  }

  pageChange(page) {
    this.loadProfiles("", page);
  }

  render() {
    let rows = _.map(this.state.profiles, (prof) => {
      let family = prof.family
        ? <a href={"/adresboek/families/" + prof.family.id + "/"}>{prof.user.last_name}</a>
        : family = <span></span>;

      return <tr key={prof.id}>
        <td><a href={"/adresboek/profiel/" + prof.id + "/"}>{prof.user.first_name}</a></td>
        <td>{family}</td>
        <td>{prof.address.street} <small>({prof.address.zip})</small></td>
        <td>{prof.address.city}</td>
        <td>{prof.phone}</td>
        <td>{prof.user.email}</td>
        <td><FavStar pk={prof.id} favorite={prof.is_favorite}></FavStar></td>
      </tr>;
    });

    return <div>
      <input type="text" onChange={_.debounce(this.searchChange.bind(this), 1000)} />
      <PaginatedTable pageno={this.state.pageno} onPageChange={this.pageChange.bind(this)} hasPrev={this.state.hasPrev} hasNext={this.state.hasNext}>
        <tbody>
        {rows}
        </tbody>
      </PaginatedTable>
    </div>;
  }
}

module.exports = ProfileSearchTable;
