/**
 * lightbox.js - 高清大图查看器 (适配桌面端与移动端)
 * 支持：鼠标滚轮缩放、双击缩放、手势捏合缩放、拖拽平移、键盘快捷键、原图直达
 */
(function() {
  'use strict';

  // 全局状态
  var currentImgUrl = '';
  var currentScale = 1.0;
  var minScale = 1.0;
  var maxScale = 4.0;
  var translateX = 0;
  var translateY = 0;

  // 拖拽与手势状态
  var isDragging = false;
  var dragStartX = 0;
  var dragStartY = 0;
  var lastTranslateX = 0;
  var lastTranslateY = 0;
  var hasMoved = false;

  // 移动端双指手势
  var isPinching = false;
  var initialPinchDist = 0;
  var initialPinchScale = 1.0;

  // 双击/双击判断
  var lastTapTime = 0;

  // DOM 元素引用
  var modalEl = null;
  var imgEl = null;
  var spinnerEl = null;
  var bodyEl = null;
  var titleEl = null;
  var skuEl = null;
  var origBtnEl = null;
  var scaleTextEl = null;

  /**
   * 自动在 body 中创建并初始化 Lightbox DOM 结构
   */
  function ensureLightboxDom() {
    if (document.getElementById('image-lightbox-modal')) {
      cacheDOMElements();
      return;
    }

    var html = `
<div id="image-lightbox-modal" class="image-lightbox-overlay" role="dialog" aria-modal="true" aria-label="图片预览">
  <div class="image-lightbox-header">
    <div class="image-lightbox-info">
      <div id="image-lightbox-title" class="image-lightbox-title">商品图片</div>
      <div id="image-lightbox-sku" class="image-lightbox-sku" style="display:none"></div>
    </div>
    <div class="image-lightbox-actions">
      <button class="image-lightbox-btn" id="image-lightbox-zoomout" title="缩小 (快捷键: -)">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line><line x1="8" y1="11" x2="14" y2="11"></line></svg>
        <span class="btn-text">缩小</span>
      </button>
      <button class="image-lightbox-btn" id="image-lightbox-reset" title="重置 1:1 (快捷键: 0)">
        <span id="image-lightbox-scale-text">100%</span>
      </button>
      <button class="image-lightbox-btn" id="image-lightbox-zoomin" title="放大 (快捷键: +)">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line><line x1="11" y1="8" x2="11" y2="14"></line><line x1="8" y1="11" x2="14" y2="11"></line></svg>
        <span class="btn-text">放大</span>
      </button>
      <a class="image-lightbox-btn" id="image-lightbox-orig" href="#" target="_blank" rel="noopener" title="在新标签页查看高清原图">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
        <span class="btn-text">原图</span>
      </a>
      <button class="image-lightbox-btn image-lightbox-close" id="image-lightbox-close" title="关闭 (ESC)">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      </button>
    </div>
  </div>
  <div class="image-lightbox-body" id="image-lightbox-body">
    <div class="image-lightbox-spinner" id="image-lightbox-spinner">
      <div class="spinner-circle"></div>
    </div>
    <img id="image-lightbox-img" class="image-lightbox-img" src="" alt="商品高清大图" draggable="false">
  </div>
  <div class="image-lightbox-footer">
    <span class="desktop-hint">💡 鼠标滚轮/双击缩放 · 拖拽平移 · ESC / 点击背景关闭</span>
    <span class="mobile-hint">💡 双指捏合/双击缩放 · 拖动平移 · 点击遮罩关闭</span>
  </div>
</div>`;

    var div = document.createElement('div');
    div.innerHTML = html;
    document.body.appendChild(div.firstElementChild);
    cacheDOMElements();
    bindEvents();
  }

  function cacheDOMElements() {
    modalEl     = document.getElementById('image-lightbox-modal');
    imgEl       = document.getElementById('image-lightbox-img');
    spinnerEl   = document.getElementById('image-lightbox-spinner');
    bodyEl      = document.getElementById('image-lightbox-body');
    titleEl     = document.getElementById('image-lightbox-title');
    skuEl       = document.getElementById('image-lightbox-sku');
    origBtnEl   = document.getElementById('image-lightbox-orig');
    scaleTextEl = document.getElementById('image-lightbox-scale-text');
  }

  function updateTransform(withTransition) {
    if (!imgEl) return;
    if (withTransition === false) {
      imgEl.classList.add('no-transition');
    } else {
      imgEl.classList.remove('no-transition');
    }

    imgEl.style.transform = 'translate3d(' + translateX + 'px, ' + translateY + 'px, 0px) scale(' + currentScale + ')';
    if (scaleTextEl) {
      scaleTextEl.textContent = Math.round(currentScale * 100) + '%';
    }

    if (bodyEl) {
      if (currentScale > 1.05) {
        bodyEl.classList.add('draggable');
      } else {
        bodyEl.classList.remove('draggable');
        bodyEl.classList.remove('panning');
      }
    }
  }

  function resetView() {
    currentScale = 1.0;
    translateX = 0;
    translateY = 0;
    updateTransform(true);
  }

  function setScale(newScale, withTransition) {
    newScale = Math.max(minScale, Math.min(maxScale, newScale));
    if (newScale === minScale) {
      translateX = 0;
      translateY = 0;
    } else {
      // 限制位移范围，防止图片移出屏幕
      clampTranslation(newScale);
    }
    currentScale = newScale;
    updateTransform(withTransition);
  }

  function clampTranslation(scale) {
    if (!bodyEl || !imgEl) return;
    var rect = bodyEl.getBoundingClientRect();
    var imgRect = imgEl.getBoundingClientRect();
    // 允许平移的最大范围
    var maxTx = Math.max(0, (imgRect.width * (scale / currentScale) - rect.width) / 2 + 100);
    var maxTy = Math.max(0, (imgRect.height * (scale / currentScale) - rect.height) / 2 + 100);
    translateX = Math.max(-maxTx, Math.min(maxTx, translateX));
    translateY = Math.max(-maxTy, Math.min(maxTy, translateY));
  }

  function bindEvents() {
    if (!modalEl) return;

    // 缩放按钮
    var zoomInBtn = document.getElementById('image-lightbox-zoomin');
    if (zoomInBtn) {
      zoomInBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        setScale(currentScale + 0.35, true);
      });
    }

    var zoomOutBtn = document.getElementById('image-lightbox-zoomout');
    if (zoomOutBtn) {
      zoomOutBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        setScale(currentScale - 0.35, true);
      });
    }

    var resetBtn = document.getElementById('image-lightbox-reset');
    if (resetBtn) {
      resetBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        resetView();
      });
    }

    // 关闭按钮
    var closeBtn = document.getElementById('image-lightbox-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        closeImageLightbox();
      });
    }

    // 鼠标滚轮缩放
    bodyEl.addEventListener('wheel', function(e) {
      e.preventDefault();
      var delta = e.deltaY < 0 ? 0.25 : -0.25;
      setScale(currentScale + delta, false);
    }, { passive: false });

    // 桌面端鼠标拖拽
    bodyEl.addEventListener('mousedown', function(e) {
      if (e.button !== 0) return; // 仅左键
      isDragging = true;
      hasMoved = false;
      dragStartX = e.clientX;
      dragStartY = e.clientY;
      lastTranslateX = translateX;
      lastTranslateY = translateY;
      bodyEl.classList.add('panning');
      imgEl.classList.add('no-transition');
    });

    window.addEventListener('mousemove', function(e) {
      if (!isDragging) return;
      var dx = e.clientX - dragStartX;
      var dy = e.clientY - dragStartY;
      if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
        hasMoved = true;
      }
      if (currentScale > 1.0) {
        translateX = lastTranslateX + dx;
        translateY = lastTranslateY + dy;
        updateTransform(false);
      }
    });

    window.addEventListener('mouseup', function(e) {
      if (!isDragging) return;
      isDragging = false;
      if (bodyEl) bodyEl.classList.remove('panning');
      if (imgEl) imgEl.classList.remove('no-transition');

      // 如果未发生位移，且点击的是背景区域（非图片本身），则关闭
      if (!hasMoved && e.target === bodyEl) {
        closeImageLightbox();
      }
    });

    // 双击/双击放大/还原
    bodyEl.addEventListener('dblclick', function(e) {
      e.preventDefault();
      if (currentScale > 1.05) {
        resetView();
      } else {
        setScale(2.0, true);
      }
    });

    // 移动端 Touch 事件（支持平移与双指捏合缩放）
    bodyEl.addEventListener('touchstart', function(e) {
      if (e.touches.length === 2) {
        isPinching = true;
        isDragging = false;
        var t1 = e.touches[0];
        var t2 = e.touches[1];
        initialPinchDist = Math.hypot(t1.clientX - t2.clientX, t1.clientY - t2.clientY);
        initialPinchScale = currentScale;
        imgEl.classList.add('no-transition');
      } else if (e.touches.length === 1) {
        isDragging = true;
        hasMoved = false;
        var t = e.touches[0];
        dragStartX = t.clientX;
        dragStartY = t.clientY;
        lastTranslateX = translateX;
        lastTranslateY = translateY;
        imgEl.classList.add('no-transition');

        // 双击模拟判断 (300ms 以内连击)
        var now = Date.now();
        if (now - lastTapTime < 300) {
          e.preventDefault();
          if (currentScale > 1.05) {
            resetView();
          } else {
            setScale(2.0, true);
          }
          lastTapTime = 0;
          return;
        }
        lastTapTime = now;
      }
    }, { passive: false });

    bodyEl.addEventListener('touchmove', function(e) {
      if (isPinching && e.touches.length === 2) {
        e.preventDefault();
        var t1 = e.touches[0];
        var t2 = e.touches[1];
        var dist = Math.hypot(t1.clientX - t2.clientX, t1.clientY - t2.clientY);
        if (initialPinchDist > 0) {
          var factor = dist / initialPinchDist;
          setScale(initialPinchScale * factor, false);
        }
      } else if (isDragging && e.touches.length === 1) {
        var t = e.touches[0];
        var dx = t.clientX - dragStartX;
        var dy = t.clientY - dragStartY;
        if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
          hasMoved = true;
        }
        if (currentScale > 1.0) {
          e.preventDefault();
          translateX = lastTranslateX + dx;
          translateY = lastTranslateY + dy;
          updateTransform(false);
        }
      }
    }, { passive: false });

    bodyEl.addEventListener('touchend', function(e) {
      if (isPinching && e.touches.length < 2) {
        isPinching = false;
        initialPinchDist = 0;
      }
      if (isDragging && e.touches.length === 0) {
        isDragging = false;
        if (imgEl) imgEl.classList.remove('no-transition');
        // 点击背景关闭
        if (!hasMoved && currentScale <= 1.05 && e.target === bodyEl) {
          closeImageLightbox();
        }
      }
    });

    // 键盘快捷键监听
    window.addEventListener('keydown', function(e) {
      if (!modalEl || !modalEl.classList.contains('open')) return;
      if (e.key === 'Escape') {
        closeImageLightbox();
      } else if (e.key === '+' || e.key === '=') {
        setScale(currentScale + 0.35, true);
      } else if (e.key === '-' || e.key === '_') {
        setScale(currentScale - 0.35, true);
      } else if (e.key === '0') {
        resetView();
      }
    });
  }

  /**
   * 打开图片大图 Lightbox
   * @param {string} url 图片 URL
   * @param {string} [title] 商品名称
   * @param {string} [sku] 商品 SKU
   */
  window.openImageLightbox = function(url, title, sku) {
    if (!url) return;
    ensureLightboxDom();

    currentImgUrl = url;
    resetView();

    if (titleEl) {
      titleEl.textContent = title || '商品高清大图';
      titleEl.title = title || '';
    }

    if (skuEl) {
      if (sku) {
        skuEl.textContent = 'SKU: ' + sku;
        skuEl.style.display = 'inline-block';
      } else {
        skuEl.style.display = 'none';
      }
    }

    if (origBtnEl) {
      origBtnEl.href = url;
    }

    if (spinnerEl) spinnerEl.style.display = 'flex';
    if (imgEl) {
      imgEl.style.opacity = '0';
      imgEl.onload = function() {
        if (spinnerEl) spinnerEl.style.display = 'none';
        imgEl.style.opacity = '1';
      };
      imgEl.onerror = function() {
        if (spinnerEl) spinnerEl.style.display = 'none';
        imgEl.style.opacity = '1';
      };
      imgEl.src = url;
    }

    modalEl.classList.add('open');
    document.body.style.overflow = 'hidden'; // 防止背景滚动
  };

  /**
   * 关闭大图 Lightbox
   */
  window.closeImageLightbox = function() {
    if (!modalEl) return;
    modalEl.classList.remove('open');
    document.body.style.overflow = '';
    resetView();
  };

  /**
   * 从带有 data- 属性的 DOM 元素触发大图查看
   */
  window.previewProductImage = function(el) {
    if (!el) return;
    var img = el.getAttribute('data-img') || '';
    if (!img) {
      // 尝试在内部查找 img 标签的 src
      var innerImg = el.querySelector('img');
      if (innerImg) img = innerImg.src;
    }
    if (!img) return;

    var title = el.getAttribute('data-title') || el.getAttribute('title') || '';
    var sku = el.getAttribute('data-sku') || '';
    window.openImageLightbox(img, title, sku);
  };

  // 页面加载完成后自动准备 DOM
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ensureLightboxDom);
  } else {
    ensureLightboxDom();
  }
})();
