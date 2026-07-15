import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { api } from "../api/client";
import { clearStoredToken, getStoredToken, storeToken } from "../utils/auth";

type AuthContextType = {
  token: string | null;
  isAuthenticated: boolean;
  isCheckingSession: boolean;
  login: (token: string) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => getStoredToken());
  const [isCheckingSession, setIsCheckingSession] = useState(() =>
    Boolean(getStoredToken()),
  );

  useEffect(() => {
    const storedToken = getStoredToken();
    if (!storedToken) {
      setToken(null);
      setIsCheckingSession(false);
      return;
    }

    let active = true;

    api
      .get("/auth/me")
      .then(() => {
        if (active) {
          setIsCheckingSession(false);
        }
      })
      .catch(() => {
        if (active) {
          clearStoredToken();
          setToken(null);
          setIsCheckingSession(false);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  const value = useMemo<AuthContextType>(
    () => ({
      token,
      isAuthenticated: Boolean(token),
      isCheckingSession,
      login: (newToken: string) => {
        storeToken(newToken);
        setToken(newToken);
      },
      logout: () => {
        clearStoredToken();
        setToken(null);
      },
    }),
    [isCheckingSession, token],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
