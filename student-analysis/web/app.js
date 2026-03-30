const authPanel = document.getElementById("auth-panel");
const appPanel = document.getElementById("app-panel");
const introPanel = document.getElementById("intro-panel");
const pageShell = document.getElementById("page-shell");
const homeView = document.getElementById("home-view");
const analysisView = document.getElementById("analysis-view");
const calculatorView = document.getElementById("calculator-view");
const authForm = document.getElementById("auth-form");
const analysisForm = document.getElementById("analysis-form");
const loginTab = document.getElementById("login-tab");
const registerTab = document.getElementById("register-tab");
const authSubmit = document.getElementById("auth-submit");
const logoutBtn = document.getElementById("logout-btn");
const userEmail = document.getElementById("user-email");
const openAnalysisBtn = document.getElementById("open-analysis");
const openCalculatorBtn = document.getElementById("open-calculator");
const backFromAnalysisBtn = document.getElementById("back-from-analysis");
const backFromCalculatorBtn = document.getElementById("back-from-calculator");
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
  calculatorView.classList.toggle("hidden", viewName !== "calculator");

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
  introPanel.classList.add("hidden");
  pageShell.classList.add("app-active");
  setActiveView("home");
}

function showAuth() {
  authPanel.classList.remove("hidden");
  appPanel.classList.add("hidden");
  resultCard.classList.add("hidden");
  introPanel.classList.remove("hidden");
  pageShell.classList.remove("app-active");
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
openCalculatorBtn.addEventListener("click", () => setActiveView("calculator"));
backFromAnalysisBtn.addEventListener("click", () => setActiveView("home"));
backFromCalculatorBtn.addEventListener("click", () => setActiveView("home"));

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

// --- Calculator Logic ---
const calcDisplay = document.getElementById("calc-display");
const calcBtns = document.querySelectorAll(".calc-btn");

let calcA = null;
let calcOperator = null;
let calcResetNext = false;

calcBtns.forEach(btn => {
  btn.addEventListener("click", () => {
    const val = btn.getAttribute("data-val");
    const current = calcDisplay.textContent;

    if (val === "C") {
      calcA = null;
      calcOperator = null;
      calcDisplay.textContent = "0";
      return;
    }

    if (val === "=") {
      if (calcA === null || calcOperator === null) return;
      
      const numA = parseFloat(calcA);
      const numB = parseFloat(current);
      let res = 0;
      
      if (calcOperator === "+") res = numA + numB;
      else if (calcOperator === "-") res = numA - numB;
      else if (calcOperator === "*") res = numA * numB;
      else if (calcOperator === "/") {
        if (numB === 0) {
          calcDisplay.textContent = "Error";
          calcA = null;
          calcOperator = null;
          calcResetNext = true;
          return;
        }
        res = numA / numB;
      }
      
      if (res % 1 !== 0) {
        res = parseFloat(res.toFixed(6));
      }
      
      calcDisplay.textContent = res;
      calcA = null;
      calcOperator = null;
      calcResetNext = true;
      return;
    }

    if (["+", "-", "*", "/"].includes(val)) {
      calcA = current;
      calcOperator = val;
      calcResetNext = true;
      return;
    }

    if (calcResetNext) {
      calcDisplay.textContent = val === "." ? "0." : val;
      calcResetNext = false;
      return;
    }

    if (val === ".") {
      if (!current.includes(".")) {
        calcDisplay.textContent = current + ".";
      }
      return;
    }

    if (current === "0" || current === "Error") {
      calcDisplay.textContent = val;
    } else {
      calcDisplay.textContent = current + val;
    }
  });
});

// --- Theme Toggle Logic ---
const themeToggle = document.getElementById("theme-toggle");

function updateThemeIcon() {
  const isDark = document.documentElement.getAttribute("data-theme") === "dark" || 
                (!document.documentElement.hasAttribute("data-theme") && window.matchMedia("(prefers-color-scheme: dark)").matches);
  themeToggle.textContent = isDark ? "☀️" : "🌙";
  themeToggle.setAttribute("title", isDark ? "Switch to Light Mode" : "Switch to Dark Mode");
}

function initTheme() {
  const storedTheme = localStorage.getItem("theme");
  if (storedTheme) {
    document.documentElement.setAttribute("data-theme", storedTheme);
  } else {
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    if (prefersDark) {
      document.documentElement.setAttribute("data-theme", "dark");
    }
  }
  updateThemeIcon();
}

themeToggle.addEventListener("click", () => {
  let isDark = document.documentElement.getAttribute("data-theme") === "dark";
  
  if (!document.documentElement.hasAttribute("data-theme")) {
    isDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  }
  
  const newTheme = isDark ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", newTheme);
  localStorage.setItem("theme", newTheme);
  updateThemeIcon();
});

initTheme();
