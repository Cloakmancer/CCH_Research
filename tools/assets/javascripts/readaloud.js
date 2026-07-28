/*
 * Read-aloud button.
 *
 * Chrome on Android only offers "Listen to this page" when its distiller judges
 * a page readable, and that verdict is a closed heuristic — these pages never
 * got the option. This drives the Web Speech API directly instead, so the
 * behaviour is ours rather than the browser's guess.
 *
 * Two deliberate choices about WHAT gets read:
 *   - Closed <details> are skipped except for their summary. The problem set
 *     hides its solutions on purpose; reading them aloud unprompted would
 *     destroy the retrieval practice the format exists for.
 *   - Code blocks, figures and permalink anchors are skipped. Reading a Python
 *     block aloud is noise, and every figure already carries alt text that a
 *     real screen reader will pick up on its own.
 */
(function () {
  "use strict";

  if (!("speechSynthesis" in window)) return;

  var synth = window.speechSynthesis;
  var chunks = [];
  var index = 0;
  var playing = false;
  var btn;

  /* ---------------------------------------------------------------- text */

  function collect(root) {
    var out = [];
    (function walk(node) {
      for (var i = 0; i < node.childNodes.length; i++) {
        var n = node.childNodes[i];
        if (n.nodeType === 3) {
          var s = n.nodeValue.replace(/\s+/g, " ");
          if (s.trim()) out.push(s);
          continue;
        }
        if (n.nodeType !== 1) continue;

        var tag = n.tagName.toLowerCase();
        if (tag === "pre" || tag === "img" || tag === "svg" ||
            n.classList.contains("headerlink") ||
            n.classList.contains("katex-html") ||
            n.getAttribute("aria-hidden") === "true") continue;

        if (tag === "details") {
          var sum = n.querySelector("summary");
          if (sum) { walk(sum); out.push(". "); }
          if (!n.open) { out.push("Solution hidden. "); continue; }
          for (var j = 0; j < n.childNodes.length; j++) {
            if (n.childNodes[j] !== sum) walk(n.childNodes[j]);
          }
          continue;
        }

        walk(n);
        if (/^(p|li|h1|h2|h3|h4|h5|h6|td|th|blockquote|div)$/.test(tag)) out.push(". ");
      }
    })(root);

    return out.join("")
      .replace(/\s+/g, " ")
      .replace(/(\.\s*)+\./g, ".")
      .trim();
  }

  /* Chrome stops a long utterance after roughly fifteen seconds, so the text is
     queued as short pieces split on sentence ends rather than as one blob. */
  var MAX = 220;

  function split(text) {
    var parts = text.match(/[^.!?]+[.!?]+|\S[^.!?]*$/g) || [];
    var out = [], buf = "";

    // A single sentence can exceed the limit on its own — these pages have
    // plenty — so oversized parts are broken again at word boundaries rather
    // than pushed through whole.
    var pieces = [];
    parts.forEach(function (p) {
      if (p.length <= MAX) { pieces.push(p); return; }
      var words = p.split(" "), line = "";
      words.forEach(function (w) {
        if ((line + " " + w).trim().length > MAX) { pieces.push(line.trim()); line = w; }
        else line += " " + w;
      });
      if (line.trim()) pieces.push(line.trim());
    });

    pieces.forEach(function (p) {
      if ((buf + " " + p).trim().length > MAX) { if (buf.trim()) out.push(buf.trim()); buf = p; }
      else buf += " " + p;
    });
    if (buf.trim()) out.push(buf.trim());
    return out;
  }

  /* -------------------------------------------------------------- speech */

  function speakFrom(i) {
    if (i >= chunks.length) { stop(); return; }
    index = i;
    var u = new SpeechSynthesisUtterance(chunks[i]);
    u.lang = document.documentElement.lang || "en";
    u.rate = 1.0;
    u.onend = function () { if (playing) speakFrom(index + 1); };
    u.onerror = function () { stop(); };
    synth.speak(u);
  }

  function start() {
    var article = document.querySelector("article.md-typeset");
    if (!article) return;
    var text = collect(article);
    if (!text) return;
    chunks = split(text);
    playing = true;
    render();
    synth.cancel();
    speakFrom(0);
  }

  function stop() {
    playing = false;
    synth.cancel();
    render();
  }

  /* ----------------------------------------------------------------- ui */

  var PLAY = '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">' +
             '<path fill="currentColor" d="M8 5v14l11-7z"/></svg>';
  var STOP = '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">' +
             '<path fill="currentColor" d="M6 6h12v12H6z"/></svg>';

  function render() {
    if (!btn) return;
    btn.innerHTML = playing ? STOP : PLAY;
    btn.setAttribute("aria-label", playing ? "Stop reading this page"
                                           : "Read this page aloud");
    btn.setAttribute("aria-pressed", playing ? "true" : "false");
    btn.classList.toggle("md-readaloud--on", playing);
  }

  /* The button lives in the header, beside the palette toggle, rather than
     floating over the page. A fixed bottom-right control sits on top of the
     right-hand table of contents on desktop and steals clicks from the last few
     entries; the header is where Material puts its own controls anyway. */
  function mount() {
    btn = document.createElement("button");
    btn.className = "md-header__button md-icon md-readaloud";
    btn.type = "button";
    btn.addEventListener("click", function () { playing ? stop() : start(); });

    var opt = document.querySelector(".md-header__inner .md-header__option");
    var header = document.querySelector(".md-header__inner");
    if (opt && opt.parentNode) opt.parentNode.insertBefore(btn, opt);
    else if (header) header.appendChild(btn);
    else { btn.classList.add("md-readaloud--floating"); document.body.appendChild(btn); }

    render();
  }

  // Never keep talking over a page the reader has left.
  window.addEventListener("beforeunload", function () { synth.cancel(); });
  document.addEventListener("visibilitychange", function () {
    if (document.hidden && playing) stop();
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();
