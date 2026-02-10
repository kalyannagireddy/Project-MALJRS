import { useCaseContext } from "@/contexts/CaseContext";
import { AI_OPTIONS } from "@/types/case";
import { Card } from "@/components/ui/card";
import { Bot, Scale, FileSearch, Users, Shield, FileText, MessageSquare } from "lucide-react";
import { cn } from "@/lib/utils";

const AI_OPTION_ICONS = {
  "Identify legal issues": Scale,
  "Find relevant precedents": FileSearch,
  "Prepare arguments": FileText,
  "Find weaknesses": Shield,
  "Draft court notes": FileText,
  "Prepare cross-questions": MessageSquare,
} as const;

export default function AIAssistancePage() {
  const { caseData, updateCase } = useCaseContext();

  const toggle = (option: string) => {
    const current = caseData.aiAssistance;
    const updated = current.includes(option) ? current.filter((o) => o !== option) : [...current, option];
    updateCase({ aiAssistance: updated });
  };

  return (
    <div className="space-y-7">
      {/* Page header */}
      <div className="flex items-center gap-4">
        <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-primary/10 border border-primary/20">
          <Bot className="h-6 w-6 text-primary" />
        </div>
        <div>
          <h2 className="text-3xl font-bold">AI Assistance Selection</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Choose the analysis and support you need from our AI system
          </p>
        </div>
      </div>

      {/* Selection grid */}
      <div className="grid gap-4 sm:grid-cols-2">
        {AI_OPTIONS.map((option) => {
          const isSelected = caseData.aiAssistance.includes(option);
          const Icon = AI_OPTION_ICONS[option as keyof typeof AI_OPTION_ICONS] || FileText;

          return (
            <button
              key={option}
              onClick={() => toggle(option)}
              className={cn(
                "relative p-5 rounded-lg border-2 text-left transition-all duration-200",
                "hover:shadow-md hover:scale-[1.02] active:scale-[0.98]",
                "glass-card group",
                isSelected
                  ? "border-primary bg-primary/5 shadow-sm"
                  : "border-border/60 hover:border-primary/40"
              )}
            >
              {/* Selection indicator */}
              <div className={cn(
                "absolute top-4 right-4 w-5 h-5 rounded-full border-2 transition-all duration-200",
                isSelected
                  ? "bg-primary border-primary"
                  : "border-border/60 group-hover:border-primary/40"
              )}>
                {isSelected && (
                  <div className="absolute inset-0 flex items-center justify-center text-primary-foreground">
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 12 12">
                      <path d="M10 3L4.5 8.5L2 6" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                )}
              </div>

              {/* Icon */}
              <div className={cn(
                "flex items-center justify-center w-10 h-10 rounded-lg mb-3 transition-all duration-200",
                isSelected
                  ? "bg-primary/15 text-primary"
                  : "bg-muted/60 text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary"
              )}>
                <Icon className="h-5 w-5" />
              </div>

              {/* Label */}
              <h3 className={cn(
                "font-semibold text-sm transition-colors duration-200",
                isSelected ? "text-foreground" : "text-foreground/90"
              )}>
                {option}
              </h3>
            </button>
          );
        })}
      </div>

      {/* Selection summary */}
      {caseData.aiAssistance.length > 0 && (
        <Card className="glass-card border-primary/20 bg-primary/5">
          <div className="p-5">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-1.5 h-1.5 rounded-full bg-primary" />
              <span className="text-sm font-medium text-foreground/90">
                {caseData.aiAssistance.length} {caseData.aiAssistance.length === 1 ? 'option' : 'options'} selected
              </span>
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed">
              The AI system will focus on: {caseData.aiAssistance.join(', ').toLowerCase()}
            </p>
          </div>
        </Card>
      )}
    </div>
  );
}
