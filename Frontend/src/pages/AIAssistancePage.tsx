import { useCaseContext } from "@/contexts/CaseContext";
import { AI_OPTIONS } from "@/types/case";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Bot } from "lucide-react";

export default function AIAssistancePage() {
  const { caseData, updateCase } = useCaseContext();

  const toggle = (option: string) => {
    const current = caseData.aiAssistance;
    const updated = current.includes(option) ? current.filter((o) => o !== option) : [...current, option];
    updateCase({ aiAssistance: updated });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Bot className="h-6 w-6 text-primary" />
        <h2 className="text-2xl font-bold">AI Assistance Selection</h2>
      </div>
      <p className="text-sm text-muted-foreground">Select what kind of help you want from the AI system.</p>

      <Card>
        <CardContent className="pt-6 space-y-4">
          {AI_OPTIONS.map((option) => (
            <div key={option} className="flex items-center gap-3">
              <Checkbox
                id={option}
                checked={caseData.aiAssistance.includes(option)}
                onCheckedChange={() => toggle(option)}
              />
              <Label htmlFor={option} className="cursor-pointer">{option}</Label>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
