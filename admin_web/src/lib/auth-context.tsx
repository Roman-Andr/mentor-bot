"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { setAuthToken } from "./api";
import { TOKEN_KEY, USER_KEY } from "./storage-keys";

interface AuthUser {
  id: number;
  email: string;
  role: string;
  first_name: string;
  last_name: string | null;
}

interface AuthContextType {
  user: AuthUser | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => {
    if (typeof window === "undefined") return null;
    try {
      const storedUser = localStorage.getItem(USER_KEY);
      const storedToken = localStorage.getItem(TOKEN_KEY);
      if (storedToken && storedUser) {
        setAuthToken(storedToken);
        return JSON.parse(storedUser);
      }
    } catch {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    }
    return null;
  });

  const [token, setToken] = useState<string | null>(() => {
    if (typeof window === "undefined") return null;
    try {
      return localStorage.getItem(TOKEN_KEY);
    } catch {
      return null;
    }
  });

  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const validateToken = async () => {
      if (!token) {
        setIsLoading(false);
        return;
      }
      try {
        const response = await fetch("/api/v1/auth/me", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (response.ok) {
          const userData = await response.json();
          const validatedUser: AuthUser = {
            id: userData.id,
            email: userData.email,
            role: userData.role,
            first_name: userData.first_name,
            last_name: userData.last_name,
          };
          setUser(validatedUser);
          localStorage.setItem(USER_KEY, JSON.stringify(validatedUser));
        } else if (response.status === 401) {
          setUser(null);
          setToken(null);
          setAuthToken(null);
          localStorage.removeItem(TOKEN_KEY);
          localStorage.removeItem(USER_KEY);
        }
      } catch {
        // keep stored session on network errors
      }
      setIsLoading(false);
    };
    validateToken();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (token) {
      setAuthToken(token);
    } else {
      setAuthToken(null);
    }
  }, [token]);

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const response = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData.toString(),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error("Login failed:", response.status, errorData);
        return false;
      }

      const data = await response.json();
      const accessToken: string = data.access_token;

      if (!accessToken) {
        console.error("Login response missing access_token");
        return false;
      }

      localStorage.setItem(TOKEN_KEY, accessToken);
      setAuthToken(accessToken);
      setToken(accessToken);

      const userResponse = await fetch("/api/v1/auth/me", {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      if (!userResponse.ok) {
        console.error("Failed to fetch user:", userResponse.status);
        localStorage.removeItem(TOKEN_KEY);
        setAuthToken(null);
        setToken(null);
        return false;
      }

      const userData = await userResponse.json();
      const user: AuthUser = {
        id: userData.id,
        email: userData.email,
        role: userData.role,
        first_name: userData.first_name,
        last_name: userData.last_name,
      };

      setUser(user);
      localStorage.setItem(USER_KEY, JSON.stringify(user));

      return true;
    } catch (error) {
      console.error("Login error:", error);
      return false;
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    setAuthToken(null);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
