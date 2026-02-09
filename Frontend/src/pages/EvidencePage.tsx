import { useCaseContext } from "@/contexts/CaseContext";
import { EvidenceItem, EVIDENCE_STRENGTHS, EVIDENCE_TYPES } from "@/types/case";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Plus, Trash2, FileText } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export default function EvidencePage() {
  const { caseData, updateCase } = useCaseContext();

  const addEvidence = () => {
    const item: EvidenceItem = {
      id: crypto.randomUUID(),
      fileName: "",
      description: "",
      linkedTimelineEventId: "",
      strength: "Medium",
      type: "Document",
    };
    updateCase({ evidence: [...caseData.evidence, item] });
  };

  const updateEvidence = (id: string, partial: Partial<EvidenceItem>) => {
    updateCase({ evidence: caseData.evidence.map((e) => (e.id === id ? { ...e, ...partial } : e)) });
  };

  const removeEvidence = (id: string) => {
    updateCase({ evidence: caseData.evidence.filter((e) => e.id !== id) });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FileText className="h-6 w-6 text-primary" />
          <h2 className="text-2xl font-bold">Evidence Upload & Tagging</h2>
        </div>
        <Button onClick={addEvidence} size="sm" className="gap-1.5">
          <Plus className="h-4 w-4" /> Add Evidence
        </Button>
      </div>

      {caseData.evidence.length === 0 && (
        <Card>
          <CardContent className="text-center py-12 text-muted-foreground">
            <FileText className="h-10 w-10 mx-auto mb-3 opacity-40" />
            <p>No evidence added yet. Add evidence items to tag and link them to your timeline.</p>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        {caseData.evidence.map((item) => (
          <Card key={item.id}>
            <CardHeader className="flex-row items-start justify-between pb-3">
              <Badge variant="outline" className="text-xs">{item.type}</Badge>
              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => removeEvidence(item.id)}>
                <Trash2 className="h-3.5 w-3.5 text-destructive" />
              </Button>
            </CardHeader>
            <CardContent className="space-y-3 pt-0">
              <div className="space-y-1.5">
                <Label className="text-xs">File Name</Label>
                <Input placeholder="document.pdf" value={item.fileName} onChange={(e) => updateEvidence(item.id, { fileName: e.target.value })} />
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs">Description</Label>
                <Input placeholder="What is this document?" value={item.description} onChange={(e) => updateEvidence(item.id, { description: e.target.value })} />
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs">Linked Timeline Event</Label>
                <Select value={item.linkedTimelineEventId} onValueChange={(v) => updateEvidence(item.id, { linkedTimelineEventId: v })}>
                  <SelectTrigger><SelectValue placeholder="Select event" /></SelectTrigger>
                  <SelectContent>
                    {caseData.timeline.map((ev) => (
                      <SelectItem key={ev.id} value={ev.id}>{ev.date ? `${ev.date} — ` : ""}{ev.description || "Untitled event"}</SelectItem>
                    ))}
                    {caseData.timeline.length === 0 && <SelectItem value="none" disabled>No timeline events</SelectItem>}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label className="text-xs">Strength</Label>
                  <Select value={item.strength} onValueChange={(v: any) => updateEvidence(item.id, { strength: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>{EVIDENCE_STRENGTHS.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
                <div className="space-y-1.5">
                  <Label className="text-xs">Type</Label>
                  <Select value={item.type} onValueChange={(v: any) => updateEvidence(item.id, { type: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>{EVIDENCE_TYPES.map((t) => <SelectItem key={t} value={t}>{t}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
