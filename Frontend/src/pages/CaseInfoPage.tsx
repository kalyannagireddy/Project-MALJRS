import { useCaseContext } from "@/contexts/CaseContext";
import { CASE_TYPES, CASE_STAGES } from "@/types/case";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Briefcase } from "lucide-react";

export default function CaseInfoPage() {
  const { caseData, updateCase } = useCaseContext();

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Briefcase className="h-6 w-6 text-primary" />
        <h2 className="text-2xl font-bold">Case Basic Information</h2>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">General Details</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-5 sm:grid-cols-2">
          <div className="sm:col-span-2 space-y-1.5">
            <Label htmlFor="caseTitle">Case Title</Label>
            <Input id="caseTitle" placeholder="Enter case title" value={caseData.caseTitle} onChange={(e) => updateCase({ caseTitle: e.target.value })} />
          </div>
          <div className="space-y-1.5">
            <Label>Case Type</Label>
            <Select value={caseData.caseType} onValueChange={(v) => updateCase({ caseType: v })}>
              <SelectTrigger><SelectValue placeholder="Select type" /></SelectTrigger>
              <SelectContent>{CASE_TYPES.map((t) => <SelectItem key={t} value={t}>{t}</SelectItem>)}</SelectContent>
            </Select>
          </div>
          <div className="space-y-1.5">
            <Label>Stage of Case</Label>
            <Select value={caseData.stageOfCase} onValueChange={(v) => updateCase({ stageOfCase: v })}>
              <SelectTrigger><SelectValue placeholder="Select stage" /></SelectTrigger>
              <SelectContent>{CASE_STAGES.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}</SelectContent>
            </Select>
          </div>
          <div className="sm:col-span-2 space-y-1.5">
            <Label htmlFor="court">Court & Jurisdiction</Label>
            <Input id="court" placeholder="e.g. High Court of Delhi" value={caseData.courtJurisdiction} onChange={(e) => updateCase({ courtJurisdiction: e.target.value })} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="plaintiff">Plaintiff / Complainant</Label>
            <Input id="plaintiff" placeholder="Name" value={caseData.plaintiffName} onChange={(e) => updateCase({ plaintiffName: e.target.value })} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="defendant">Defendant / Respondent</Label>
            <Input id="defendant" placeholder="Name" value={caseData.defendantName} onChange={(e) => updateCase({ defendantName: e.target.value })} />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
