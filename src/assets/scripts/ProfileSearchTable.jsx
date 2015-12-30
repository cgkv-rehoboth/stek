let React = require("react");
let _ = require('underscore');
let api = require('api');
let forms = require('forms');
let { Table } = require('bootstrap/tables');

class ProfileSearchTable extends React.Component {

  static get propTypes() {
    return {};
  }

  constructor(props) {
    super(props);
    this.state = {
      profiles: []
    };
  }

  componentWillMount() {
    // load initial profiles
    api.profiles.list()
      .then((data) => {
        console.debug("Loading profiles complete");

        this.setState({
          profiles: data.data.results
        });
      });
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
      </tr>;
    });

    return <div>
      <Table>
        <tbody>
        {rows}
        </tbody>
      </Table>
    </div>;
  }
}

module.exports = ProfileSearchTable;
