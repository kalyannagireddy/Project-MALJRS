import { useCaseContext } from "@/contexts/CaseContext";
import { TimelineEvent } from "@/types/case";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Plus, Trash2, Clock } from "lucide-react";
import { cn } from "@/lib/utils";

export default function TimelinePage() {
  const { caseData, updateCase } = useCaseContext();
  const timeline = caseData.timeline;

  const addEvent = () => {
    const newEvent: TimelineEvent = {
      id: crypto.randomUUID(),
      date: "",
      description: "",
      peopleInvolved: "",
      proofAvailable: false,
    };
    updateCase({ timeline: [...timeline, newEvent] });
  };

  const updateEvent = (id: string, partial: Partial<TimelineEvent>) => {
    updateCase({ timeline: timeline.map((e) => (e.id === id ? { ...e, ...partial } : e)) });
  };

  const removeEvent = (id: string) => {
    updateCase({ timeline: timeline.filter((e) => e.id !== id) });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Clock className="h-6 w-6 text-primary" />
          <h2 className="text-2xl font-bold">Case Timeline</h2>
        </div>
        <Button onClick={addEvent} size="sm" className="gap-1.5">
          <Plus className="h-4 w-4" /> Add Event
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          {timeline.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <Clock className="h-10 w-10 mx-auto mb-3 opacity-40" />
              <p>No timeline events yet. Add events to build your case timeline.</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-36">Date</TableHead>
                  <TableHead>Event Description</TableHead>
                  <TableHead className="w-40">People Involved</TableHead>
                  <TableHead className="w-24 text-center">Proof?</TableHead>
                  <TableHead className="w-12" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {timeline.map((event) => (
                  <TableRow key={event.id}>
                    <TableCell>
                      <Input type="date" value={event.date} onChange={(e) => updateEvent(event.id, { date: e.target.value })} className="text-sm" />
                    </TableCell>
                    <TableCell>
                      <Input placeholder="Describe event..." value={event.description} onChange={(e) => updateEvent(event.id, { description: e.target.value })} />
                    </TableCell>
                    <TableCell>
                      <Input placeholder="Names" value={event.peopleInvolved} onChange={(e) => updateEvent(event.id, { peopleInvolved: e.target.value })} />
                    </TableCell>
                    <TableCell className="text-center">
                      <Switch checked={event.proofAvailable} onCheckedChange={(v) => updateEvent(event.id, { proofAvailable: v })} />
                    </TableCell>
                    <TableCell>
                      <Button variant="ghost" size="icon" onClick={() => removeEvent(event.id)}>
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
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
