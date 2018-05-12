var get_url_archief = function (d) {
  return '/attestation/info/' + d['pid'] + '/' + d['nmlid'] + '/' + d['entity'].replace(/\s+/, '/');
};

var get_url_namenlijst = function (d) {
  return 'https://database.namenlijst.be/#/person/_id=' + d['nmlid'];
}
var changes = {};

var emptySrc = 'data:text/html;charset=utf-8,';
d3.text('loading').then(function (d) {
  emptySrc += encodeURI(d);
});

var tabulate = function (data) {
  var table = d3.select('#csvtable');
  var columns = ['status', 'entity', 'pid'];
  var thead = table.select('thead');
  var tbody = table.select('tbody');
  var iframes = ['archief', 'namenlijst'];
  data = data.filter(function (d) {
    return d['status'] == '';
  });

	thead.select('tr')
	  .selectAll('th')
	    .data(columns)
	    .enter()
	  .append('th')
	    .text(function (d) { return d });

  var onload = function () {
    d3.select(this).classed('loading', false);
  };

  for (var k of iframes) {
    d3.select('iframe#' + k).on('load', onload).on('hashchange', onload);
  }

  var rows = tbody.selectAll('tr')
      .data(data)
      .enter()
      .append('tr')
    .on('click', function (d) {
      var $this = d3.select(this);
      if (!$this.classed('active')) {
        d3.select(this.parentNode).selectAll('tr.active').classed('active', false);
        $this.classed('active', true);
        d['url_archief'] = get_url_archief(d);
        d['url_namenlijst'] = get_url_namenlijst(d);

        for (var k of iframes) {
          var el = d3.select('iframe#' + k);
          el.classed('loading', true);
          el.attr('src', emptySrc);
          setTimeout((function (src, elem) {
            return function () {
              elem.attr('src', src);
            };
          })(d['url_' + k], el), 200);
        }
      } else {
        if (d3.event.srcElement.nodeName === 'BUTTON') {
          d.status = d3.event.srcElement.value;
          d.statusTitle = d3.event.srcElement.title;
          d.statusColor = d3.event.srcElement.classList[d3.event.srcElement.classList.length - 1];
          modal(d);
        }
      }
    })
    .attr('class', function (row) {
      switch (row['status']) {
        case '?':
          return 'yellow';
        case 'ok':
          return 'green';
        case 'nok':
          return 'red';
        default:
          return 'default';
      }
    });

	var cells = rows.selectAll('td')
	    .data(function(row) {
	    	return columns.map(function (column) {
	    		return {
            column: column,
            value: row[column],
            row: row
          };
	      });
      })
      .enter()
    .append('td')
      .html(function (d) {
        switch (d.column) {
          case 'pid':

            return '<a title="' + escape(d.row.pid) +
                    '" href="' + escape(get_url_archief(d.row)) + '" target="archief">' +
                    escape(d.value) +
                    '</a>, pid ' + escape(d.row.pid) + ', pagina ' + d.row.page;
          case 'status':
            if (d.value == '') {
              return '<div class="pure-button-group" role="group" aria-label="Status">' +
                    '<button title="Geconfirmeerde match" value="ok" class="pure-button green">✔</button>' +
                    '<button title="Onzeker, mogelijke match" value="?" class="pure-button yellow">?</button>' +
                    '<button title="Geen match" value="nok" class="pure-button red">×</button>' +
                    '</div>';
            }
            return escape(d.value);

          default:
            return escape(d.value);
        }
        return '';
      });

  return table;
}



jsonrpc('get_items', {amount: 100}).then(function (data) {
  data = data.result

  data.map(function (a) {
      a['page'] = parseInt(a.pid.substring(a.pid.length-4).replace(/^0/s, ''));
      return a;
  })

  tabulate(data);

  d3.select('table tbody tr').select(function (){this.click();});

});
