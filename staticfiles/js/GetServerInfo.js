/**
 * Created with PyCharm.
 * User: tyler
 * Date: 9/19/13
 * Time: 12:58 AM
 * To change this template use File | Settings | File Templates.
 */

var ListServersInterval = null;

function ListServers() {
    $.get('/api/ServerList', function(data) {
        var DataDiv = $('#ServerContainer');
        $(DataDiv).empty();

        var table = $('<table></table>').addClass('striped rounded');

        var head = $('<thead></thead>');
        var row = $('<tr></tr>');
        $(row).append($('<td></td>').text('Server'));
        $(row).append($('<td></td>').text('Users'));

        var LastTD = $('<td></td>').text('Last Updated');
        var RefreshButton = $('<i></i>').addClass('icon-arrows-ccw ttip');
        var UpdateTime = new Date();
        var RefreshText = $('<span></span>').html("Updates are received from computers every 15 minutes.<br/> This table will refresh automatically every 15 minutes. <br/> This table was last refreshed at " + UpdateTime.toLocaleTimeString())
        var refreshLink = $('<a href="#"></a>').append(RefreshButton).append(RefreshText).addClass('Refresh hasTooltip');
        $(refreshLink).click(function() {
            ListServers();
        })
        $(LastTD).append(refreshLink);
        $(row).append(LastTD)

        $(head).append(row);
        var body = $('<tbody></tbody>');
        for (item in data) {
            server = data[item];
            row = $('<tr></tr>');
            $(row).append($('<td></td>').text(server.ComputerName));
            $(row).append($('<td></td>').text(server.NumUsers));
            $(row).append($('<td></td>').text(server.LastUpdated));
            $(body).append(row);
        }

        $(table).append(head);
        $(table).append(body);

        $(DataDiv).append(table);

    })
    window.clearInterval(ListServersInterval);
    ListServersInterval = window.setInterval(ListServers, 900000)
}

$(document).ready(ListServers)