import { useCaseContext } from "@/contexts/CaseContext";
import { STEPS } from "@/types/case";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";
import { CheckCircle, Edit, Send } from "lucide-react";
import { toast } from "sonner";

export default function ReviewPage() {
  const { caseData } = useCaseContext();
  const navigate = useNavigate();

  const handleSubmit = () => {
    const json = JSON.stringify(caseData, null, 2);
    console.log("Case Data JSON:", json);
    toast.success("Case submitted to AI system!", { description: "Your case data has been exported." });
  };

  const Section = ({ title, stepIndex, children }: { title: string; stepIndex: number; children: React.ReactNode }) => (
    <Card>
      <CardHeader className="flex-row items-center justify-between pb-3">
        <CardTitle className="text-base">{title}</CardTitle>
        <Button variant="ghost" size="sm" onClick={() => navigate(STEPS[stepIndex].path)} className="gap-1 text-xs">
          <Edit className="h-3 w-3" /> Edit
        </Button>
      </CardHeader>
      <CardContent className="text-sm space-y-1">{children}</CardContent>
    </Card>
  );

  const Field = ({ label, value }: { label: string; value: string }) => (
    <div className="flex gap-2">
      <span className="text-muted-foreground min-w-[140px]">{label}:</span>
      <span className="font-medium">{value || "—"}</span>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <CheckCircle className="h-6 w-6 text-primary" />
        <h2 className="text-2xl font-bold">Review & Submit</h2>
      </div>

      <Section title="Case Basic Information" stepIndex={0}>
        <Field label="Case Title" value={caseData.caseTitle} />
        <Field label="Case Type" value={caseData.caseType} />
        <Field label="Court" value={caseData.courtJurisdiction} />
        <Field label="Stage" value={caseData.stageOfCase} />
        <Field label="Plaintiff" value={caseData.plaintiffName} />
        <Field label="Defendant" value={caseData.defendantName} />
      </Section>

      <Section title="Timeline" stepIndex={1}>
        {caseData.timeline.length === 0 ? <p className="text-muted-foreground">No events added.</p> :
          caseData.timeline.map((e) => (
            <div key={e.id} className="flex gap-2">
              <span className="text-muted-foreground">{e.date || "No date"}</span>
              <span>— {e.description || "No description"}</span>
              {e.proofAvailable && <Badge variant="secondary" className="text-xs">Proof</Badge>}
            </div>
          ))}
      </Section>

      <Section title="Claims" stepIndex={2}>
        {caseData.claims.length === 0 ? <p className="text-muted-foreground">No claims added.</p> :
          <ul className="list-disc list-inside space-y-1">{caseData.claims.map((c, i) => <li key={i}>{c || "—"}</li>)}</ul>}
        {caseData.reliefRequested && <div className="mt-2"><span className="text-muted-foreground">Relief: </span>{caseData.reliefRequested}</div>}
      </Section>

      <Section title="Evidence" stepIndex={3}>
        {caseData.evidence.length === 0 ? <p className="text-muted-foreground">No evidence added.</p> :
          caseData.evidence.map((e) => (
            <div key={e.id} className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs">{e.type}</Badge>
              <span>{e.description || e.fileName || "Untitled"}</span>
              <Badge variant="secondary" className="text-xs">{e.strength}</Badge>
            </div>
          ))}
      </Section>

      <Section title="Legal Issues" stepIndex={4}>
        {caseData.legalIssues.length === 0 ? <p className="text-muted-foreground">No issues added.</p> :
          <ul className="list-disc list-inside space-y-1">{caseData.legalIssues.map((i, idx) => <li key={idx}>{i || "—"}</li>)}</ul>}
      </Section>

      <Section title="Laws & Sections" stepIndex={5}>
        {caseData.lawSections.length === 0 ? <p className="text-muted-foreground">No laws added.</p> :
          caseData.lawSections.map((s) => (
            <div key={s.id}><span className="font-medium">{s.actName}</span> {s.sectionNumber && `— ${s.sectionNumber}`} {s.description && `(${s.description})`}</div>
          ))}
      </Section>

      <Section title="Strengths & Weaknesses" stepIndex={6}>
        <Field label="Strengths" value={caseData.strengths} />
        <Field label="Weaknesses" value={caseData.weaknesses} />
      </Section>

      <Section title="Witnesses" stepIndex={7}>
        {caseData.witnesses.length === 0 ? <p className="text-muted-foreground">No witnesses added.</p> :
          caseData.witnesses.map((w) => <div key={w.id}><span className="font-medium">{w.name}</span> — {w.knowledge}</div>)}
      </Section>

      <Section title="AI Assistance" stepIndex={8}>
        {caseData.aiAssistance.length === 0 ? <p className="text-muted-foreground">No options selected.</p> :
          <div className="flex flex-wrap gap-2">{caseData.aiAssistance.map((a) => <Badge key={a}>{a}</Badge>)}</div>}
      </Section>

      <div className="pt-4">
        <Button onClick={handleSubmit} size="lg" className="w-full gap-2">
          <Send className="h-4 w-4" /> Submit Case to AI System
        </Button>
      </div>
    </div>
  );
}
