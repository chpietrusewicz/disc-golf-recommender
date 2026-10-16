const state = { brands: [], selectedBrands: [] };
const brandList = document.querySelector("#brand-list");
const brandSearch = document.querySelector("#brand-search");
const brandCount = document.querySelector("#brand-count");
const queryInput = document.querySelector("#query");
const recommendButton = document.querySelector("#recommend");
const resultsSection = document.querySelector("#results-section");
const results = document.querySelector("#results");
const message = document.querySelector("#message");
const resultSummary = document.querySelector("#result-summary");

function showMessage(text) {
  message.textContent = text;
  message.hidden = !text;
}

function renderBrands() {
  const search = brandSearch.value.trim().toLowerCase();
  brandList.innerHTML = "";
  state.brands
    .filter((brand) => brand.toLowerCase().includes(search))
    .forEach((brand) => {
      const label = document.createElement("label");
      label.className = "brand-option";
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.checked = state.selectedBrands.includes(brand);
      checkbox.addEventListener("change", () => {
        state.selectedBrands = checkbox.checked
          ? [...state.selectedBrands, brand]
          : state.selectedBrands.filter((selected) => selected !== brand);
        updateBrandCount();
      });
      label.append(checkbox, document.createTextNode(brand));
      brandList.append(label);
    });
}

function updateBrandCount() {
  brandCount.textContent = `${state.selectedBrands.length} brands selected · ${state.brands.length} available`;
}

function value(value) {
  return value === null || value === undefined ? "—" : value;
}

function escapeHTML(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderResults(items, query) {
  results.innerHTML = "";
  resultSummary.textContent = `Showing ${items.length} matches for “${query}”`;
  items.forEach((disc, index) => {
    const card = document.createElement("article");
    card.className = "result-card";
    card.innerHTML = `
      <div class="result-number">0${index + 1}</div>
      <h3>${escapeHTML(disc.name)}</h3>
      <div class="result-meta">${escapeHTML(disc.brand)} · ${escapeHTML(disc.type)}</div>
      <div class="flight">
        <span>Speed ${escapeHTML(value(disc.speed))}</span>
        <span>Glide ${escapeHTML(value(disc.glide))}</span>
        <span>Turn ${escapeHTML(value(disc.turn))}</span>
        <span>Fade ${escapeHTML(value(disc.fade))}</span>
      </div>`;
    results.append(card);
  });
  resultsSection.hidden = false;
}

async function recommend() {
  const query = queryInput.value.trim();
  if (!state.selectedBrands.length) return showMessage("Choose at least one brand first.");
  if (!query) return showMessage("Describe the kind of disc you want first.");

  showMessage("");
  recommendButton.disabled = true;
  recommendButton.querySelector("span").textContent = "…";
  try {
    const response = await fetch("/api/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, brands: state.selectedBrands }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "Recommendation failed.");
    if (!payload.results.length) {
      resultsSection.hidden = true;
      return showMessage("No discs matched that request inside your selected brands.");
    }
    renderResults(payload.results, query);
  } catch (error) {
    showMessage(error.message);
  } finally {
    recommendButton.disabled = false;
    recommendButton.querySelector("span").textContent = "→";
  }
}

document.querySelectorAll("[data-example]").forEach((button) => {
  button.addEventListener("click", () => {
    queryInput.value = button.dataset.example;
    queryInput.focus();
  });
});
brandSearch.addEventListener("input", renderBrands);
document.querySelector("#select-all").addEventListener("click", () => {
  state.selectedBrands = [...state.brands];
  renderBrands();
  updateBrandCount();
});
recommendButton.addEventListener("click", recommend);
queryInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    recommend();
  }
});

fetch("/api/config")
  .then((response) => response.json())
  .then((config) => {
    state.brands = config.brands;
    state.selectedBrands = config.defaultBrands.filter((brand) => state.brands.includes(brand));
    renderBrands();
    updateBrandCount();
  })
  .catch(() => showMessage("Could not load the brand list. Is the Python server running?"));
