import { useCaseContext } from "@/contexts/CaseContext";
import { CASE_TYPES, CASE_STAGES } from "@/types/case";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Briefcase, FileText } from "lucide-react";

export default function CaseInfoPage() {
  const { caseData, updateCase, loadExample } = useCaseContext();

  return (
    <div className="space-y-7">
      {/* Page header */}
      <div className="flex items-center gap-4 justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-primary/10 border border-primary/20">
            <Briefcase className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h2 className="text-3xl font-bold">Case Basic Information</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Begin by providing essential details about your legal case
            </p>
          </div>
        </div>
        <Button
          onClick={loadExample}
          variant="outline"
          className="flex items-center gap-2"
        >
          <FileText className="h-4 w-4" />
          Load Example Case
        </Button>
      </div>

      {/* Main form card */}
      <Card className="glass-card">
        <CardHeader className="border-b border-border/50">
          <CardTitle className="text-lg font-semibold">General Details</CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="grid gap-6 sm:grid-cols-2">
            {/* Case Title - Full width */}
            <div className="sm:col-span-2 space-y-2">
              <Label htmlFor="caseTitle" className="text-sm font-medium">
                Case Title
                <span className="text-destructive ml-1">*</span>
              </Label>
              <Input
                id="caseTitle"
                placeholder="Enter a descriptive title for your case"
                value={caseData.caseTitle}
                onChange={(e) => updateCase({ caseTitle: e.target.value })}
                className="border-border/60 focus:border-primary focus:ring-primary transition-all duration-200"
              />
            </div>

            {/* Case Type */}
            <div className="space-y-2">
              <Label className="text-sm font-medium">
                Case Type
                <span className="text-destructive ml-1">*</span>
              </Label>
              <Select value={caseData.caseType} onValueChange={(v) => updateCase({ caseType: v })}>
                <SelectTrigger className="border-border/60 focus:border-primary focus:ring-primary">
                  <SelectValue placeholder="Select case type" />
                </SelectTrigger>
                <SelectContent>
                  {CASE_TYPES.map((t) => (
                    <SelectItem key={t} value={t}>{t}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Stage of Case */}
            <div className="space-y-2">
              <Label className="text-sm font-medium">
                Current Stage
                <span className="text-destructive ml-1">*</span>
              </Label>
              <Select value={caseData.stageOfCase} onValueChange={(v) => updateCase({ stageOfCase: v })}>
                <SelectTrigger className="border-border/60 focus:border-primary focus:ring-primary">
                  <SelectValue placeholder="Select stage" />
                </SelectTrigger>
                <SelectContent>
                  {CASE_STAGES.map((s) => (
                    <SelectItem key={s} value={s}>{s}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Court & Jurisdiction - Full width */}
            <div className="sm:col-span-2 space-y-2">
              <Label htmlFor="court" className="text-sm font-medium">
                Court & Jurisdiction
              </Label>
              <Input
                id="court"
                placeholder="e.g., High Court of Delhi, Supreme Court of India"
                value={caseData.courtJurisdiction}
                onChange={(e) => updateCase({ courtJurisdiction: e.target.value })}
                className="border-border/60 focus:border-primary focus:ring-primary transition-all duration-200"
              />
            </div>

            {/* Parties section with visual separation */}
            <div className="sm:col-span-2 pt-4 border-t border-border/30">
              <h3 className="text-base font-semibold mb-4">Parties Involved</h3>
            </div>

            {/* Plaintiff */}
            <div className="space-y-2">
              <Label htmlFor="plaintiff" className="text-sm font-medium">
                Plaintiff / Complainant
              </Label>
              <Input
                id="plaintiff"
                placeholder="Full name"
                value={caseData.plaintiffName}
                onChange={(e) => updateCase({ plaintiffName: e.target.value })}
                className="border-border/60 focus:border-primary focus:ring-primary transition-all duration-200"
              />
            </div>

            {/* Defendant */}
            <div className="space-y-2">
              <Label htmlFor="defendant" className="text-sm font-medium">
                Defendant / Respondent
              </Label>
              <Input
                id="defendant"
                placeholder="Full name"
                value={caseData.defendantName}
                onChange={(e) => updateCase({ defendantName: e.target.value })}
                className="border-border/60 focus:border-primary focus:ring-primary transition-all duration-200"
              />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
