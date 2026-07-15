export const AUTH_TOKEN_KEY = "token";

type JwtPayload = {
  exp?: number;
};

export function getStoredToken() {
  const token = localStorage.getItem(AUTH_TOKEN_KEY);
  if (!token) {
    return null;
  }

  if (isTokenExpired(token)) {
    clearStoredToken();
    return null;
  }

  return token;
}

export function storeToken(token: string) {
  localStorage.setItem(AUTH_TOKEN_KEY, token);
}

export function clearStoredToken() {
  localStorage.removeItem(AUTH_TOKEN_KEY);
}

export function isAuth() {
  return Boolean(getStoredToken());
}

export function isTokenExpired(token: string) {
  try {
    const encodedPayload = token.split(".")[1];
    if (!encodedPayload) {
      return true;
    }

    const normalizedPayload = encodedPayload
      .replace(/-/g, "+")
      .replace(/_/g, "/");
    const padding = "=".repeat((4 - (normalizedPayload.length % 4)) % 4);
    const payload = JSON.parse(
      window.atob(`${normalizedPayload}${padding}`),
    ) as JwtPayload;

    return typeof payload.exp !== "number" || payload.exp * 1000 <= Date.now();
  } catch {
    return true;
  }
}
