"use client";

import { Component, type ReactNode } from "react";
import { logger } from "@/lib/logger";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: { componentStack: string }) {
    logger.error("Error caught by ErrorBoundary", {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center p-4">
          <div className="text-center">
            <h1 className="mb-2 text-2xl font-bold text-red-600 dark:text-red-400">
              Something went wrong
            </h1>
            <p className="mb-4 text-gray-600 dark:text-gray-400">
              An unexpected error occurred
            </p>
            {process.env.NODE_ENV === "development" && this.state.error && (
              <details className="rounded bg-gray-100 p-4 text-left text-sm dark:bg-gray-800">
                <summary className="mb-2 cursor-pointer font-semibold">
                  Error details
                </summary>
                <pre className="whitespace-pre-wrap">{this.state.error.stack}</pre>
              </details>
            )}
            <button
              onClick={() => window.location.reload()}
              className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 dark:hover:bg-blue-700"
            >
              Refresh
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
