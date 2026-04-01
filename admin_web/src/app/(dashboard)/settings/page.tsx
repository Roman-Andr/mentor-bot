"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { useTheme } from "next-themes";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { PageHeader } from "@/components/layout/page-header";
import { useToast } from "@/components/ui/toast";
import { Palette, Save } from "lucide-react";

const themes = [
  { value: "light" as const, labelKey: "themeLight" },
  { value: "dark" as const, labelKey: "themeDark" },
  { value: "system" as const, labelKey: "themeSystem" },
];

const languages = [
  { value: "ru", labelKey: "languageRu" },
  { value: "en", labelKey: "languageEn" },
];

export default function SettingsPage() {
  const t = useTranslations("settings");
  const router = useRouter();
  const { theme: currentTheme, setTheme } = useTheme();
  const { toast } = useToast();
  const [isPending, startTransition] = useTransition();

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

    toast(t("saved"), "success");
  };

  const handleCancel = () => {
    setSelectedTheme(currentTheme || "system");
    setSelectedLanguage(document.cookie.match(/locale=([^;]+)/)?.[1] || "ru");
  };

  return (
    <div className="space-y-6 p-6">
      <PageHeader title={t("title")} subtitle={t("subtitle")} />

      <div className="grid gap-6 md:grid-cols-4">
        <Card className="md:col-span-1">
          <CardContent className="p-4">
            <nav className="space-y-1">
              <button className="flex w-full cursor-pointer items-center gap-3 rounded-lg bg-blue-50 px-3 py-2 text-sm text-blue-700 dark:bg-blue-950 dark:text-blue-300">
                <Palette className="size-4" />
                {t("appearance")}
              </button>
            </nav>
          </CardContent>
        </Card>

        <div className="space-y-6 md:col-span-3">
          <Card>
            <CardHeader>
              <CardTitle>{t("appearance")}</CardTitle>
              <CardDescription>{t("appearanceDescription")}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <Label>{t("theme")}</Label>
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
                      <span>{t(th.labelKey)}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <Label>{t("language")}</Label>
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
                      <span>{t(lang.labelKey)}</span>
                    </label>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={handleCancel}>
              {t("cancel")}
            </Button>
            <Button className="gap-2" onClick={handleSave} disabled={isPending}>
              <Save className="size-4" />
              {t("save")}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
