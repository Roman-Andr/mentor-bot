import { useTranslations } from "@/shared/hooks/use-translations";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { AlertTriangle, ExternalLink } from "lucide-react";
import Link from "next/link";
import { Button } from "@/shared/ui/button";

interface EscalationCounts {
  hr: number;
  mentor: number;
  inProgress: number;
  items: any[];
}

interface EscalationSummaryProps {
  escalations: EscalationCounts;
}

export function EscalationSummary({ escalations }: EscalationSummaryProps) {
  const t = useTranslations();

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-base">{t("dashboard.escalations")}</CardTitle>
        <Link href="/escalations">
          <Button variant="ghost" size="sm" className="gap-1 text-xs">
            <ExternalLink className="size-3" />
            <span className="hidden sm:inline">{t("common.viewAll")}</span>
          </Button>
        </Link>
      </CardHeader>
      <CardContent className="space-y-2">
        {escalations.items.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-4 text-center">
            <div className="bg-muted mb-2 flex size-10 items-center justify-center rounded-full">
              <AlertTriangle className="text-muted-foreground size-5" />
            </div>
            <p className="text-muted-foreground text-sm">{t("escalations.noEscalations")}</p>
          </div>
        ) : (
          <div className="space-y-2">
            {escalations.items.slice(0, 5).map((item: any) => (
              <div key={item.id} className="rounded-lg border px-3 py-2">
                <div className="mb-1 flex items-start justify-between gap-2">
                  <p className="min-w-0 flex-1 truncate text-sm font-medium">{item.reason || item.description || `Эскалация #${item.id}`}</p>
                  <span className="text-muted-foreground text-xs whitespace-nowrap">{new Date(item.created_at).toLocaleDateString()}</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span className="rounded bg-muted px-1.5 py-0.5">{item.type}</span>
                  <span>•</span>
                  <span>{item.status}</span>
                  {item.user_id && (
                    <>
                      <span>•</span>
                      <span>Пользователь #{item.user_id}</span>
                    </>
                  )}
                </div>
              </div>
            ))}
            {escalations.items.length > 5 && (
              <p className="text-muted-foreground text-center text-xs">
                +{escalations.items.length - 5} {t("common.more")}
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
