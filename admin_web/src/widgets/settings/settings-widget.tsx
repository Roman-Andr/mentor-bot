"use client";

/* eslint-disable react-hooks/set-state-in-effect */
import { useState, useTransition, useCallback, useEffect } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { useLocale } from "next-intl";
import { useTheme } from "next-themes";
import { useTranslations } from "@/shared/hooks/use-translations";
import { usePreferences } from "@/shared/hooks/use-preferences";
import { Button } from "@/shared/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/ui/card";
import { Label } from "@/shared/ui/label";
import { Input } from "@/shared/ui/input";
import { Switch } from "@/shared/ui/switch";
import { Select } from "@/shared/ui/select";
import { PageContent } from "@/shared/layout/page-content";
import { useToast } from "@/shared/hooks/use-toast";
import { notificationsApi } from "@/shared/lib/api/notifications";
import {
  Bell, Globe, Palette, Save, Send, Clock, Sun, Moon, Monitor, CheckCircle2,
} from "lucide-react";
import { cn } from "@/shared/lib/utils";

type Section = "appearance" | "language" | "notifications" | "send-notification";

const NOTIFICATION_TYPES = [
  { value: "SYSTEM", label: "System" },
  { value: "REMINDER", label: "Reminder" },
  { value: "INFO", label: "Info" },
];

const NOTIFICATION_CHANNELS = [
  { value: "TELEGRAM", label: "Telegram" },
  { value: "EMAIL", label: "Email" },
  { value: "BOTH", label: "Both" },
];

interface NavItemProps {
  icon: React.ElementType;
  label: string;
  active: boolean;
  onClick: () => void;
}

function NavItem({ icon: Icon, label, active, onClick }: NavItemProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex w-full cursor-pointer items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
        active ? "bg-primary text-primary-foreground" : "hover:bg-muted text-muted-foreground hover:text-foreground",
      )}
    >
      <Icon className="size-4" />
      {label}
    </button>
  );
}

export function SettingsWidget() {
  const t = useTranslations();
  const router = useRouter();
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const { theme: currentTheme, setTheme } = useTheme();
  const currentLocale = useLocale();
  const { toast } = useToast();
  const [isPending, startTransition] = useTransition();
  const activeSection = (searchParams.get("tab") as Section) || "appearance";

  const { preferences, isLoading: prefsLoading, updatePreferences, isUpdating: prefsUpdating } = usePreferences();

  const [selectedTheme, setSelectedTheme] = useState(currentTheme || "system");
  const [selectedLanguage, setSelectedLanguage] = useState(currentLocale || "ru");
  const [telegramEnabled, setTelegramEnabled] = useState(
    preferences?.success && preferences.data ? preferences.data.notification_telegram_enabled ?? true : true,
  );
  const [emailEnabled, setEmailEnabled] = useState(
    preferences?.success && preferences.data ? preferences.data.notification_email_enabled ?? true : true,
  );

  const [notifForm, setNotifForm] = useState({
    userId: "", type: "SYSTEM", channel: "TELEGRAM", subject: "", body: "", scheduledAt: "",
  });
  const [notifSending, setNotifSending] = useState(false);

  useEffect(() => {
    if (preferences?.success && preferences.data) {
      setTelegramEnabled(preferences.data.notification_telegram_enabled ?? true);
      setEmailEnabled(preferences.data.notification_email_enabled ?? true);
      setSelectedLanguage(preferences.data.language);
    }
  }, [preferences]);

  useEffect(() => {
    if (currentTheme && currentTheme !== selectedTheme) setSelectedTheme(currentTheme);
  }, [currentTheme]);

  const themes = [
    { value: "light" as const, label: t("settings.themeLight"), icon: Sun },
    { value: "dark" as const, label: t("settings.themeDark"), icon: Moon },
    { value: "system" as const, label: t("settings.themeSystem"), icon: Monitor },
  ];

  const languages = [
    { value: "ru", label: t("settings.languageRu") },
    { value: "en", label: t("settings.languageEn") },
  ];

  const handleSave = useCallback(() => {
    setTheme(selectedTheme);
    updatePreferences({
      language: selectedLanguage,
      notification_telegram_enabled: telegramEnabled,
      notification_email_enabled: emailEnabled,
    });
    if (selectedLanguage !== currentLocale) {
      document.cookie = `locale=${selectedLanguage};path=/;max-age=31536000`;
      startTransition(() => { router.refresh(); });
    }
    toast(t("settings.saved"), "success");
  }, [selectedTheme, selectedLanguage, currentLocale, telegramEnabled, emailEnabled, setTheme, router, toast, t, updatePreferences]);

  const handleCancel = useCallback(() => {
    setSelectedTheme(currentTheme || "system");
    setSelectedLanguage(currentLocale || "ru");
    if (preferences?.success && preferences.data) {
      setTelegramEnabled(preferences.data.notification_telegram_enabled);
      setEmailEnabled(preferences.data.notification_email_enabled);
    }
  }, [currentTheme, currentLocale, preferences]);

  const handleSectionChange = useCallback((section: Section) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("tab", section);
    router.replace(`${pathname}?${params.toString()}`);
  }, [searchParams, pathname, router]);

  const handleSendNotification = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!notifForm.userId || !notifForm.body) return;
    setNotifSending(true);
    try {
      if (notifForm.scheduledAt) {
        await notificationsApi.schedule({
          user_id: Number(notifForm.userId),
          type: notifForm.type,
          channel: notifForm.channel,
          body: notifForm.body,
          subject: notifForm.subject || null,
          scheduled_time: new Date(notifForm.scheduledAt).toISOString(),
        });
        toast(t("settings.notificationScheduled") || "Notification scheduled", "success");
      } else {
        await notificationsApi.send({
          user_id: Number(notifForm.userId),
          type: notifForm.type,
          channel: notifForm.channel,
          body: notifForm.body,
          subject: notifForm.subject || null,
        });
        toast(t("settings.notificationSent") || "Notification sent", "success");
      }
      setNotifForm((f) => ({ ...f, userId: "", body: "", subject: "", scheduledAt: "" }));
    } catch {
      toast(t("common.error") || "Error", "error");
    } finally {
      setNotifSending(false);
    }
  };

  return (
    <PageContent title={t("settings.title")} subtitle={t("settings.subtitle")}>
      <div className="grid gap-6 md:grid-cols-4 md:items-start">
        <Card className="md:col-span-1">
          <CardContent className="p-3">
            <nav className="space-y-1">
              <NavItem icon={Palette} label={t("settings.appearance")} active={activeSection === "appearance"} onClick={() => handleSectionChange("appearance")} />
              <NavItem icon={Globe} label={t("settings.language")} active={activeSection === "language"} onClick={() => handleSectionChange("language")} />
              <NavItem icon={Bell} label={t("settings.notifications")} active={activeSection === "notifications"} onClick={() => handleSectionChange("notifications")} />
              <NavItem
                icon={Send}
                label={t("settings.sendNotification") || "Send Notification"}
                active={activeSection === "send-notification"}
                onClick={() => handleSectionChange("send-notification")}
              />
            </nav>
          </CardContent>
        </Card>

        <div className="space-y-6 md:col-span-3">
          {activeSection === "appearance" && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><Palette className="size-5" />{t("settings.appearance")}</CardTitle>
                <CardDescription>{t("settings.appearanceDescription")}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-3">
                  {themes.map((th) => {
                    const Icon = th.icon;
                    return (
                      <button
                        key={th.value}
                        onClick={() => setSelectedTheme(th.value)}
                        className={cn(
                          "relative flex flex-col items-center gap-2 rounded-xl border-2 p-4 text-sm transition-all",
                          selectedTheme === th.value ? "border-primary bg-primary/5" : "border-border hover:border-primary/50",
                        )}
                      >
                        {selectedTheme === th.value && <CheckCircle2 className="text-primary absolute top-2 right-2 size-4" />}
                        <Icon className="size-6" />
                        {th.label}
                      </button>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          )}

          {activeSection === "language" && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><Globe className="size-5" />{t("settings.language")}</CardTitle>
                <CardDescription>{t("settings.languageDescription")}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-3">
                  {languages.map((lang) => (
                    <button
                      key={lang.value}
                      onClick={() => setSelectedLanguage(lang.value)}
                      className={cn(
                        "relative flex items-center gap-3 rounded-xl border-2 p-4 text-sm transition-all",
                        selectedLanguage === lang.value ? "border-primary bg-primary/5" : "border-border hover:border-primary/50",
                      )}
                    >
                      {selectedLanguage === lang.value && <CheckCircle2 className="text-primary absolute top-2 right-2 size-4" />}
                      <Globe className="size-5" />
                      {lang.label}
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {activeSection === "notifications" && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><Bell className="size-5" />{t("settings.notifications")}</CardTitle>
                <CardDescription>{t("settings.notificationsDescription")}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <p className="font-medium">{t("settings.telegramNotifications")}</p>
                    <p className="text-muted-foreground text-sm">{t("settings.telegramNotificationsDescription")}</p>
                  </div>
                  <Switch checked={telegramEnabled} onCheckedChange={setTelegramEnabled} disabled={prefsLoading} />
                </div>
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <p className="font-medium">{t("settings.emailNotifications")}</p>
                    <p className="text-muted-foreground text-sm">{t("settings.emailNotificationsDescription")}</p>
                  </div>
                  <Switch checked={emailEnabled} onCheckedChange={setEmailEnabled} disabled={prefsLoading} />
                </div>
              </CardContent>
            </Card>
          )}

          {activeSection === "send-notification" && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><Send className="size-5" />{t("settings.sendNotification") || "Send Notification"}</CardTitle>
                <CardDescription>{t("settings.sendNotificationDesc") || "Send an immediate or scheduled notification to a user"}</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSendNotification} className="space-y-4">
                  <div className="grid gap-4 sm:grid-cols-2">
                    <div className="space-y-1.5">
                      <Label>{t("settings.recipientUserId") || "Recipient User ID"}</Label>
                      <Input
                        type="number"
                        value={notifForm.userId}
                        onChange={(ev) => setNotifForm((f) => ({ ...f, userId: ev.target.value }))}
                        placeholder="User ID"
                        required
                      />
                    </div>
                    <div className="space-y-1.5">
                      <Label>{t("settings.notificationType") || "Type"}</Label>
                      <Select value={notifForm.type} onChange={(v) => setNotifForm((f) => ({ ...f, type: v }))} options={NOTIFICATION_TYPES} />
                    </div>
                    <div className="space-y-1.5">
                      <Label>{t("settings.channel") || "Channel"}</Label>
                      <Select value={notifForm.channel} onChange={(v) => setNotifForm((f) => ({ ...f, channel: v }))} options={NOTIFICATION_CHANNELS} />
                    </div>
                    <div className="space-y-1.5">
                      <Label>{t("settings.subject") || "Subject (optional)"}</Label>
                      <Input
                        value={notifForm.subject}
                        onChange={(ev) => setNotifForm((f) => ({ ...f, subject: ev.target.value }))}
                        placeholder={t("common.optional") || "Optional"}
                      />
                    </div>
                  </div>
                  <div className="space-y-1.5">
                    <Label>{t("settings.messageBody") || "Message"}</Label>
                    <textarea
                      value={notifForm.body}
                      onChange={(ev) => setNotifForm((f) => ({ ...f, body: ev.target.value }))}
                      placeholder={t("settings.messagePlaceholder") || "Enter notification message..."}
                      required
                      rows={3}
                      className="border-input bg-background placeholder:text-muted-foreground focus-visible:ring-ring flex min-h-[80px] w-full rounded-md border px-3 py-2 text-sm focus-visible:ring-1 focus-visible:outline-none"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <Label className="flex items-center gap-1.5">
                      <Clock className="size-3.5" />
                      {t("settings.scheduledAt") || "Schedule for (optional)"}
                    </Label>
                    <Input
                      type="datetime-local"
                      value={notifForm.scheduledAt}
                      onChange={(ev) => setNotifForm((f) => ({ ...f, scheduledAt: ev.target.value }))}
                    />
                    <p className="text-muted-foreground text-xs">{t("settings.leaveBlankToSendNow") || "Leave blank to send immediately"}</p>
                  </div>
                  <div className="flex justify-end">
                    <Button type="submit" disabled={notifSending} className="gap-2">
                      {notifForm.scheduledAt ? <Clock className="size-4" /> : <Send className="size-4" />}
                      {notifForm.scheduledAt ? t("settings.scheduleNotification") || "Schedule" : t("settings.sendNow") || "Send Now"}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}

          {activeSection !== "send-notification" && (
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={handleCancel}>{t("settings.cancel")}</Button>
              <Button className="gap-2" onClick={handleSave} disabled={isPending || prefsUpdating}>
                <Save className="size-4" />
                {t("settings.save")}
              </Button>
            </div>
          )}
        </div>
      </div>
    </PageContent>
  );
}
