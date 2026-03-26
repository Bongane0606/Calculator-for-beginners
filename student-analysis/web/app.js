const authPanel = document.getElementById("auth-panel");
const appPanel = document.getElementById("app-panel");
const homeView = document.getElementById("home-view");
const analysisView = document.getElementById("analysis-view");
const authForm = document.getElementById("auth-form");
const analysisForm = document.getElementById("analysis-form");
const loginTab = document.getElementById("login-tab");
const registerTab = document.getElementById("register-tab");
const authSubmit = document.getElementById("auth-submit");
const logoutBtn = document.getElementById("logout-btn");
const userEmail = document.getElementById("user-email");
const openAnalysisBtn = document.getElementById("open-analysis");
const backFromAnalysisBtn = document.getElementById("back-from-analysis");
const resultCard = document.getElementById("result-card");
const errorText = document.getElementById("error-text");
const warningText = document.getElementById("warning-text");
const scoreValue = document.getElementById("score-value");
const completionValue = document.getElementById("completion-value");
const feedbackValue = document.getElementById("feedback-value");

let authMode = "login";

function showError(message) {
  errorText.textContent = message;
  errorText.classList.remove("hidden");
}

function hideError() {
  errorText.textContent = "";
  errorText.classList.add("hidden");
}

function showWarning(message) {
  if (!message) {
    warningText.textContent = "";
    warningText.classList.add("hidden");
    return;
  }

  warningText.textContent = message;
  warningText.classList.remove("hidden");
}

function setAuthMode(mode) {
  authMode = mode;
  const isLogin = mode === "login";
  loginTab.classList.toggle("active", isLogin);
  registerTab.classList.toggle("active", !isLogin);
  authSubmit.textContent = isLogin ? "Log In" : "Create Account";
  hideError();
}

function setActiveView(viewName) {
  homeView.classList.toggle("hidden", viewName !== "home");
  analysisView.classList.toggle("hidden", viewName !== "analysis");

  if (viewName !== "analysis") {
    resultCard.classList.add("hidden");
    showWarning("");
  }

  hideError();
}

function showApp(email) {
  userEmail.textContent = email;
  authPanel.classList.add("hidden");
  appPanel.classList.remove("hidden");
  setActiveView("home");
}

function showAuth() {
  authPanel.classList.remove("hidden");
  appPanel.classList.add("hidden");
  resultCard.classList.add("hidden");
  showWarning("");
  userEmail.textContent = "-";
}

async function sendJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const result = await response.json();
  if (!response.ok) {
    throw new Error(result.error || "Request failed.");
  }

  return result;
}

loginTab.addEventListener("click", () => setAuthMode("login"));
registerTab.addEventListener("click", () => setAuthMode("register"));

openAnalysisBtn.addEventListener("click", () => setActiveView("analysis"));
backFromAnalysisBtn.addEventListener("click", () => setActiveView("home"));

authForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideError();

  const formData = new FormData(authForm);
  const payload = {
    email: String(formData.get("email") || "").trim(),
    password: String(formData.get("password") || ""),
  };

  try {
    const endpoint = authMode === "login" ? "/api/login" : "/api/register";
    const result = await sendJson(endpoint, payload);
    authForm.reset();
    showApp(result.email);
  } catch (error) {
    showError(error.message || "Unable to complete authentication.");
  }
});

logoutBtn.addEventListener("click", async () => {
  hideError();

  try {
    await sendJson("/api/logout", {});
  } catch (error) {
    showError(error.message || "Unable to log out right now.");
    return;
  }

  showAuth();
});

analysisForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideError();

  const formData = new FormData(analysisForm);
  const payload = {
    hours: Number(formData.get("hours")),
    sessions: Number(formData.get("sessions")),
    planned: Number(formData.get("planned")),
    completed: Number(formData.get("completed")),
    difficulty: Number(formData.get("difficulty")),
  };

  if (payload.completed > payload.planned) {
    showError("Completed work cannot be more than planned work.");
    resultCard.classList.add("hidden");
    return;
  }

  try {
    const result = await sendJson("/api/analyze", payload);
    scoreValue.textContent = `${result.score}%`;
    completionValue.textContent = `${result.completionRate}%`;
    feedbackValue.textContent = result.feedback;
    userEmail.textContent = result.email;
    showWarning(result.warning);
    resultCard.classList.remove("hidden");
  } catch (error) {
    resultCard.classList.add("hidden");
    showWarning("");
    showError(error.message || "Unable to analyze study data right now.");
  }
});

async function loadSession() {
  try {
    const response = await fetch("/api/session");
    const result = await response.json();

    if (result.authenticated) {
      showApp(result.email);
      return;
    }
  } catch (error) {
    showError("Unable to check your login session.");
  }

  showAuth();
}

setAuthMode("login");
loadSession();
