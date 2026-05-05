import { DialogueEditWidget } from "@/widgets/dialogues/dialogue-edit-widget";

export default function DialogueEditPage({ params }: { params: Promise<{ id: string }> }) {
  return <DialogueEditWidget params={params} />;
}
