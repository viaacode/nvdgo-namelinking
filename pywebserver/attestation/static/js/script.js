var get_url_archief = function (d) {
  return '/attestation/info/model-' + window.model + '/' + d['pid'] + '/' + d['nmlid'] + '/' + d['entity'].replace(/\s+/, '/');
};

var get_url_link = function (d) {
  return d['url'];
}

var emptySrc = 'data:text/html;charset=utf-8,';
d3.text('loading').then(function (d) {
  emptySrc += encodeURI(d);
});

var i = 0;

var preloads = [
        d3.select('iframe#attestation1'),
        d3.select('iframe#attestation2')
    ];

var link = d3.select('iframe#link_url');
var nextData = null;
var buffer = [];

window.nextItem = function () {
    var amount = 1;
    if (nextData === null) {
      amount = 5;
    }
    jsonrpc('get_items', { amount: amount, model: window.model }).then(function (data) {
      link.attr('src', emptySrc);
      data = data.result

      Array.prototype.push.apply(buffer, data);

      var curData = nextData ? nextData : buffer.shift();
      nextData = buffer.shift();

      var notI = i == 0 ? 1 : 0;

      // preloads[notI].attr('src', emptySrc);
      preloads[notI].attr('src', get_url_archief(curData));
      preloads[i].attr('src', emptySrc);
      link.attr('src', curData['url']);

      preloads[i].classed('inactive', true);
      preloads[notI].classed('inactive', false);

      // hack to ensure "loading" is loaded before attempting long page load
      setTimeout((function (a, b) {
        return function () {
            a.attr('src', b);
        };
      })(preloads[i], get_url_archief(nextData)), 1000);
      i = notI;
    });
};

window.nextItem();
