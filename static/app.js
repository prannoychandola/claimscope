const input = document.querySelector("#claim-input");
const searchButton = document.querySelector("#search-button");
const errorMessage = document.querySelector("#error-message");
const resultsSection = document.querySelector("#results-section");
const resultsList = document.querySelector("#results-list");
const resultCount = document.querySelector("#result-count");

document.querySelectorAll("[data-sample]").forEach((button) => {
  button.addEventListener("click", () => {
    input.value = button.dataset.sample;
    input.focus();
  });
});

function makeVerdictControl() {
  const wrap = document.createElement("div");
  wrap.className = "review-control";
  const label = document.createElement("span");
  label.className = "review-label";
  label.textContent = "YOUR REVIEW";
  const choices = document.createElement("div");
  choices.className = "verdict-choices";
  [
    ["Supports", "supports"],
    ["Contradicts", "contradicts"],
    ["Partial", "partial"],
    ["Insufficient", "insufficient"],
  ].forEach(([text, value]) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "verdict-button";
    button.textContent = text;
    button.setAttribute("aria-pressed", "false");
    button.addEventListener("click", () => {
      choices.querySelectorAll("button").forEach((choice) => {
        choice.setAttribute("aria-pressed", "false");
      });
      button.setAttribute("aria-pressed", "true");
      label.textContent = "YOUR REVIEW · " + value.toUpperCase();
    });
    choices.append(button);
  });
  wrap.append(label, choices);
  return wrap;
}

function renderCandidate(item, index, maxScore) {
  const card = document.createElement("article");
  card.className = "evidence-card";

  const top = document.createElement("div");
  top.className = "card-top";
  const source = document.createElement("div");
  source.className = "source-line";
  const id = document.createElement("span");
  id.className = "doc-id";
  id.textContent = item.id;
  const section = document.createElement("span");
  section.className = "section-tag";
  section.textContent = item.section;
  source.append(id, section);

  const score = document.createElement("div");
  score.className = "score-wrap";
  const scoreText = document.createElement("span");
  scoreText.className = "score-text";
  scoreText.textContent = "BM25 " + item.retrieval_score.toFixed(2);
  const bar = document.createElement("span");
  bar.className = "score-track";
  const fill = document.createElement("span");
  fill.className = "score-fill";
  fill.style.width = (maxScore > 0 ? Math.max(3, (item.retrieval_score / maxScore) * 100) : 0) + "%";
  bar.append(fill);
  score.append(scoreText, bar);
  top.append(source, score);

  const title = document.createElement("h3");
  title.textContent = item.title;
  const excerpt = document.createElement("blockquote");
  excerpt.textContent = item.text;
  const meta = document.createElement("p");
  meta.className = "candidate-meta";
  meta.textContent = "Fictional demo passage · query term coverage " + (item.query_term_coverage * 100).toFixed(0) + "%";

  const review = makeVerdictControl();
  card.style.animationDelay = (index * 55) + "ms";
  card.append(top, title, excerpt, meta, review);
  return card;
}

async function search() {
  const claim = input.value.trim();
  errorMessage.hidden = true;
  if (!claim) {
    errorMessage.textContent = "Add a claim first.";
    errorMessage.hidden = false;
    input.focus();
    return;
  }
  searchButton.disabled = true;
  searchButton.querySelector("span:first-child").textContent = "Searching…";
  resultsSection.hidden = true;
  try {
    const response = await fetch("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ claim, top_k: 5 }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Search failed.");
    resultsList.replaceChildren();
    const candidates = data.candidates || [];
    resultCount.textContent = candidates.length + " passages";
    if (candidates.length === 0 || candidates.every((candidate) => candidate.retrieval_score === 0)) {
      const empty = document.createElement("div");
      empty.className = "empty-state";
      empty.textContent = "No useful lexical match found in the tiny demo corpus. That does not establish that no evidence exists.";
      resultsList.append(empty);
    } else {
      const maxScore = Math.max(...candidates.map((candidate) => candidate.retrieval_score));
      candidates.forEach((candidate, index) => {
        resultsList.append(renderCandidate(candidate, index, maxScore));
      });
    }
    resultsSection.hidden = false;
    resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    errorMessage.textContent = error.message || "Could not connect to the local demo.";
    errorMessage.hidden = false;
  } finally {
    searchButton.disabled = false;
    searchButton.querySelector("span:first-child").textContent = "Find evidence";
  }
}

searchButton.addEventListener("click", search);
input.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") search();
});
