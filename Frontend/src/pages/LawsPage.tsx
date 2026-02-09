import { useCaseContext } from "@/contexts/CaseContext";
import { LawSection } from "@/types/case";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Plus, Trash2, BookOpen } from "lucide-react";

export default function LawsPage() {
  const { caseData, updateCase } = useCaseContext();

  const addSection = () => {
    const item: LawSection = { id: crypto.randomUUID(), actName: "", sectionNumber: "", description: "" };
    updateCase({ lawSections: [...caseData.lawSections, item] });
  };

  const updateSection = (id: string, partial: Partial<LawSection>) => {
    updateCase({ lawSections: caseData.lawSections.map((s) => (s.id === id ? { ...s, ...partial } : s)) });
  };

  const removeSection = (id: string) => {
    updateCase({ lawSections: caseData.lawSections.filter((s) => s.id !== id) });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <BookOpen className="h-6 w-6 text-primary" />
          <h2 className="text-2xl font-bold">Known Laws & Sections</h2>
        </div>
        <Button onClick={addSection} size="sm" className="gap-1.5"><Plus className="h-4 w-4" /> Add Section</Button>
      </div>
      <p className="text-sm text-muted-foreground">Optional — add any laws, acts, or sections you believe are relevant.</p>

      {caseData.lawSections.length === 0 && (
        <Card><CardContent className="text-center py-12 text-muted-foreground">No laws or sections added yet.</CardContent></Card>
      )}

      {caseData.lawSections.map((section) => (
        <Card key={section.id}>
          <CardContent className="pt-5 space-y-3">
            <div className="flex items-start justify-between">
              <div className="grid gap-3 sm:grid-cols-3 flex-1">
                <div className="space-y-1.5">
                  <Label className="text-xs">Act Name</Label>
                  <Input placeholder="e.g. Indian Penal Code" value={section.actName} onChange={(e) => updateSection(section.id, { actName: e.target.value })} />
                </div>
                <div className="space-y-1.5">
                  <Label className="text-xs">Section Number</Label>
                  <Input placeholder="e.g. Section 420" value={section.sectionNumber} onChange={(e) => updateSection(section.id, { sectionNumber: e.target.value })} />
                </div>
                <div className="space-y-1.5">
                  <Label className="text-xs">Description</Label>
                  <Input placeholder="Optional" value={section.description} onChange={(e) => updateSection(section.id, { description: e.target.value })} />
                </div>
              </div>
              <Button variant="ghost" size="icon" className="ml-2 mt-5" onClick={() => removeSection(section.id)}>
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
