import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Copy, Check, ExternalLink } from "lucide-react";

interface InvitationLinkDialogProps {
  url: string | null;
  onOpenChange: (open: boolean) => void;
}

export function InvitationLinkDialog({ url, onOpenChange }: InvitationLinkDialogProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!url) return;
    await navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Dialog open={!!url} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Приглашение создано</DialogTitle>
          <DialogDescription>
            Отправьте эту ссылку новому сотруднику для регистрации через Telegram бота
          </DialogDescription>
        </DialogHeader>
        <div className="flex gap-2">
          <Input value={url || ""} readOnly className="font-mono text-sm" />
          <Button variant="outline" size="icon" onClick={handleCopy} className="shrink-0">
            {copied ? <Check className="size-4 text-green-600" /> : <Copy className="size-4" />}
          </Button>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Закрыть
          </Button>
          {url && (
            <Button className="gap-2" asChild>
              <a href={url} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="size-4" />
                Открыть
              </a>
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
