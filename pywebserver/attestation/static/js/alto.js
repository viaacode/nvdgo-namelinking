if (typeof exports === 'undefined') {
   var exports = this;
}

// some helper functions
var warn = function warn() {
   if (typeof console !== 'object') {
      return;
   }
   if (typeof console.warn === 'function') {
      return console.warn.apply(this, arguments);
   }
   if (typeof console.log === 'function') {
      return console.log.apply(this, arguments);
   }
}

var div_factory = function (cls) {
   var el = document.createElement('div');
   el.className = cls;
   return el;
}

var wrap = function wrap(selection, elem, no_clone) {
   if (typeof elem === 'string') {
      // auto create div.elem if string (i.e. elem is classname)
      elem = div_factory(elem);
   }
   if (selection instanceof Element) {
      selection = d3.select(selection)
   }

   return selection.each(function (d, i) {
         if (!no_clone) {
            elem = elem.cloneNode();
         }
         this.parentNode
            .insertBefore(elem, this)
            .append(this);
      }).selectAll(function () {
         return [this.parentNode];
      });
}

var Extent = function Extent(x, y, w, h) {
    this.x = x;
    this.y = y;
    this.w = w;
    this.h = h;
}

Extent.to_coords = function(x, y, w, h) {
    return [x, y, x + w, y + h];
};

Extent.prototype.as_coords = function() {
    return Extent.to_coords(this.x, this.y, this.w, this.h);
};

Extent.prototype.extend = function (x, y, w, h) {
    var coords = this.as_coords();
    var extension = Extent.to_coords(x, y, w, h);
    coords = [
        Math.min(coords[0], extension[0]),
        Math.min(coords[1], extension[1]),
        Math.max(coords[2], extension[2]),
        Math.max(coords[3], extension[3]),
    ];
    this.x = coords[0];
    this.y = coords[1];
    this.w = coords[2] - coords[0];
    this.h = coords[3] - coords[1];
    return this;
};

var altoFuncs = function(elements, page_dimensions) {
    this.els = elements;
    this.page_dimensions = page_dimensions;
    this.events = {'mouseover': [], 'mouseout': []}
};

altoFuncs.prototype.highlight = function(text) {
    this.els.text.selectAll('span').classed('active', function (d, i, m) {
        return typeof text !== 'undefined' && (d.word.meta == text);
    });

    if (typeof text !== 'undefined') {
        var extent = this.getExtent(text);
        this.highlightExtents([extent]);
    } else {
        this.highlightExtents();
    }
    return this;
};

altoFuncs.prototype.highlightExtents = function(extents) {
    if (typeof extents === 'undefined' || extents.length === 0) {
        this.els.extent.classed('active', false);
        return this;
    }
    var els = this.els.extent.selectAll('span').data(extents);
    els.exit().remove();
    var appended = els.enter().append('span');
    this.els.extent.classed('active', true);

    for (var el of [els.transition().duration(500), appended]) {
        el.style('left', function (d) { return d[0]; })
           .style('top', function (d) { return d[1]; })
           .style('width', function (d) { return d[2]; })
           .style('height', function (d) { return d[3]; });
    }

    return this;
};

altoFuncs.prototype.getExtent = function(text) {
    var extents = this.els.text.selectAll('span').filter(function (d) {
        return d.word.meta == text;
    }).data();

    if (!extents.length) {
        return false;
    }
    var extent = extents.pop().extent;
    extent = new Extent(extent.x, extent.y, extent.w, extent.h);
    for (var e of extents) {
        extent.extend(e.extent.x, e.extent.y, e.extent.w, e.extent.h);
    }

    var scaler = this.scaler();
    return scaler.scale(extent);
};

altoFuncs.prototype.on = function (eventName, handler) {
    this.events[eventName].push(handler);
    return this;
};

altoFuncs.prototype.handleEvent = function (eventName) {
    var me = this;
    return function (d, i, m) {
        if (typeof me.events[eventName] !== 'undefined') {
            for (handler of me.events[eventName]) {
                handler.call(this, d, i, m);
            }
        }
    };
};

altoFuncs.prototype.scaler = function scaler(newW, newH, unit) {
    var w = this.page_dimensions[0],
        h = this.page_dimensions[1];

    if (typeof newW === 'undefined') {
        newW = 100;
    }
    if (typeof newH === 'undefined') {
        newH = 100;
    }
    if (typeof unit === 'undefined') {
        unit = '%';
    }

    var x = function (coord) {
        return (coord / w * newW) + unit;
    };
    var y = function (coord) {
        return (coord / h * newH) + unit;
    };
    return {
      x: x,
      y: y,
      scale: function (extent) {
        return [x(extent.x), y(extent.y), x(extent.w), y(extent.h)];
      }
   };
};


var alto = function alto(selection, links) {
  return selection.each(function(d, i) {
     if (this.__alto) {
        // already initialized
        return;
     }
     var data = this.getAttribute('data-alto');

     if (!data) {
        warn("No data for element", el);
        return el;
     }
     try {
        data = JSON.parse(data);
     } catch (e) {
        warn(e, el);
        return el;
     }

     var els = {};

     els.wrapper = wrap(this, 'alto-wrapper');
     els.main = wrap(els.wrapper, 'alto-main');
     els.text = els.wrapper.append('div').classed('alto-text', true);
     els.extra = els.main.append('div').classed('alto-extra', true);
     els.extent = els.wrapper.append('div').classed('alto-extent', true);

     this.__alto = new altoFuncs(els, data['page_dimensions']);
     var __alto = this.__alto;

     var id_prefix = 'alto_' + Date.now();

     var sc = __alto.scaler();
     var alto_links = {};

     els.text.selectAll('span').data(data['words']).enter()
       .append('span')
           .text(function(d) {return d.word.text;})
           .attr('title', function (d) { return d.word.full_text; })
           .style('left', function (d) { return sc.x(d.extent.x); })
           .style('top', function (d) { return sc.y(d.extent.y); })
           .style('width', function (d) { return sc.x(d.extent.w); })
           .style('height', function (d) { return sc.y(d.extent.h); })
           .attr('id', function(d, i) { return id_prefix + '_' + i; } )
           .on('mouseover', this.__alto.handleEvent('mouseover'))
           .on('mouseout', this.__alto.handleEvent('mouseout'))
           .each(function (d, i) {
           });

      __alto
          .on('mouseover', function (d) {
            __alto.highlight(d.word.meta);
          }).
          on('mouseout', function () {
            __alto.highlight();
          });
//      $this.data('alto-links', alto_links);
     /*
     els.extra.append('div').classed('alto-links', true)
     els.extra.select('div.alto-links').append('ul').selectAll('li').data(data['words']).enter()
          .append('li')
          .append('a')
          .classed('pure-button', true)
          .classed('pure-button-primary', true)
          .text(function (d) {
             return d.word.full_text;
          })
          .attr('href', function(d, i) {
             return '#' + id_prefix + '_' + i;
          })
          .attr('title', function (d) {
             return d.word.text;
          })
          .on('mouseover', function (d, i) {
             d3.select('#' + id_prefix + '_' + i).classed('active', true);
          })
          .on('mouseout', function (d, i) {
             d3.select('#' + id_prefix + '_' + i).classed('active', false);
          });
       */
  });
};

exports.alto = alto;
