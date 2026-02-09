import { useCaseContext } from "@/contexts/CaseContext";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { ShieldCheck, ShieldAlert } from "lucide-react";

export default function StrengthsWeaknessesPage() {
  const { caseData, updateCase } = useCaseContext();

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Strengths & Weaknesses</h2>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader className="flex-row items-center gap-2 pb-3">
            <ShieldCheck className="h-5 w-5 text-[hsl(var(--legal-success))]" />
            <CardTitle className="text-base">Strengths</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              placeholder="What strongly supports your case?"
              rows={8}
              value={caseData.strengths}
              onChange={(e) => updateCase({ strengths: e.target.value })}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex-row items-center gap-2 pb-3">
            <ShieldAlert className="h-5 w-5 text-destructive" />
            <CardTitle className="text-base">Weaknesses</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              placeholder="What may weaken your case?"
              rows={8}
              value={caseData.weaknesses}
              onChange={(e) => updateCase({ weaknesses: e.target.value })}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
