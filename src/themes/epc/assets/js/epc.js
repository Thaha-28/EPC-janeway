/* EPC theme interactions: mobile nav, dropdown keyboard support.
   No frameworks. Respects prefers-reduced-motion (handled in CSS). */
(function () {
  "use strict";

  function closeAllDrops(except) {
    var drops = document.querySelectorAll(".epc-nav-drop > button[aria-expanded='true']");
    for (var i = 0; i < drops.length; i++) {
      if (drops[i] !== except) {
        drops[i].setAttribute("aria-expanded", "false");
        var ul = drops[i].parentElement.querySelector("ul");
        if (ul) ul.hidden = true;
      }
    }
  }

  // About-style dropdowns: click toggles (touch + keyboard), Escape closes.
  document.addEventListener("click", function (ev) {
    var btn = ev.target.closest(".epc-nav-drop > button");
    if (btn) {
      var open = btn.getAttribute("aria-expanded") === "true";
      closeAllDrops(btn);
      btn.setAttribute("aria-expanded", open ? "false" : "true");
      var ul = btn.parentElement.querySelector("ul");
      if (ul) ul.hidden = open;
      return;
    }
    if (!ev.target.closest(".epc-nav-drop")) closeAllDrops(null);
  });
  document.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape") {
      var openBtn = document.querySelector(".epc-nav-drop > button[aria-expanded='true']");
      closeAllDrops(null);
      if (openBtn) openBtn.focus();
      var nav = document.querySelector(".epc-nav[data-open='true']");
      if (nav) {
        nav.setAttribute("data-open", "false");
        var burger = nav.querySelector(".epc-hamburger");
        if (burger) {
          burger.setAttribute("aria-expanded", "false");
          burger.focus();
        }
      }
    }
  });

  // Mobile hamburger.
  document.addEventListener("click", function (ev) {
    var burger = ev.target.closest(".epc-hamburger");
    if (!burger) return;
    var nav = burger.closest(".epc-nav");
    if (!nav) return;
    var open = nav.getAttribute("data-open") === "true";
    nav.setAttribute("data-open", open ? "false" : "true");
    burger.setAttribute("aria-expanded", open ? "false" : "true");
  });

  // Sync OLH header toggles (Foundation) with aria when present.
  document.addEventListener("click", function (ev) {
    var t = ev.target.closest("[data-responsive-toggle]");
    if (!t) return;
    window.setTimeout(function () {
      var target = document.getElementById(t.getAttribute("data-responsive-toggle"));
      if (target) t.setAttribute("aria-expanded", target.style.display === "none" ? "false" : "true");
    }, 50);
  });
})();
