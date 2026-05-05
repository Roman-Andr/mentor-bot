/**
 * Query builder utility to reduce duplication in API modules
 */

export function buildQueryString(params?: Record<string, unknown>): string {
  if (!params) return "";

  const searchParams = new URLSearchParams();

  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null) {
      searchParams.set(key, String(value));
    }
  }

  return searchParams.toString();
}
