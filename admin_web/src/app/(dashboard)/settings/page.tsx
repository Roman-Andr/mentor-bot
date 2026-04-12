"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { useTheme } from "next-themes";
import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { PageHeader } from "@/components/layout/page-header";
import { useToast } from "@/hooks/use-toast";
import { Globe, Palette, Save } from "lucide-react";


export default function SettingsPage() {
  const t = useTranslations();

  const themes = [
    { value: "light" as const, label: t("settings.themeLight") },
    { value: "dark" as const, label: t("settings.themeDark") },
    { value: "system" as const, label: t("settings.themeSystem") },
  ];

  const languages = [
    { value: "ru", label: t("settings.languageRu") },
    { value: "en", label: t("settings.languageEn") },
  ];
  const router = useRouter();
  const { theme: currentTheme, setTheme } = useTheme();
  const { toast } = useToast();
  const [isPending, startTransition] = useTransition();
  const [activeSection, setActiveSection] = useState<"appearance" | "language">("appearance");

  const [selectedTheme, setSelectedTheme] = useState(currentTheme || "system");
  const [selectedLanguage, setSelectedLanguage] = useState(
    document.cookie.match(/locale=([^;]+)/)?.[1] || "ru"
  );

  const handleSave = () => {
    setTheme(selectedTheme);

    const currentLocale = document.cookie.match(/locale=([^;]+)/)?.[1] || "ru";
    if (selectedLanguage !== currentLocale) {
      document.cookie = `locale=${selectedLanguage};path=/;max-age=31536000`;
      startTransition(() => {
        router.refresh();
      });
    }

    toast(t("settings.saved"), "success");
  };

  const handleCancel = () => {
    setSelectedTheme(currentTheme || "system");
    setSelectedLanguage(document.cookie.match(/locale=([^;]+)/)?.[1] || "ru");
  };

  return (
    <div className="space-y-6 p-6">
      <PageHeader title={t("settings.title")} subtitle={t("settings.subtitle")} />

      <div className="grid gap-6 md:grid-cols-4">
        <Card className="md:col-span-1">
          <CardContent className="p-4">
            <nav className="space-y-1">
              <button
                onClick={() => setActiveSection("appearance")}
                className={`flex w-full cursor-pointer items-center gap-3 rounded-lg px-3 py-2 text-sm ${
                  activeSection === "appearance"
                    ? "bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
                    : "hover:bg-gray-100 dark:hover:bg-gray-800"
                }`}
              >
                <Palette className="size-4" />
                {t("settings.appearance")}
              </button>
              <button
                onClick={() => setActiveSection("language")}
                className={`flex w-full cursor-pointer items-center gap-3 rounded-lg px-3 py-2 text-sm ${
                  activeSection === "language"
                    ? "bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
                    : "hover:bg-gray-100 dark:hover:bg-gray-800"
                }`}
              >
                <Globe className="size-4" />
                {t("settings.language")}
              </button>
            </nav>
          </CardContent>
        </Card>

        <div className="space-y-6 md:col-span-3">
          {activeSection === "appearance" && (
            <Card>
              <CardHeader>
                <CardTitle>{t("settings.appearance")}</CardTitle>
                <CardDescription>{t("settings.appearanceDescription")}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <Label>{t("settings.theme")}</Label>
                  <div className="mt-2 flex gap-4">
                    {themes.map((th) => (
                      <label key={th.value} className="flex cursor-pointer items-center gap-2">
                        <input
                          type="radio"
                          name="theme"
                          value={th.value}
                          checked={selectedTheme === th.value}
                          onChange={() => setSelectedTheme(th.value)}
                          className="accent-brand"
                        />
                        <span>{th.label}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {activeSection === "language" && (
            <Card>
              <CardHeader>
                <CardTitle>{t("settings.language")}</CardTitle>
                <CardDescription>{t("settings.languageDescription")}</CardDescription>
              </CardHeader>
              <CardContent>
                <div>
                  <Label>{t("settings.selectLanguage")}</Label>
                  <div className="mt-2 flex gap-4">
                    {languages.map((lang) => (
                      <label key={lang.value} className="flex cursor-pointer items-center gap-2">
                        <input
                          type="radio"
                          name="language"
                          value={lang.value}
                          checked={selectedLanguage === lang.value}
                          onChange={() => setSelectedLanguage(lang.value)}
                          className="accent-brand"
                        />
                        <span>{lang.label}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={handleCancel}>
              {t("settings.cancel")}
            </Button>
            <Button className="gap-2" onClick={handleSave} disabled={isPending}>
              <Save className="size-4" />
              {t("settings.save")}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
