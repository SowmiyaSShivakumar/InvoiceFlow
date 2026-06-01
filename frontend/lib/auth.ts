import type { AuthTokens } from "./api";

export const ACCESS_TOKEN_COOKIE = "invoiceflow_access_token";
export const REFRESH_TOKEN_COOKIE = "invoiceflow_refresh_token";

function cookieOptions(maxAgeSeconds: number): string {
  return `Path=/; Max-Age=${maxAgeSeconds}; SameSite=Lax`;
}

export function parseCookieString(cookieString: string, name: string): string | null {
  const parts = cookieString.split(";").map((part) => part.trim());
  const prefix = `${name}=`;
  const match = parts.find((part) => part.startsWith(prefix));
  if (!match) {
    return null;
  }
  return decodeURIComponent(match.slice(prefix.length));
}

export function getCookie(name: string): string | null {
  if (typeof document === "undefined") {
    return null;
  }
  return parseCookieString(document.cookie, name);
}

export function setCookie(name: string, value: string, maxAgeSeconds: number): void {
  if (typeof document === "undefined") {
    return;
  }
  document.cookie = `${name}=${encodeURIComponent(value)}; ${cookieOptions(maxAgeSeconds)}`;
}

export function deleteCookie(name: string): void {
  if (typeof document === "undefined") {
    return;
  }
  document.cookie = `${name}=; Path=/; Max-Age=0; SameSite=Lax`;
}

export function persistAuthTokens(tokens: AuthTokens): void {
  setCookie(ACCESS_TOKEN_COOKIE, tokens.access_token, tokens.expires_in);
  setCookie(REFRESH_TOKEN_COOKIE, tokens.refresh_token, 60 * 60 * 24 * 30);
}

export function clearAuthTokens(): void {
  deleteCookie(ACCESS_TOKEN_COOKIE);
  deleteCookie(REFRESH_TOKEN_COOKIE);
}

export function readAccessToken(): string | null {
  return getCookie(ACCESS_TOKEN_COOKIE);
}

export function readRefreshToken(): string | null {
  return getCookie(REFRESH_TOKEN_COOKIE);
}

