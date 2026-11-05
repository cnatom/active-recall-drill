// 图与要点联动：悬停图上某部分时高亮对应要点（其余半透明），移出恢复。
// 每个 .stage 各自绑定自己的 svg 与 .side 里的要点；图元用 data-p="1" 或 "2,5" 标注。
(function () {
  function nums(el) {
    return (el.getAttribute('data-p') || '').split(',').map(function (x) {
      return parseInt(x, 10);
    }).filter(function (n) { return !isNaN(n); });
  }

  Array.prototype.forEach.call(document.querySelectorAll('.stage'), function (stage) {
    var svg = stage.querySelector('svg');
    var items = Array.prototype.slice.call(stage.querySelectorAll('.points li'));
    if (!svg || !items.length) return;
    var shapes = Array.prototype.slice.call(svg.querySelectorAll('[data-p]'));


    function clear() {
      items.forEach(function (li) { li.classList.remove('hot', 'dim'); });
      shapes.forEach(function (el) { el.classList.remove('ph'); });
    }
    function focus(list) {
      items.forEach(function (li, i) {
        var n = i + 1;
        var on = list.indexOf(n) >= 0;
        li.classList.toggle('dim', !on);
        li.classList.toggle('hot', on);
      });
      shapes.forEach(function (el) {
        el.classList.toggle('ph', nums(el).some(function (n) { return list.indexOf(n) >= 0; }));
      });
    }

    svg.addEventListener('mouseover', function (e) {
      var el = e.target;
      while (el && el !== svg) {
        if (el.getAttribute && el.getAttribute('data-p')) {
          focus(nums(el));
          return;
        }
        el = el.parentNode;
      }
      clear();
    });
    svg.addEventListener('mouseleave', clear);

    items.forEach(function (li, i) {
      li.addEventListener('mouseenter', function () { focus([i + 1]); });
      li.addEventListener('mouseleave', clear);
    });
  });
})();
