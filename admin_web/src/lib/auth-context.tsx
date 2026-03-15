"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import { api, setAuthToken } from "./api";

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

const TOKEN_KEY = "admin_token";
const USER_KEY = "admin_user";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem(TOKEN_KEY);
    const storedUser = localStorage.getItem(USER_KEY);
    if (storedToken && storedUser) {
      setAuthToken(storedToken);
      setToken(storedToken);
      try {
        setUser(JSON.parse(storedUser));
      } catch {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
        setAuthToken(null);
      }
    }
    setIsLoading(false);
  }, []);

  useEffect(() => {
    if (token) {
      setAuthToken(token);
    } else {
      setAuthToken(null);
    }
  }, [token]);

  const login = async (email: string, password: string): Promise<boolean> => {
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_AUTH_SERVICE_URL || "http://localhost:8001"}/api/v1/auth/login`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: formData,
        }
      );

      if (!response.ok) {
        return false;
      }

      const data = await response.json();
      setToken(data.access_token);

      const userResponse = await fetch(
        `${process.env.NEXT_PUBLIC_AUTH_SERVICE_URL || "http://localhost:8001"}/api/v1/auth/me`,
        {
          headers: {
            Authorization: `Bearer ${data.access_token}`,
          },
        }
      );

      if (userResponse.ok) {
        const userData = await userResponse.json();
        const user: AuthUser = {
          id: userData.id,
          email: userData.email,
          role: userData.role,
          first_name: userData.first_name,
          last_name: userData.last_name,
        };
        setUser(user);
        setAuthToken(data.access_token);
        localStorage.setItem(TOKEN_KEY, data.access_token);
        localStorage.setItem(USER_KEY, JSON.stringify(user));
      }

      return true;
    } catch {
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