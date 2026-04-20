const FIABS_SESSION_KEY = "fiabs.session";

function getSession() {
    try {
        return JSON.parse(localStorage.getItem(FIABS_SESSION_KEY) || "null");
    } catch (error) {
        return null;
    }
}

function saveSession(session) {
    localStorage.setItem(FIABS_SESSION_KEY, JSON.stringify(session));
}

function clearSession() {
    localStorage.removeItem(FIABS_SESSION_KEY);
}

function requireRole(allowedRoles, loginPath) {
    const session = getSession();
    if (!session || !allowedRoles.includes(session.role)) {
        window.location.href = loginPath;
        return null;
    }
    return session;
}

function logout(loginPath) {
    clearSession();
    window.location.href = loginPath;
}
