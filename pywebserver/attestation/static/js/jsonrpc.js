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
