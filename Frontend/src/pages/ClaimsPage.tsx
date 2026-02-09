import { useCaseContext } from "@/contexts/CaseContext";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Plus, Trash2, Gavel } from "lucide-react";

export default function ClaimsPage() {
  const { caseData, updateCase } = useCaseContext();

  const addClaim = () => updateCase({ claims: [...caseData.claims, ""] });
  const updateClaim = (i: number, val: string) => {
    const updated = [...caseData.claims];
    updated[i] = val;
    updateCase({ claims: updated });
  };
  const removeClaim = (i: number) => updateCase({ claims: caseData.claims.filter((_, idx) => idx !== i) });

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Gavel className="h-6 w-6 text-primary" />
        <h2 className="text-2xl font-bold">Claims / Allegations</h2>
      </div>

      <Card>
        <CardHeader className="flex-row items-center justify-between">
          <CardTitle className="text-base">Individual Claims</CardTitle>
          <Button onClick={addClaim} size="sm" className="gap-1.5"><Plus className="h-4 w-4" /> Add Claim</Button>
        </CardHeader>
        <CardContent className="space-y-3">
          {caseData.claims.length === 0 && (
            <p className="text-center text-muted-foreground py-6">No claims added yet.</p>
          )}
          {caseData.claims.map((claim, i) => (
            <div key={i} className="flex gap-2">
              <Input value={claim} onChange={(e) => updateClaim(i, e.target.value)} placeholder={`Claim ${i + 1}`} />
              <Button variant="ghost" size="icon" onClick={() => removeClaim(i)}>
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Relief Requested</CardTitle>
        </CardHeader>
        <CardContent>
          <Textarea
            placeholder="Describe the relief sought from the court..."
            rows={5}
            value={caseData.reliefRequested}
            onChange={(e) => updateCase({ reliefRequested: e.target.value })}
          />
        </CardContent>
      </Card>
    </div>
  );
}
