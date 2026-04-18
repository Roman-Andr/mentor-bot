"use client";

import { createContext, useEffect, useState, type ReactNode } from "react";

interface AuthUser {
  id: number;
  email: string;
  role: string;
  first_name: string;
  last_name: string | null;
}

interface AuthContextType {
  user: AuthUser | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  // User state is derived from httpOnly cookie validation, NOT localStorage
  // This prevents XSS attacks from stealing user data
  const [user, setUser] = useState<AuthUser | null>(null);

  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const validateSession = async () => {
      try {
        const response = await fetch("/api/v1/auth/me", {
          credentials: "include",  // Send httpOnly cookies
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
          setIsAuthenticated(true);
        } else if (response.status === 401) {
          setUser(null);
          setIsAuthenticated(false);
        }
      } catch {
        // Network errors don't clear user state - auth state is server-side
      }
      setIsLoading(false);
    };
    validateSession();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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
        credentials: "include",  // Receive httpOnly cookies
        body: formData.toString(),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error("Login failed:", response.status, errorData);
        return false;
      }

      const data = await response.json();

      const userResponse = await fetch("/api/v1/auth/me", {
        credentials: "include",  // Send httpOnly cookies
      });

      if (!userResponse.ok) {
        console.error("Failed to fetch user:", userResponse.status);
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
      setIsAuthenticated(true);
      // User data is NOT stored in localStorage (XSS prevention)
      // Auth tokens are in httpOnly cookies, user data is fetched from server

      return true;
    } catch (error) {
      console.error("Login error:", error);
      return false;
    }
  };

  const logout = async () => {
    // Call logout endpoint to clear httpOnly cookies
    try {
      await fetch("/api/v1/auth/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch {
      // ignore errors
    }
    setUser(null);
    setIsAuthenticated(false);
    // No localStorage to clear - auth is entirely cookie-based
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export { AuthContext };
