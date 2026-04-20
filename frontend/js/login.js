const API_BASE_URL = "http://127.0.0.1:8000";
// v1.0.1 - Ensuring username is included in payload
console.log("login.js v1.0.1 loaded");

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("loginForm");
    const status = document.getElementById("loginStatus");
    const loginBtn = document.getElementById("loginBtn");
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const roleInput = document.getElementById("role");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        console.log("Form submit triggered");
        
        const username = usernameInput.value.trim();
        const password = passwordInput.value;
        const role = roleInput.value;

        // Force Inclusion of Username Guard
        if (!username) {
            showStatus("Username is required.", "error");
            setLoading(false);
            return;
        }

        console.log("Payload being sent:", {
            username: usernameInput.value,
            password: passwordInput.value,
            role: roleInput.value
        });

        // Basic Validation
        if (!username || !password || !role) {
            showStatus("Please fill in all fields.", "error");
            return;
        }

        if (password.length < 8) {
            showStatus("Password must be at least 8 characters.", "error");
            return;
        }

        // Start Loading State
        setLoading(true);
        showStatus("");

        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    username: usernameInput.value.trim(),
                    password: passwordInput.value,
                    role: roleInput.value
                }),
            });

            const payload = await response.json();
            
            if (!response.ok) {
                let errorMessage = "Login failed.";
                if (payload.detail) {
                    if (Array.isArray(payload.detail)) {
                        // Extract human-readable messages from FastAPI validation errors
                        errorMessage = payload.detail.map(err => {
                            const field = err.loc[err.loc.length - 1];
                            return `${field}: ${err.msg}`;
                        }).join(", ");
                    } else if (typeof payload.detail === 'string') {
                        errorMessage = payload.detail;
                    } else {
                        errorMessage = JSON.stringify(payload.detail);
                    }
                }
                throw new Error(errorMessage);
            }

            showStatus("Login successful! Redirecting...", "success");
            
            // Store token if present, otherwise just save session
            if (payload.access_token) {
                localStorage.setItem("token", payload.access_token);
            }
            
            saveSession(payload);
            
            // Artificial delay for better UX
            setTimeout(() => {
                window.location.href = payload.role === "public" ? "./public/public.html" : "./index.html";
            }, 800);

        } catch (error) {
            console.error("Login Error:", error);
            const displayMsg = error.message && typeof error.message === 'string' 
                ? error.message 
                : JSON.stringify(error);
            showStatus(displayMsg, "error");
            setLoading(false);
        }
    });

    // Fallback Click Handler to ensure submission
    loginBtn.addEventListener("click", (e) => {
        console.log("Login button clicked");
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        // If the form submit event isn't firing automatically
        if (loginBtn.textContent !== "Signing In...") {
            console.log("Manually dispatching submit event");
            form.requestSubmit();
        }
    });

    function showStatus(message, type = "") {
        status.textContent = message;
        status.className = type ? `status-${type}` : "";
    }

    function setLoading(isLoading) {
        if (isLoading) {
            loginBtn.textContent = "Signing In...";
            loginBtn.disabled = true;
        } else {
            loginBtn.textContent = "Login";
            loginBtn.disabled = false;
        }
    }
});
