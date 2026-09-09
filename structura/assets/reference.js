"use strict";
(() => {
  const form = document.querySelector("form.search");
  const input = document.querySelector("#site-query");
  const results = document.querySelector("#search-results");
  const status = document.querySelector("#search-status");
  if (!form || !input || !results || !status) return;
  const records = window.structuraSearch || [];
  const prefix = document.body.dataset.root || "";
  const normalize = value => value.toLowerCase().normalize("NFKD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, " ").trim();
  function render(query) {
    results.replaceChildren();
    const words = normalize(query).split(/\s+/).filter(Boolean);
    document.querySelector("#search-fallback").hidden = words.length > 0;
    if (!words.length) {
      status.textContent = "Browse all entries below, or search by name, model, company, year or standard.";
      return;
    }
    const hits = records.filter(record => words.every(word => normalize(record.terms).includes(word)));
    status.textContent = hits.length ? `${hits.length} result${hits.length === 1 ? "" : "s"} for “${query}”` : `No results for “${query}”. Try a shorter model name, a manufacturer or a year.`;
    const list = document.createElement("ul"); list.className = "records";
    for (const hit of hits) {
      const li = document.createElement("li"), link = document.createElement("a"), title = document.createElement("strong"), description = document.createElement("span");
      link.className = "record-link"; link.href = prefix + hit.url;
      title.textContent = hit.title; description.textContent = hit.description;
      link.append(title, description); li.append(link); list.append(li);
    }
    results.append(list);
  }
  const query = new URLSearchParams(location.search).get("q") || "";
  input.value = query; render(query);
  form.addEventListener("submit", event => {
    event.preventDefault(); const q = input.value.trim();
    history.replaceState(null, "", location.pathname + (q ? "?q=" + encodeURIComponent(q) : ""));
    render(q);
  });
  input.addEventListener("input", () => render(input.value.trim()));
})();
