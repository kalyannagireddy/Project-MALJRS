import { useCaseContext } from "@/contexts/CaseContext";
import { WitnessInfo } from "@/types/case";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Plus, Trash2, Users } from "lucide-react";

export default function WitnessesPage() {
  const { caseData, updateCase } = useCaseContext();

  const addWitness = () => {
    const w: WitnessInfo = { id: crypto.randomUUID(), name: "", knowledge: "", linkedTimelineEventId: "" };
    updateCase({ witnesses: [...caseData.witnesses, w] });
  };

  const updateWitness = (id: string, partial: Partial<WitnessInfo>) => {
    updateCase({ witnesses: caseData.witnesses.map((w) => (w.id === id ? { ...w, ...partial } : w)) });
  };

  const removeWitness = (id: string) => {
    updateCase({ witnesses: caseData.witnesses.filter((w) => w.id !== id) });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Users className="h-6 w-6 text-primary" />
          <h2 className="text-2xl font-bold">Witness Information</h2>
        </div>
        <Button onClick={addWitness} size="sm" className="gap-1.5"><Plus className="h-4 w-4" /> Add Witness</Button>
      </div>
      <p className="text-sm text-muted-foreground">Optional — add witnesses and link them to timeline events.</p>

      <Card>
        <CardContent className="p-0">
          {caseData.witnesses.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <Users className="h-10 w-10 mx-auto mb-3 opacity-40" />
              <p>No witnesses added yet.</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Witness Name</TableHead>
                  <TableHead>What They Know</TableHead>
                  <TableHead className="w-48">Linked Event</TableHead>
                  <TableHead className="w-12" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {caseData.witnesses.map((w) => (
                  <TableRow key={w.id}>
                    <TableCell><Input placeholder="Name" value={w.name} onChange={(e) => updateWitness(w.id, { name: e.target.value })} /></TableCell>
                    <TableCell><Input placeholder="Their knowledge" value={w.knowledge} onChange={(e) => updateWitness(w.id, { knowledge: e.target.value })} /></TableCell>
                    <TableCell>
                      <Select value={w.linkedTimelineEventId} onValueChange={(v) => updateWitness(w.id, { linkedTimelineEventId: v })}>
                        <SelectTrigger><SelectValue placeholder="Select event" /></SelectTrigger>
                        <SelectContent>
                          {caseData.timeline.map((ev) => (
                            <SelectItem key={ev.id} value={ev.id}>{ev.date ? `${ev.date} — ` : ""}{ev.description || "Untitled"}</SelectItem>
                          ))}
                          {caseData.timeline.length === 0 && <SelectItem value="none" disabled>No events</SelectItem>}
                        </SelectContent>
                      </Select>
                    </TableCell>
                    <TableCell>
                      <Button variant="ghost" size="icon" onClick={() => removeWitness(w.id)}><Trash2 className="h-4 w-4 text-destructive" /></Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
