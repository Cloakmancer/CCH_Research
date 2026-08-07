/*
 * Groups each top-level H2 (and everything up to the next H2) into a
 * <div class="note-card"> so the notes read like the interactive study-notes
 * page — one boxed card per topic — without touching any markdown source.
 *
 * Deliberately does NOT touch:
 *   - anything before the first H2 (the H1 and any lead-in paragraph stay
 *     outside a card, same as the interactive pages' masthead)
 *   - the left nav, the right-hand "on this page" TOC, or search — those are
 *     rendered from heading ids, not from where a heading sits in the DOM,
 *     so wrapping it one level deeper changes nothing for them
 *   - pages with no H2 at all (nothing to group; the loop below is a no-op)
 *
 * navigation.instant is off in mkdocs.yml, so every page load is a real
 * reload — no SPA re-run to guard against, plain DOMContentLoaded is enough
 * (same assumption readaloud.js already makes).
 */
(function () {
  "use strict";

  function run() {
    var root = document.querySelector("article.md-content__inner.md-typeset");
    if (!root) return;

    var children = Array.prototype.slice.call(root.children);
    var card = null;

    children.forEach(function (node) {
      if (node.tagName === "H2") {
        card = document.createElement("div");
        card.className = "note-card";
        root.insertBefore(card, node);
        card.appendChild(node);
      } else if (card) {
        card.appendChild(node);
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
})();
