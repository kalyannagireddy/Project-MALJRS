import { useCaseContext } from "@/contexts/CaseContext";
import { STEPS } from "@/types/case";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";
import { CheckCircle, Edit, Send } from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

import { useState } from "react";
import { CaseService } from "@/services/api";

export default function ReviewPage() {
  const { caseData } = useCaseContext();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      // Use selected AI options from caseData, or default to full analysis
      const options = caseData.aiAssistance.length > 0 ? caseData.aiAssistance : ["Full Analysis"];

      const result = await CaseService.processCase(caseData, options);

      if (result.success) {
        toast.success("Case analyzed successfully!", { description: "AI analysis complete." });
        console.log("AI Report:", result.report);
        // Navigate to a results page if exists, or stay here showing success
        // For now, we'll just show the success toast
      }
    } catch (error) {
      console.error("Submission failed:", error);
      toast.error("Failed to submit case", { description: "Please try again later." });
    } finally {
      setIsSubmitting(false);
    }
  };

  const Section = ({ title, stepIndex, children }: { title: string; stepIndex: number; children: React.ReactNode }) => (
    <Card className="glass-card">
      <CardHeader className="flex-row items-center justify-between pb-4 border-b border-border/30">
        <CardTitle className="text-base font-semibold">{title}</CardTitle>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate(STEPS[stepIndex].path)}
          className="gap-2 text-xs hover:bg-accent/10 hover:text-primary transition-all duration-200"
        >
          <Edit className="h-3.5 w-3.5" />
          Edit
        </Button>
      </CardHeader>
      <CardContent className="pt-5 text-sm space-y-2.5">{children}</CardContent>
    </Card>
  );

  const Field = ({ label, value }: { label: string; value: string }) => (
    <div className="flex gap-3">
      <span className="text-muted-foreground min-w-[160px] font-medium">{label}:</span>
      <span className="font-normal mono text-sm">{value || "—"}</span>
    </div>
  );

  return (
    <div className="space-y-7">
      {/* Page header */}
      <div className="flex items-center gap-4">
        <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-success/10 border border-success/20">
          <CheckCircle className="h-6 w-6 text-success" />
        </div>
        <div>
          <h2 className="text-3xl font-bold">Review & Submit</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Review all details before submitting to the AI analysis system
          </p>
        </div>
      </div>

      {/* Review sections */}
      <div className="space-y-5">
        <Section title="Case Basic Information" stepIndex={0}>
          <Field label="Case Title" value={caseData.caseTitle} />
          <Field label="Case Type" value={caseData.caseType} />
          <Field label="Court" value={caseData.courtJurisdiction} />
          <Field label="Stage" value={caseData.stageOfCase} />
          <Field label="Plaintiff" value={caseData.plaintiffName} />
          <Field label="Defendant" value={caseData.defendantName} />
        </Section>

        <Section title="Timeline" stepIndex={1}>
          {caseData.timeline.length === 0 ? (
            <p className="text-muted-foreground italic">No events added.</p>
          ) : (
            <div className="space-y-3">
              {caseData.timeline.map((e) => (
                <div key={e.id} className="flex items-start gap-3 pb-3 border-b border-border/20 last:border-0 last:pb-0">
                  <span className="text-muted-foreground mono text-xs min-w-[90px]">{e.date || "No date"}</span>
                  <div className="flex-1">
                    <span className="text-sm">{e.description || "No description"}</span>
                    {e.proofAvailable && (
                      <Badge variant="secondary" className="ml-2 text-xs">Proof Available</Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </Section>

        <Section title="Claims" stepIndex={2}>
          {caseData.claims.length === 0 ? (
            <p className="text-muted-foreground italic">No claims added.</p>
          ) : (
            <ul className="list-disc list-inside space-y-1.5 marker:text-primary">
              {caseData.claims.map((c, i) => (
                <li key={i} className="text-sm">{c || "—"}</li>
              ))}
            </ul>
          )}
          {caseData.reliefRequested && (
            <div className="mt-4 pt-4 border-t border-border/30">
              <span className="text-muted-foreground font-medium">Relief Requested: </span>
              <span className="text-sm">{caseData.reliefRequested}</span>
            </div>
          )}
        </Section>

        <Section title="Evidence" stepIndex={3}>
          {caseData.evidence.length === 0 ? (
            <p className="text-muted-foreground italic">No evidence added.</p>
          ) : (
            <div className="space-y-3">
              {caseData.evidence.map((e) => (
                <div key={e.id} className="flex items-center gap-3 flex-wrap">
                  <Badge variant="outline" className="text-xs">{e.type}</Badge>
                  <span className="text-sm flex-1">{e.description || e.fileName || "Untitled"}</span>
                  <Badge
                    variant={e.strength === "Strong" ? "default" : "secondary"}
                    className={cn("text-xs", e.strength === "Strong" && "bg-success/15 text-success border-success/30")}
                  >
                    {e.strength}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </Section>

        <Section title="Legal Issues" stepIndex={4}>
          {caseData.legalIssues.length === 0 ? (
            <p className="text-muted-foreground italic">No issues added.</p>
          ) : (
            <ul className="list-disc list-inside space-y-1.5 marker:text-primary">
              {caseData.legalIssues.map((i, idx) => (
                <li key={idx} className="text-sm">{i || "—"}</li>
              ))}
            </ul>
          )}
        </Section>

        <Section title="Laws & Sections" stepIndex={5}>
          {caseData.lawSections.length === 0 ? (
            <p className="text-muted-foreground italic">No laws added.</p>
          ) : (
            <div className="space-y-2.5">
              {caseData.lawSections.map((s) => (
                <div key={s.id} className="text-sm">
                  <span className="font-semibold">{s.actName}</span>
                  {s.sectionNumber && <span className="mono ml-2">§ {s.sectionNumber}</span>}
                  {s.description && <span className="text-muted-foreground ml-2">({s.description})</span>}
                </div>
              ))}
            </div>
          )}
        </Section>

        <Section title="Strengths & Weaknesses" stepIndex={6}>
          <Field label="Strengths" value={caseData.strengths} />
          <Field label="Weaknesses" value={caseData.weaknesses} />
        </Section>

        <Section title="Witnesses" stepIndex={7}>
          {caseData.witnesses.length === 0 ? (
            <p className="text-muted-foreground italic">No witnesses added.</p>
          ) : (
            <div className="space-y-2.5">
              {caseData.witnesses.map((w) => (
                <div key={w.id} className="text-sm">
                  <span className="font-semibold">{w.name}</span>
                  <span className="text-muted-foreground"> — {w.knowledge}</span>
                </div>
              ))}
            </div>
          )}
        </Section>

        <Section title="AI Assistance" stepIndex={8}>
          {caseData.aiAssistance.length === 0 ? (
            <p className="text-muted-foreground italic">No options selected.</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {caseData.aiAssistance.map((a) => (
                <Badge key={a} className="bg-primary/15 text-primary border-primary/30 hover:bg-primary/20">{a}</Badge>
              ))}
            </div>
          )}
        </Section>
      </div>

      {/* Submit button - Confident and bold */}
      <div className="pt-6">
        <Button
          onClick={handleSubmit}
          size="lg"
          disabled={isSubmitting}
          className={cn(
            "w-full gap-3 text-base font-semibold",
            "bg-primary hover:bg-amber-dark text-primary-foreground",
            "shadow-lg hover:shadow-xl",
            "transition-all duration-300",
            "hover:scale-[1.02] active:scale-[0.98]",
            isSubmitting && "opacity-70 cursor-not-allowed"
          )}
        >
          {isSubmitting ? (
            <>
              <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent" />
              Processing...
            </>
          ) : (
            <>
              <Send className="h-5 w-5" />
              Submit Case to AI System
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
