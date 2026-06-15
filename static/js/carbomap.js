/* Carbomap — loads carbomap/data.json and renders a Google map + list + filters.
   Plain vanilla JS. The map only runs when a Maps API key was built in; the list
   and filters work regardless. */
(function () {
  "use strict";

  var hasMap = !!(window.CARBOMAP && window.CARBOMAP.hasMap);
  var DATA = [];
  var markers = [];               // [{ data, marker }]
  var map = null, infoWindow = null, bounds = null;

  function el(id) { return document.getElementById(id); }

  // ----- rendering helpers ------------------------------------------------ //
  function starHtml(rating) {
    var pct = Math.max(0, Math.min(5, rating)) / 5 * 100;
    return '<span class="stars" role="img" aria-label="' + rating +
      ' out of 5"><span class="stars-fill" style="width:' + pct + '%"></span></span>';
  }

  function priceText(r) {
    if (r.price === null || r.price === undefined || r.price === "") return "";
    return r.currency ? (r.currency + " " + r.price) : ("" + r.price);
  }

  function badges(r) {
    var g = r.guanciale
      ? '<span class="cb-badge yes">guanciale</span>'
      : '<span class="cb-badge no">no guanciale</span>';
    var c = r.cream
      ? '<span class="cb-badge cream">cream</span>'
      : '<span class="cb-badge nocream">no cream</span>';
    return g + " " + c;
  }

  function metaLine(r) {
    var loc = [r.city, r.country].filter(Boolean).join(", ");
    var price = priceText(r);
    return (loc ? '<p class="cb-loc">' + loc + "</p>" : "") +
      '<p class="cb-rate">' + starHtml(r.rating) +
      ' <span class="cb-num">' + r.rating.toFixed(1) + "</span>" +
      (price ? ' · <span class="cb-price">' + price + "</span>" : "") + "</p>" +
      '<p class="cb-badges">' + badges(r) + "</p>";
  }

  function popupHtml(r) {
    var img = r.image ? '<img class="cb-pop-img" src="' + r.image + '" alt="">' : "";
    return '<div class="cb-pop">' + img + "<h3>" + r.name + "</h3>" +
      metaLine(r) + '<div class="cb-note">' + (r.note || "") + "</div></div>";
  }

  function cardHtml(r) {
    var img = r.image
      ? '<img class="cb-card-img" src="' + r.image + '" alt="">'
      : '<div class="cb-card-img cb-card-noimg">no photo</div>';
    return '<article class="cb-card" data-slug="' + r.slug + '">' + img +
      '<div class="cb-card-body"><h3>' + r.name + "</h3>" +
      metaLine(r) + '<div class="cb-note">' + (r.note || "") + "</div></div></article>";
  }

  // ----- filtering -------------------------------------------------------- //
  function currentFilters() {
    var slider = el("f-price");
    return {
      minRating: parseFloat(el("f-rating").value) || 0,
      maxPrice: parseInt(slider.value, 10),
      priceIsAny: slider.value === slider.max,
      guanciale: el("f-guanciale").value,
      cream: el("f-cream").value,
    };
  }

  function matches(r, f) {
    if (r.rating < f.minRating) return false;
    if (!f.priceIsAny && typeof r.price === "number" && r.price > f.maxPrice) return false;
    if (f.guanciale === "yes" && !r.guanciale) return false;
    if (f.guanciale === "no" && r.guanciale) return false;
    if (f.cream === "yes" && !r.cream) return false;
    if (f.cream === "no" && r.cream) return false;
    return true;
  }

  function apply() {
    var f = currentFilters();
    var visible = DATA.filter(function (r) { return matches(r, f); });
    el("cb-count").textContent = visible.length;
    renderList(visible);
    if (map) {
      bounds = new google.maps.LatLngBounds();
      markers.forEach(function (m) {
        var show = matches(m.data, f);
        m.marker.setMap(show ? map : null);
        if (show) bounds.extend(m.marker.getPosition());
      });
      if (!bounds.isEmpty()) map.fitBounds(bounds);
    }
  }

  function renderList(list) {
    var c = el("cb-list");
    if (!list.length) {
      c.innerHTML = '<p class="cb-empty">No restaurants match these filters.</p>';
      return;
    }
    c.innerHTML = list.map(cardHtml).join("");
    c.querySelectorAll(".cb-card").forEach(function (card) {
      card.addEventListener("click", function () { focusMarker(card.dataset.slug); });
    });
  }

  // ----- map -------------------------------------------------------------- //
  function openInfo(entry) {
    if (!infoWindow) return;
    infoWindow.setContent(popupHtml(entry.data));
    infoWindow.open({ anchor: entry.marker, map: map });
  }

  function focusMarker(slug) {
    var entry = markers.filter(function (m) { return m.data.slug === slug; })[0];
    if (!entry || !map) return;
    setView("map");
    map.panTo(entry.marker.getPosition());
    map.setZoom(Math.max(map.getZoom() || 0, 15));
    openInfo(entry);
  }

  async function initMap() {
    var maps = await google.maps.importLibrary("maps");
    var markerLib = await google.maps.importLibrary("marker");
    map = new maps.Map(el("cb-map"), {
      center: { lat: 41.9, lng: 12.5 }, zoom: 5,
      mapTypeControl: false, streetViewControl: false,
    });
    infoWindow = new maps.InfoWindow();
    markers = DATA.map(function (r) {
      var marker = new markerLib.Marker({
        position: { lat: r.lat, lng: r.lng }, title: r.name,
      });
      var entry = { data: r, marker: marker };
      marker.addListener("click", function () { openInfo(entry); });
      return entry;
    });
    apply();
  }

  // ----- view toggle & wiring -------------------------------------------- //
  function setView(view) {
    if (view === "map" && !hasMap) view = "list";
    el("cb-map").hidden = view !== "map";
    el("cb-list").hidden = view !== "list";
    document.querySelectorAll(".cb-views button").forEach(function (b) {
      b.classList.toggle("active", b.dataset.view === view);
    });
    if (view === "map" && map) {
      google.maps.event.trigger(map, "resize");
      if (bounds && !bounds.isEmpty()) map.fitBounds(bounds);
    }
  }

  function updatePriceLabel() {
    var s = el("f-price");
    el("f-price-val").textContent = (s.value === s.max) ? "any" : ("≤ " + s.value);
  }

  function setupPriceSlider() {
    var prices = DATA.map(function (r) { return r.price; })
      .filter(function (p) { return typeof p === "number"; });
    var max = prices.length ? Math.ceil(Math.max.apply(null, prices)) : 100;
    var s = el("f-price");
    s.max = String(max); s.value = String(max);
    updatePriceLabel();
  }

  function wire() {
    ["f-rating", "f-guanciale", "f-cream"].forEach(function (id) {
      el(id).addEventListener("change", apply);
    });
    el("f-price").addEventListener("input", function () { updatePriceLabel(); apply(); });
    el("f-reset").addEventListener("click", function () {
      el("f-rating").value = "0";
      el("f-guanciale").value = "";
      el("f-cream").value = "";
      var s = el("f-price"); s.value = s.max;
      updatePriceLabel(); apply();
    });
    document.querySelectorAll(".cb-views button").forEach(function (b) {
      b.addEventListener("click", function () { setView(b.dataset.view); });
    });
  }

  async function start() {
    try {
      var res = await fetch("/carbomap/data.json");
      DATA = await res.json();
    } catch (e) {
      DATA = [];
      console.error("Carbomap: could not load data.json", e);
    }
    setupPriceSlider();
    wire();
    setView(hasMap ? "map" : "list");
    if (hasMap) {
      try { await initMap(); }
      catch (e) { console.error("Carbomap: map failed to load", e); setView("list"); apply(); }
    } else {
      apply();
    }
  }

  if (document.readyState !== "loading") start();
  else document.addEventListener("DOMContentLoaded", start);
})();
