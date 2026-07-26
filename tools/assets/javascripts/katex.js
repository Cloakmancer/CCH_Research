// Render LaTeX math with KaTeX. Works with MkDocs Material's instant navigation,
// which swaps page content without a full reload.
document$.subscribe(({ body }) => {
  renderMathInElement(body, {
    delimiters: [
      { left: "$$", right: "$$", display: true },
      { left: "$", right: "$", display: false },
      { left: "\\(", right: "\\)", display: false },
      { left: "\\[", right: "\\]", display: true }
    ],
    // Don't blow up the whole page on one malformed expression.
    throwOnError: false,
    ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"]
  });
});
