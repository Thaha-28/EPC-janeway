(function () {
  "use strict";

  var NAV_ID = "epc-nav";

  function navRoot() {
    return document.getElementById(NAV_ID);
  }

  function closeDrops(except) {
    var drops = document.querySelectorAll(".epc-nav-drop > button[aria-expanded='true']");
    for (var i = 0; i < drops.length; i++) {
      if (drops[i] === except) continue;
      drops[i].setAttribute("aria-expanded", "false");
      var menu = drops[i].parentElement.querySelector("ul");
      if (menu) menu.hidden = true;
    }
  }

  function toggleDrop(btn) {
    var willOpen = btn.getAttribute("aria-expanded") !== "true";
    closeDrops(btn);
    btn.setAttribute("aria-expanded", willOpen ? "true" : "false");
    var menu = btn.parentElement.querySelector("ul");
    if (menu) menu.hidden = !willOpen;
    return willOpen;
  }

  function setNav(open) {
    var nav = navRoot();
    if (!nav) return;
    nav.setAttribute("data-open", open ? "true" : "false");
    var burger = document.querySelector(".epc-hamburger");
    if (burger) burger.setAttribute("aria-expanded", open ? "true" : "false");
  }

  function setSearch(open) {
    var form = document.getElementById("epc-search");
    if (!form) return;
    form.setAttribute("data-open", open ? "true" : "false");
    var toggle = document.querySelector(".epc-search-toggle");
    if (toggle) toggle.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) {
      var input = document.getElementById("epc-search-input");
      if (input) input.focus();
    }
  }

  document.addEventListener("click", function (ev) {
    var dropBtn = ev.target.closest(".epc-nav-drop > button");
    if (dropBtn) {
      toggleDrop(dropBtn);
      return;
    }
    if (!ev.target.closest(".epc-nav-drop")) closeDrops(null);

    var burger = ev.target.closest(".epc-hamburger");
    if (burger) {
      var nav = navRoot();
      if (nav) setNav(nav.getAttribute("data-open") !== "true");
      return;
    }

    var searchToggle = ev.target.closest(".epc-search-toggle");
    if (searchToggle) {
      var form = document.getElementById("epc-search");
      if (form) setSearch(form.getAttribute("data-open") !== "true");
      return;
    }

    if (!ev.target.closest(".epc-header")) {
      setSearch(false);
      var openNav = navRoot();
      if (openNav && window.matchMedia("(max-width: 1100px)").matches) setNav(false);
    }
  });

  document.addEventListener("keydown", function (ev) {
    if (ev.key !== "Escape") return;
    var openBtn = document.querySelector(".epc-nav-drop > button[aria-expanded='true']");
    closeDrops(null);
    if (openBtn) openBtn.focus();
    var nav = navRoot();
    if (nav && nav.getAttribute("data-open") === "true") {
      setNav(false);
      var burger = document.querySelector(".epc-hamburger");
      if (burger) burger.focus();
    }
    setSearch(false);
  });

  document.addEventListener("focusin", function (ev) {
    var drop = ev.target.closest(".epc-nav-drop");
    if (drop) {
      var btn = drop.querySelector("button");
      if (btn && btn.getAttribute("aria-expanded") !== "true") {
        closeDrops(btn);
        btn.setAttribute("aria-expanded", "true");
        var menu = drop.querySelector("ul");
        if (menu) menu.hidden = false;
      }
    }
  });
})();