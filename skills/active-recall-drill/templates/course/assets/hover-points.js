// 图与要点联动：图上自动标圆圈序号，悬停某部分时高亮对应要点（其余半透明），移出恢复。
// 图元用 data-p="1" 或 data-p="2,5" 标注与哪些要点对应。
(function () {
  var svg = document.querySelector('.stage svg');
  var items = Array.prototype.slice.call(document.querySelectorAll('.points li'));
  if (!svg || !items.length) return;
  var shapes = Array.prototype.slice.call(svg.querySelectorAll('[data-p]'));
  var NS = 'http://www.w3.org/2000/svg';

  function nums(el) {
    return (el.getAttribute('data-p') || '').split(',').map(function (x) {
      return parseInt(x, 10);
    }).filter(function (n) { return !isNaN(n); });
  }

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

  // 鼠标停在要点上时，也把图上对应的部分点亮
  items.forEach(function (li, i) {
    li.addEventListener('mouseenter', function () { focus([i + 1]); });
    li.addEventListener('mouseleave', clear);
  });
})();
