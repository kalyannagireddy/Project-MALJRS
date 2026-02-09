import { useCaseContext } from "@/contexts/CaseContext";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, Trash2, HelpCircle } from "lucide-react";

export default function LegalIssuesPage() {
  const { caseData, updateCase } = useCaseContext();

  const addIssue = () => updateCase({ legalIssues: [...caseData.legalIssues, ""] });
  const updateIssue = (i: number, val: string) => {
    const updated = [...caseData.legalIssues];
    updated[i] = val;
    updateCase({ legalIssues: updated });
  };
  const removeIssue = (i: number) => updateCase({ legalIssues: caseData.legalIssues.filter((_, idx) => idx !== i) });

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <HelpCircle className="h-6 w-6 text-primary" />
        <h2 className="text-2xl font-bold">Legal Issues</h2>
      </div>

      <Card>
        <CardHeader className="flex-row items-center justify-between">
          <div>
            <CardTitle className="text-base">Questions for the Court</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">What questions must the court answer in this case?</p>
          </div>
          <Button onClick={addIssue} size="sm" className="gap-1.5"><Plus className="h-4 w-4" /> Add Issue</Button>
        </CardHeader>
        <CardContent className="space-y-3">
          {caseData.legalIssues.length === 0 && (
            <p className="text-center text-muted-foreground py-6">No legal issues added yet.</p>
          )}
          {caseData.legalIssues.map((issue, i) => (
            <div key={i} className="flex gap-2">
              <Input value={issue} onChange={(e) => updateIssue(i, e.target.value)} placeholder={`Legal issue ${i + 1}`} />
              <Button variant="ghost" size="icon" onClick={() => removeIssue(i)}>
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
