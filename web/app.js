const form = document.querySelector("#question-form");
const questionInput = document.querySelector("#question");
const characterCount = document.querySelector("#character-count");
const runButton = document.querySelector("#run-button");
const resultPanel = document.querySelector(".result-panel");
const resultContent = document.querySelector("#result-content");
const loadingState = document.querySelector("#loading-state");
const errorState = document.querySelector("#error-state");
const answerNode = document.querySelector("#answer");
const evidenceList = document.querySelector("#evidence-list");
const evidenceSummary = document.querySelector("#evidence-summary");
const resultStatus = document.querySelector("#result-status");
const copyButton = document.querySelector("#copy-button");
let currentResult = {
  question: "Where did you go to college?",
  answer: "I studied at University of Washington, and The University of Texas at Austin.",
  evidence: ["University of Washington", "The University of Texas at Austin"],
};

function setLoading(isLoading) {
  resultPanel.setAttribute("aria-busy", String(isLoading));
  runButton.disabled = isLoading;
  runButton.querySelector(".button-label").textContent = isLoading ? "Running…" : "Run baseline";
  loadingState.hidden = !isLoading;
  resultContent.hidden = isLoading;
  errorState.hidden = true;
}

function renderResult(result) {
  currentResult = result;
  answerNode.textContent = result.answer;
  const evidence = Array.isArray(result.evidence) ? result.evidence : [];
  const count = evidence.length;
  evidenceSummary.textContent = count === 1 ? "1 profile line matched" : `${count} profile lines matched`;
  evidenceList.replaceChildren();

  if (count === 0) {
    const item = document.createElement("li");
    item.className = "empty-evidence";
    item.textContent = "No supporting profile line was found. The system abstained instead of guessing.";
    evidenceList.append(item);
    resultStatus.className = "result-status abstained";
    resultStatus.innerHTML = '<span aria-hidden="true">—</span> Abstained safely';
  } else {
    evidence.forEach((line, index) => {
      const item = document.createElement("li");
      const number = document.createElement("span");
      number.className = "evidence-index";
      number.textContent = String(index + 1).padStart(2, "0");
      const text = document.createElement("span");
      text.textContent = line;
      item.append(number, text);
      evidenceList.append(item);
    });
    resultStatus.className = "result-status success";
    resultStatus.innerHTML = '<span aria-hidden="true">✓</span> Evidence found';
  }
  resultContent.hidden = false;
}

async function runQuestion(question) {
  setLoading(true);
  try {
    const response = await fetch("/api/answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "The baseline could not run.");
    renderResult(payload);
  } catch (error) {
    resultContent.hidden = true;
    errorState.textContent = error.message;
    errorState.hidden = false;
  } finally {
    loadingState.hidden = true;
    resultPanel.setAttribute("aria-busy", "false");
    runButton.disabled = false;
    runButton.querySelector(".button-label").textContent = "Run baseline";
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  runQuestion(questionInput.value.trim());
});

questionInput.addEventListener("input", () => {
  characterCount.textContent = questionInput.value.length;
});

questionInput.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
    event.preventDefault();
    form.requestSubmit();
  }
});

document.querySelectorAll(".example-chip").forEach((button) => {
  button.addEventListener("click", () => {
    questionInput.value = button.dataset.question;
    characterCount.textContent = questionInput.value.length;
    questionInput.focus();
  });
});

copyButton.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(JSON.stringify(currentResult, null, 2));
    copyButton.textContent = "Copied";
    window.setTimeout(() => { copyButton.textContent = "Copy JSON"; }, 1400);
  } catch {
    copyButton.textContent = "Copy unavailable";
  }
});
