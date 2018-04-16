/*! fast-levenshtein 2016-12-27. Copyright Ramesh Nair <ram@hiddentao.com> (http://www.hiddentao.com/) */
!function(){"use strict";var a;try{a="undefined"!=typeof Intl&&"undefined"!=typeof Intl.Collator?Intl.Collator("generic",{sensitivity:"base"}):null}catch(b){console.log("Collator could not be initialized and wouldn't be used")}var c=[],d=[],e={get:function(b,e,f){var g=f&&a&&f.useCollator,h=b.length,i=e.length;if(0===h)return i;if(0===i)return h;var j,k,l,m,n;for(l=0;i>l;++l)c[l]=l,d[l]=e.charCodeAt(l);c[i]=i;var o;if(g)for(l=0;h>l;++l){for(k=l+1,m=0;i>m;++m)j=k,o=0===a.compare(b.charAt(l),String.fromCharCode(d[m])),k=c[m]+(o?0:1),n=j+1,k>n&&(k=n),n=c[m+1]+1,k>n&&(k=n),c[m]=j;c[m]=k}else for(l=0;h>l;++l){for(k=l+1,m=0;i>m;++m)j=k,o=b.charCodeAt(l)===d[m],k=c[m]+(o?0:1),n=j+1,k>n&&(k=n),n=c[m+1]+1,k>n&&(k=n),c[m]=j;c[m]=k}return k}};"undefined"!=typeof define&&null!==define&&define.amd?define(function(){return e}):"undefined"!=typeof module&&null!==module&&"undefined"!=typeof exports&&module.exports===exports?module.exports=e:"undefined"!=typeof self&&"function"==typeof self.postMessage&&"function"==typeof self.importScripts?self.Levenshtein=e:"undefined"!=typeof window&&null!==window&&(window.Levenshtein=e)}();

// List of HTML entities for escaping.
var htmlEscapes = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#x27;',
  '/': '&#x2F;'
};

// Regex containing the keys listed immediately above.
var htmlEscaper = /[&<>"'\/]/g;

// Escape a string for HTML interpolation.
var escape = function(string) {
  return ('' + string).replace(htmlEscaper, function(match) {
    return htmlEscapes[match];
  });
};

var get_url_archief = function (d) {
  return '/linker/details/' + d['article_id'] + '/' + d['nmlid'] + '/' + d['entity'].replace(/\s+/, '/');
};

var get_url_namenlijst = function (d) {
  return 'https://database.namenlijst.be/#/person/_id=' + d['nmlid'];
}
var changes = {};


function modal(d) {
  document.getElementById('modal-trigger').click();
  var tr = d3.select('table tr.active');
  var src = 'about:blank';
  tr.select(function(){
    src = d3.select(this.nextElementSibling).select('a[target="archief"]').attr('href');
    return this;
  });

  d3.select('#new-status')
    .text(d['statusTitle'].charAt(0).toLowerCase() + d['statusTitle'].substr(1))
    .classed('red green yellow', false)
    .classed(d['statusColor'], true);

  var $this = d3.select('#modal');

  for (var k in d) {
    var el = d3.select('#update-item').select('input[name="' + k + '"]');
    if (el.size()) {
      el.property('value', d[k]);
    }
  }
}

var emptySrc = 'data:text/html;charset=utf-8,';
d3.text('loading').then(function (d) {
  emptySrc += encodeURI(d);
});

var tabulate = function (data) {
  var table = d3.select('#csvtable');
  var columns = ['status', /*'score', 'days_diff', */ 'firstname', 'lastname', 'entity', 'title']
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
          case 'firstname':
          case 'lastname':
            return '<a href="' + escape(get_url_namenlijst(d.row)) + '" target="namenlijst">' +
                    escape(d.value) +
                    '</a>';
          case 'title':

            return '<a title="' + escape(d.row.article_id) +
                    '" href="' + escape(get_url_archief(d.row)) + '" target="archief">' +
                    escape(d.value) +
                    '</a>, pid ' + escape(d.row.article_id) + ', pagina ' + d.row.page;
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

window.jsonrpc = function (method, data) {
  var obj = {};
  if (data instanceof FormData) {
    data.forEach(function(v, k) {
      obj[k] = v;
    });
  } else {
    obj = data;
  }

  var body = {
    method: method,
    params: obj,
    id: Date.now(),
    jsonrpc: "2.0"
  };
  var headers = new Headers();
  headers['Content-Type'] = 'application/json';

  var options = {};
  options.body = JSON.stringify(body);
  options.headers = headers;
  options.method = 'POST';
  return d3.json('/api/jsonrpc', options);
}


jsonrpc('get_items', {amount: 100}).then(function (data) {
  data = data.result

  jsonrpc('get_kinds').then(function (d) {
    new Awesomplete(document.getElementById("autosuggestkind"), {
      list: d.result,
      minChars: 0
    });
  })

  data.map(function (a) {
      a['score'] = Math.min(
        Levenshtein.get(a.firstname + ' ' + a.lastname, a.entity),
        Levenshtein.get(a.lastname + ' ' + a.firstname, a.entity)
      );
      a['page'] = parseInt(a.article_id.substring(a.article_id.length-4).replace(/^0/s, ''))
      return a;
  })

  tabulate(data.sort(function(a,b) {
    if (a.score == b.score) {
      return Math.random(-1, 1);
      // return a.lastname > b.lastname ? 1 : a.lastname < b.lastname ? -1 : a.firstname > b.firstname ? 1 : -1;
    }
    return a.score - b.score;
  }));

  d3.select('table tbody tr').select(function (){this.click();});
  var $form = d3.select('#update-item');
  $form.on('submit', function () {
    d3.event.preventDefault();
    $form.select('input[type="submit"]').property('disabled', true);
    var tr = d3.select('table tr.active');
    tr.select(function(){this.nextElementSibling.click();return this;});

    var data = new FormData(document.getElementById('update-item'));
    jsonrpc('update_item', data)
      .then(function (d) {
        document.getElementById('modal-trigger').click();
        if (typeof(d) === 'object' && typeof(d.success) !== 'undefined' && d.success) {
          tr.style('display', 'none');
        }
        $form.select('input[type="submit"]').property('disabled', false);
      });
  });

  d3.select('button[type="reset"]').on('click', function () {
    document.getElementById('modal-trigger').click();
  });
});
