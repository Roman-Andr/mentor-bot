import path from "path";
import { fileURLToPath } from "url";
import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";
import tailwindcss from "eslint-plugin-tailwindcss";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const shadcnClassNames = [
  "bg-background",
  "bg-foreground",
  "bg-primary",
  "bg-secondary",
  "bg-destructive",
  "bg-muted",
  "bg-accent",
  "bg-popover",
  "bg-card",
  "bg-input",
  "bg-ring",
  "bg-border",
  "text-primary",
  "text-primary-foreground",
  "text-secondary",
  "text-secondary-foreground",
  "text-destructive",
  "text-destructive-foreground",
  "text-muted",
  "text-muted-foreground",
  "text-accent",
  "text-accent-foreground",
  "text-popover-foreground",
  "text-card-foreground",
  "border-input",
  "border-ring",
  "border-border",
  "ring-ring",
  "ring-offset-background",
  "toggle",
];

const shadcnPattern = shadcnClassNames.map(
  (c) => `^([\\w-]+:)*${c.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}(/\\d+)?$`,
);

const eslintConfig = defineConfig([
  // Next.js base configurations
  ...nextVitals,
  ...nextTs,

  // Tailwind CSS plugin with recommended rules
  ...tailwindcss.configs["flat/recommended"],

  // Global ignore patterns
  globalIgnores([".next/**", "out/**", "build/**", "next-env.d.ts"]),

  // Whitelist shadcn/ui custom CSS variable classes
  {
    rules: {
      "no-console": "error",
      "tailwindcss/no-custom-classname": [
        "warn",
        {
          cssFiles: ["src/app/globals.css"],
          whitelist: shadcnPattern,
        },
      ],
      "tailwindcss/no-unnecessary-arbitrary-value": "warn",
    },
    settings: {
      tailwindcss: {
        config: path.join(__dirname, "./tailwind.config.js"),
      },
    },
  },
]);

export default eslintConfig;
