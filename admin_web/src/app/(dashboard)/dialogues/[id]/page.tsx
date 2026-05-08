import { PageContent } from "@/shared/layout/page-content";
import { DialogueEditWidget } from "@/widgets/dialogues/dialogue-edit-widget";

export default function DialogueEditPage({ params }: { params: Promise<{ id: string }> }) {
  return (
    <PageContent title="" subtitle="">
      <DialogueEditWidget params={params} />
    </PageContent>
  );
}
