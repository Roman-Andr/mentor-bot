import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface EscalationCounts {
  hr: number;
  mentor: number;
  inProgress: number;
}

interface EscalationSummaryProps {
  escalations: EscalationCounts;
}

export function EscalationSummary({ escalations }: EscalationSummaryProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Эскалации</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between rounded-lg bg-red-50 p-3">
            <span className="text-sm text-red-700">К HR</span>
            <span className="font-bold text-red-700">{escalations.hr}</span>
          </div>
          <div className="flex items-center justify-between rounded-lg bg-yellow-50 p-3">
            <span className="text-sm text-yellow-700">К наставнику</span>
            <span className="font-bold text-yellow-700">{escalations.mentor}</span>
          </div>
          <div className="flex items-center justify-between rounded-lg bg-blue-50 p-3">
            <span className="text-sm text-blue-700">В работе</span>
            <span className="font-bold text-blue-700">{escalations.inProgress}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
