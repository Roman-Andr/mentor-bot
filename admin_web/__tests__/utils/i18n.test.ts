import { describe, it, expect } from "vitest";
import en from "../../messages/en.json";
import ru from "../../messages/ru.json";

type LocaleObject = { [key: string]: string | LocaleObject };

function flattenKeys(obj: LocaleObject, prefix = ""): string[] {
  const keys: string[] = [];
  for (const [k, v] of Object.entries(obj)) {
    const full = prefix ? `${prefix}.${k}` : k;
    if (typeof v === "object" && v !== null) {
      keys.push(...flattenKeys(v as LocaleObject, full));
    } else {
      keys.push(full);
    }
  }
  return keys;
}

const enKeys = new Set(flattenKeys(en as LocaleObject));
const ruKeys = new Set(flattenKeys(ru as LocaleObject));

describe("i18n locale completeness", () => {
  it("en.json and ru.json have the same number of keys", () => {
    expect(enKeys.size).toBe(ruKeys.size);
  });

  it("all en.json keys exist in ru.json", () => {
    const missingInRu = [...enKeys].filter((k) => !ruKeys.has(k));
    expect(missingInRu).toEqual([]);
  });

  it("all ru.json keys exist in en.json", () => {
    const missingInEn = [...ruKeys].filter((k) => !enKeys.has(k));
    expect(missingInEn).toEqual([]);
  });

  it("no keys have empty string values in en.json", () => {
    const emptyKeys: string[] = [];
    function checkEmpty(obj: LocaleObject, prefix = "") {
      for (const [k, v] of Object.entries(obj)) {
        const full = prefix ? `${prefix}.${k}` : k;
        if (typeof v === "object") {
          checkEmpty(v as LocaleObject, full);
        } else if (v === "") {
          emptyKeys.push(full);
        }
      }
    }
    checkEmpty(en as LocaleObject);
    expect(emptyKeys).toEqual([]);
  });

  it("no keys have empty string values in ru.json", () => {
    const emptyKeys: string[] = [];
    function checkEmpty(obj: LocaleObject, prefix = "") {
      for (const [k, v] of Object.entries(obj)) {
        const full = prefix ? `${prefix}.${k}` : k;
        if (typeof v === "object") {
          checkEmpty(v as LocaleObject, full);
        } else if (v === "") {
          emptyKeys.push(full);
        }
      }
    }
    checkEmpty(ru as LocaleObject);
    expect(emptyKeys).toEqual([]);
  });

  it("all values are strings (no nested arrays)", () => {
    function checkTypes(obj: LocaleObject, prefix = "") {
      for (const [k, v] of Object.entries(obj)) {
        const full = prefix ? `${prefix}.${k}` : k;
        if (Array.isArray(v)) {
          throw new Error(`Key "${full}" has array value, expected string or object`);
        }
        if (typeof v === "object" && v !== null) {
          checkTypes(v as LocaleObject, full);
        } else {
          expect(typeof v, `Key "${full}"`).toBe("string");
        }
      }
    }
    expect(() => checkTypes(en as LocaleObject)).not.toThrow();
    expect(() => checkTypes(ru as LocaleObject)).not.toThrow();
  });

  it("both locales have required top-level namespaces", () => {
    const requiredNamespaces = [
      "common",
      "analytics",
      "auth",
      "checklists",
      "dashboard",
      "departments",
      "dialogues",
      "escalations",
      "feedback",
      "invitations",
      "knowledge",
      "meetings",
      "nav",
      "notificationTemplates",
      "pagination",
      "settings",
      "statuses",
      "templates",
      "users",
    ];
    for (const ns of requiredNamespaces) {
      expect(en, `en.json missing namespace: ${ns}`).toHaveProperty(ns);
      expect(ru, `ru.json missing namespace: ${ns}`).toHaveProperty(ns);
    }
  });
});
