var get_url_archief = function (d) {
  return '/attestation/info/' + d['pid'] + '/' + d['nmlid'] + '/' + d['entity'].replace(/\s+/, '/');
};

var get_url_namenlijst = function (d) {
  return 'https://database.namenlijst.be/#/person/_id=' + d['nmlid'];
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

var namenlijst = d3.select('iframe#namenlijst');
var nextData = null;

window.nextItem = function () {
    var amount = 1;
    if (nextData === null) {
      amount = 2;
    }
    jsonrpc('get_items', { amount: amount }).then(function (data) {
      namenlijst.attr('src', emptySrc);
      data = data.result

      var notI = i == 0 ? 1 : 0;

      preloads[i].attr('src', get_url_archief(data[0]));
      if (typeof(data[1]) !== 'undefined') {
        preloads[notI].attr('src', get_url_archief(data[1]));
        namenlijst.attr('src', get_url_namenlijst(data[1]));
      } else {
        namenlijst.attr('src', get_url_namenlijst(nextData));
      }
      preloads[i].classed('inactive', true);
      preloads[notI].classed('inactive', false);
      i = notI;
      nextData = data[0];
    });
};

window.nextItem();
