// 地图式查看：图放在固定框里，拖动平移，滚轮或按钮缩放
(function () {
  Array.prototype.forEach.call(document.querySelectorAll('.mapview'), function (view) {
    var canvas = view.querySelector('.mapcanvas');
    if (!canvas) return;
    var zoom = 1;
    var scale = view.querySelector('.mapscale');
    // 初始放大一点，文字可读；仍可缩小看全图
    zoom = 1.35;
    canvas.style.width = (zoom * 100) + '%';

    function syncScale() { if (scale) scale.textContent = Math.round(zoom * 100) + '%'; }
    var dragging = false;
    var startX = 0, startY = 0, startL = 0, startT = 0;

    requestAnimationFrame(function () {
      view.scrollLeft = (canvas.clientWidth - view.clientWidth) / 2;
      view.scrollTop = (canvas.clientHeight - view.clientHeight) / 2;
      if (scale) scale.textContent = Math.round(zoom * 100) + '%';
    });

    function setZoom(next, cx, cy) {
      next = Math.min(4, Math.max(1, next));
      if (next === zoom) return;
      var rect = view.getBoundingClientRect();
      var px = (typeof cx === 'number' ? cx : rect.width / 2) / rect.width;
      var py = (typeof cy === 'number' ? cy : rect.height / 2) / rect.height;
      var oldW = canvas.clientWidth, oldH = canvas.clientHeight;
      zoom = next;
      canvas.style.width = (zoom * 100) + '%';
      syncScale();
      requestAnimationFrame(function () {
        view.scrollLeft += (canvas.clientWidth - oldW) * px;
        view.scrollTop += (canvas.clientHeight - oldH) * py;
      });
    }

    view.addEventListener('pointerdown', function (e) {
      if (e.target.closest('.mapctl, .mapscale')) return;
      dragging = true;
      view.classList.add('dragging');
      try { view.setPointerCapture(e.pointerId); } catch (err) {}
      startX = e.clientX; startY = e.clientY;
      startL = view.scrollLeft; startT = view.scrollTop;
    });
    view.addEventListener('pointermove', function (e) {
      if (!dragging) return;
      view.scrollLeft = startL - (e.clientX - startX);
      view.scrollTop = startT - (e.clientY - startY);
    });
    function stop() { dragging = false; view.classList.remove('dragging'); }
    view.addEventListener('pointerup', stop);
    view.addEventListener('pointercancel', stop);
    view.addEventListener('pointerleave', function () { if (!dragging) return; });

    view.addEventListener('wheel', function (e) {
      e.preventDefault();
      var r = view.getBoundingClientRect();
      setZoom(zoom * (e.deltaY < 0 ? 1.15 : 1 / 1.15), e.clientX - r.left, e.clientY - r.top);
    }, { passive: false });

    Array.prototype.forEach.call(view.querySelectorAll('[data-z]'), function (btn) {
      btn.addEventListener('click', function () {
        var z = btn.getAttribute('data-z');
        if (z === 'reset') {
          zoom = 1;
          canvas.style.width = '100%';
          view.scrollTo(0, 0);
          syncScale();
        } else {
          setZoom(zoom * (z === 'in' ? 1.3 : 1 / 1.3));
        }
      });
    });
  });
})();
