const API_BASE_URL = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {
    const roleCards = document.querySelectorAll("[data-role]");
    const roleInput = document.getElementById("role");
    const passwordInput = document.getElementById("password");
    const form = document.getElementById("loginForm");
    const status = document.getElementById("loginStatus");

    roleCards.forEach((card) => {
        card.addEventListener("click", () => {
            roleCards.forEach((item) => item.classList.remove("active"));
            card.classList.add("active");
            roleInput.value = card.dataset.role;
            passwordInput.value = `${card.dataset.role}123`;
        });
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        status.textContent = "Signing in...";

        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    role: roleInput.value,
                    password: passwordInput.value,
                }),
            });

            const payload = await response.json();
            if (!response.ok) {
                throw new Error(payload.detail || "Login failed.");
            }

            saveSession(payload);
            window.location.href = payload.role === "public" ? "./public/public.html" : "./index.html";
        } catch (error) {
            status.textContent = error.message;
        }
    });
});
