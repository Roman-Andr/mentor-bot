"use client";

import { createContext, useEffect, useState, type ReactNode } from "react";
import { setUnauthorizedCallback } from "./api/client";
import { useRouter } from "next/navigation";
import { logger } from "./logger";
import { handleError } from "./error";

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

  const [isLoading, setIsLoading] = useState(true);

  const router = useRouter();

  useEffect(() => {
    setUnauthorizedCallback(() => {
      setUser(null);
      router.push("/login");
    });
  }, [router]);

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
        } else if (response.status === 401) {
          setUser(null);
        }
      } catch {
        // Network errors don't clear user state - auth state is server-side
      }
      setIsLoading(false);
    };
    validateSession();

  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      logger.debug("Sending login request");
      const response = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        credentials: "include",
        body: formData.toString(),
      });

      logger.debug("Login response status", { status: response.status, setCookie: response.headers.get("Set-Cookie") || "none" });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        logger.error("Login failed", { status: response.status, errorData });
        return false;
      }

      const data = await response.json();
      logger.debug("Login success", { hasToken: !!data.access_token });

      logger.debug("Fetching /me with cookies");
      const userResponse = await fetch("/api/v1/auth/me", {
        credentials: "include",
      });

      logger.debug("/me response status", { status: userResponse.status });

      if (!userResponse.ok) {
        logger.error("Failed to fetch user", { status: userResponse.status });
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
      // User data is NOT stored in localStorage (XSS prevention)
      // Auth tokens are in httpOnly cookies, user data is fetched from server

      return true;
    } catch (error) {
      const appError = handleError(error, { action: "login" });
      logger.error("Login error", { error: appError });
      return false;
    }
  };

  const refresh = async () => {
    try {
      logger.debug("Fetching /me with cookies");
      const userResponse = await fetch("/api/v1/auth/me", {
        credentials: "include",
      });

      logger.debug("/me response status", { status: userResponse.status });

      if (!userResponse.ok) {
        logger.error("Failed to fetch user", { status: userResponse.status });
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
      return true;
    } catch (error) {
      logger.error("Failed to refresh user data", { error });
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
    // No localStorage to clear - auth is entirely cookie-based
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export { AuthContext };
