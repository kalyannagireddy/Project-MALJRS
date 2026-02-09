import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { useCaseContext } from "@/contexts/CaseContext";
import { STEPS } from "@/types/case";
import { Button } from "@/components/ui/button";
import { Save, Scale, ChevronLeft, ChevronRight, Menu } from "lucide-react";
import { cn } from "@/lib/utils";
import { useState, useEffect } from "react";

export default function CaseLayout() {
  const { caseData, saveDraft, currentStep, setCurrentStep } = useCaseContext();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    const step = STEPS.find((s) => s.path === location.pathname);
    if (step) setCurrentStep(step.number);
  }, [location.pathname, setCurrentStep]);

  const goToStep = (step: typeof STEPS[number]) => {
    navigate(step.path);
  };

  const canGoNext = currentStep < 10;
  const canGoPrev = currentStep > 1;

  return (
    <div className="flex min-h-screen w-full bg-background">
      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-30 flex flex-col border-r transition-all duration-200",
          sidebarOpen ? "w-60" : "w-0 overflow-hidden",
          "bg-[hsl(var(--sidebar-background))] text-[hsl(var(--sidebar-foreground))]"
        )}
      >
        <div className="flex items-center gap-2 px-4 py-5 border-b border-[hsl(var(--sidebar-border))]">
          <Scale className="h-5 w-5 text-[hsl(var(--sidebar-primary))]" />
          <span className="font-semibold text-sm tracking-wide text-[hsl(var(--sidebar-primary-foreground))]">
            Case Intelligence
          </span>
        </div>
        <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-0.5">
          {STEPS.map((step) => (
            <button
              key={step.number}
              onClick={() => goToStep(step)}
              className={cn(
                "flex items-center gap-3 w-full rounded-md px-3 py-2.5 text-sm transition-colors",
                currentStep === step.number
                  ? "bg-[hsl(var(--sidebar-accent))] text-[hsl(var(--sidebar-accent-foreground))] font-medium"
                  : "hover:bg-[hsl(var(--sidebar-accent))/50] text-[hsl(var(--sidebar-foreground))]"
              )}
            >
              <span
                className={cn(
                  "flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-semibold",
                  currentStep === step.number
                    ? "bg-[hsl(var(--sidebar-primary))] text-[hsl(var(--sidebar-primary-foreground))]"
                    : currentStep > step.number
                    ? "bg-[hsl(var(--sidebar-accent))] text-[hsl(var(--sidebar-accent-foreground))]"
                    : "border border-[hsl(var(--sidebar-border))] text-[hsl(var(--sidebar-foreground))]"
                )}
              >
                {step.number}
              </span>
              <span className="truncate">{step.title}</span>
            </button>
          ))}
        </nav>
      </aside>

      {/* Main area */}
      <div className={cn("flex-1 flex flex-col transition-all duration-200", sidebarOpen ? "ml-60" : "ml-0")}>
        {/* Header */}
        <header className="sticky top-0 z-20 flex items-center justify-between border-b bg-card px-4 py-3 shadow-sm">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(!sidebarOpen)}>
              <Menu className="h-4 w-4" />
            </Button>
            <div>
              <h1 className="text-lg font-semibold leading-tight">
                {caseData.caseTitle || "New Case"}
              </h1>
              <p className="text-xs text-muted-foreground">
                Step {currentStep} of {STEPS.length} — {STEPS[currentStep - 1]?.title}
              </p>
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={saveDraft} className="gap-1.5">
            <Save className="h-3.5 w-3.5" />
            Save Draft
          </Button>
        </header>

        {/* Progress bar */}
        <div className="bg-card border-b px-4 py-2">
          <div className="flex gap-1">
            {STEPS.map((step) => (
              <div
                key={step.number}
                className={cn(
                  "h-1.5 flex-1 rounded-full transition-colors",
                  step.number <= currentStep ? "bg-primary" : "bg-muted"
                )}
              />
            ))}
          </div>
        </div>

        {/* Content */}
        <main className="flex-1 p-6">
          <div className="mx-auto max-w-4xl">
            <Outlet />

            {/* Navigation buttons */}
            <div className="flex items-center justify-between mt-8 pt-6 border-t">
              <Button
                variant="outline"
                disabled={!canGoPrev}
                onClick={() => goToStep(STEPS[currentStep - 2])}
                className="gap-1.5"
              >
                <ChevronLeft className="h-4 w-4" /> Previous
              </Button>
              {canGoNext && (
                <Button onClick={() => goToStep(STEPS[currentStep])} className="gap-1.5">
                  Next <ChevronRight className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
