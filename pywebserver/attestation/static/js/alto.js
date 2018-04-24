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
   if (typeof console.lo  === 'function') {
      return console.log.apply(this, arguments);
   }
}

var scale = function scale(w, h, newW, newH, unit) {
   if (typeof newW === 'undefined') {
      newW = 100;
   }
   if (typeof newH === 'undefined') {
      newH = 100;
   }
   if (typeof unit === 'undefined') {
      unit = '%';
   }
   return {
      x: function (coord) {
         return (coord / w * newW) + unit;
      },
      y: function (coord) {
         return (coord / h * newH) + unit;
      }
   };
};

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

var alto = function alto(selection) {
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

     var $this = d3.select(this);
     var els = {};

     els.wrapper = wrap(this, 'alto-wrapper');
     els.main = wrap(els.wrapper, 'alto-main');
     els.text = els.wrapper.append('div').classed('alto-text', true);
     els.extra = els.main.append('div').classed('alto-extra', true);
     console.log(els);
     window.els = els;
     window.wrapf = wrap;

     var id_prefix = 'alto_' + Date.now();

     var sc = scale.apply(null, data['page_dimensions']);
     window.sc = sc;
     els.text.selectAll('span').data(data['words']).enter()
       .append('span')
           .text(function(d) {return d.word.text;})
           .attr('title', function (d) { return d.word.full_text; })
           .style('left', function (d) { return sc.x(d.extent.x); })
           .style('top', function (d) { return sc.y(d.extent.y); })
           .style('width', function (d) { return sc.x(d.extent.w); })
           .style('height', function (d) { return sc.y(d.extent.h); })
           .attr('id', function(d, i) { return id_prefix + '_' + i; } )
           .each(function () {

           });

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
  });
};

exports.alto = alto;
