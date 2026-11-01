// Run in the client's page (browser devtools or a browser tool's JS exec). Returns the brand tokens as JSON.
(() => {
  const cs = (el) => getComputedStyle(el);
  const vars = {}, faces = [], links = [];
  for (const sheet of document.styleSheets) {
    try {
      for (const r of sheet.cssRules) {
        if (r.selectorText && /(^|,)\s*:root/.test(r.selectorText)) for (const p of r.style) if (p.startsWith("--")) vars[p] = r.style.getPropertyValue(p).trim();
        if (r.constructor.name === "CSSFontFaceRule") faces.push(r.cssText.slice(0, 260));
      }
    } catch (e) { if (sheet.href) links.push(sheet.href); }
  }
  const fonts = new Set(), bgs = {}, colors = {}, grads = new Set();
  document.querySelectorAll("body *").forEach((el) => {
    const s = cs(el);
    fonts.add(s.fontFamily.split(",")[0].trim());
    if (s.backgroundImage.includes("gradient")) grads.add(s.backgroundImage.slice(0, 240));
    if (s.backgroundColor !== "rgba(0, 0, 0, 0)") bgs[s.backgroundColor] = (bgs[s.backgroundColor] || 0) + 1;
    colors[s.color] = (colors[s.color] || 0) + 1;
  });
  const top = (o, n) => Object.entries(o).sort((a, b) => b[1] - a[1]).slice(0, n);
  const h1 = document.querySelector("h1"), h = h1 && cs(h1);
  const clipped = [...document.querySelectorAll("h1 *, h2 *")].filter((e) => cs(e).backgroundImage !== "none" && /text/.test(cs(e).webkitBackgroundClip || cs(e).backgroundClip))
    .map((e) => ({ text: e.textContent.trim().slice(0, 40), gradient: cs(e).backgroundImage }));
  return {
    url: location.href,
    title: document.title,
    rootVars: vars,
    bodyBackground: cs(document.body).backgroundColor,
    backgrounds: top(bgs, 15),
    textColors: top(colors, 12),
    gradients: [...grads].slice(0, 20),
    gradientText: clipped,
    fonts: [...fonts],
    fontFaces: faces.slice(0, 12),
    fontLinks: [...document.querySelectorAll('link[href*="font"]')].map((l) => l.href).concat(links).slice(0, 10),
    h1: h && { font: h.fontFamily, size: h.fontSize, weight: h.fontWeight, tracking: h.letterSpacing, color: h.color },
    logo: [...document.querySelectorAll('img[src*="logo" i], svg[class*="logo" i], a[class*="logo" i] img')].map((e) => e.currentSrc || e.src || "inline-svg").slice(0, 5),
    images: [...document.images].map((i) => i.currentSrc || i.src).filter((s) => s && !s.startsWith("data:")).slice(0, 40),
  };
})();
