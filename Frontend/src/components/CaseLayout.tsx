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
    <div className="flex min-h-screen w-full">
      {/* Sidebar - Deep charcoal with subtle pattern */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-30 flex flex-col border-r transition-all duration-300",
          sidebarOpen ? "w-64" : "w-0 overflow-hidden",
          "bg-[hsl(var(--sidebar-background))] text-[hsl(var(--sidebar-foreground))]",
          "border-[hsl(var(--sidebar-border))]"
        )}
        style={{
          backgroundImage: `
            linear-gradient(135deg, hsl(var(--sidebar-background)) 0%, hsl(var(--sidebar-accent)) 100%),
            url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.02'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")
          `,
          backgroundBlendMode: 'normal, overlay',
        }}
      >
        {/* Logo header */}
        <div className="flex items-center gap-3 px-5 py-6 border-b border-[hsl(var(--sidebar-border))]">
          <div className="flex items-center justify-center w-8 h-8 rounded bg-[hsl(var(--sidebar-primary))]">
            <Scale className="h-5 w-5 text-[hsl(var(--sidebar-primary-foreground))]" />
          </div>
          <div className="flex flex-col">
            <span className="font-semibold text-sm tracking-tight text-[hsl(var(--sidebar-primary-foreground))]">
              MALJRS
            </span>
            <span className="text-xs text-[hsl(var(--sidebar-foreground))] opacity-70">
              Case Intelligence
            </span>
          </div>
        </div>

        {/* Step navigation */}
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {STEPS.map((step) => {
            const isActive = currentStep === step.number;
            const isCompleted = currentStep > step.number;
            
            return (
              <button
                key={step.number}
                onClick={() => goToStep(step)}
                className={cn(
                  "flex items-center gap-3 w-full rounded-md px-3 py-3 text-sm transition-all duration-200",
                  "border border-transparent",
                  isActive
                    ? "bg-[hsl(var(--sidebar-accent))] text-[hsl(var(--sidebar-accent-foreground))] font-medium border-[hsl(var(--sidebar-primary))/20]"
                    : "hover:bg-[hsl(var(--sidebar-accent))/60] text-[hsl(var(--sidebar-foreground))]"
                )}
              >
                <span
                  className={cn(
                    "flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-semibold transition-all duration-200",
                    isActive
                      ? "bg-[hsl(var(--sidebar-primary))] text-[hsl(var(--sidebar-primary-foreground))] scale-110"
                      : isCompleted
                      ? "bg-[hsl(var(--sidebar-accent))] text-[hsl(var(--sidebar-accent-foreground))] border border-[hsl(var(--sidebar-border))]"
                      : "border-2 border-[hsl(var(--sidebar-border))] text-[hsl(var(--sidebar-foreground))]"
                  )}
                >
                  {step.number}
                </span>
                <span className="truncate text-left">{step.title}</span>
              </button>
            );
          })}
        </nav>
      </aside>

      {/* Main content area */}
      <div className={cn("flex-1 flex flex-col transition-all duration-300", sidebarOpen ? "ml-64" : "ml-0")}>
        {/* Header - Frosted glass effect */}
        <header className="sticky top-0 z-20 flex items-center justify-between border-b backdrop-blur-md bg-card/80 px-5 py-4 shadow-sm border-border/50">
          <div className="flex items-center gap-4">
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="hover:bg-accent/10"
            >
              <Menu className="h-5 w-5" />
            </Button>
            <div>
              <h1 className="text-xl font-semibold leading-tight">
                {caseData.caseTitle || "New Legal Case"}
              </h1>
              <p className="text-xs text-muted-foreground mt-0.5 mono">
                Step {currentStep} of {STEPS.length} · {STEPS[currentStep - 1]?.title}
              </p>
            </div>
          </div>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={saveDraft} 
            className="gap-2 border-border/60 hover:bg-accent/10 hover:border-amber transition-all duration-200"
          >
            <Save className="h-3.5 w-3.5" />
            Save Draft
          </Button>
        </header>

        {/* Progress indicator - Bolder design */}
        <div className="bg-card/60 border-b border-border/50 px-5 py-3 backdrop-blur-sm">
          <div className="flex gap-1.5">
            {STEPS.map((step) => (
              <div
                key={step.number}
                className={cn(
                  "h-2 flex-1 rounded-full transition-all duration-500",
                  step.number <= currentStep 
                    ? "bg-gradient-to-r from-amber via-amber to-amber-dark shadow-sm" 
                    : "bg-muted/60"
                )}
              />
            ))}
          </div>
        </div>

        {/* Page content */}
        <main className="flex-1 p-6">
          <div className="mx-auto max-w-4xl">
            <Outlet />

            {/* Navigation buttons */}
            <div className="flex items-center justify-between mt-10 pt-6 border-t border-border/50">
              <Button
                variant="outline"
                disabled={!canGoPrev}
                onClick={() => goToStep(STEPS[currentStep - 2])}
                className="gap-2 border-border/60 hover:bg-accent/10 transition-all duration-200"
              >
                <ChevronLeft className="h-4 w-4" />
                Previous
              </Button>
              {canGoNext && (
                <Button 
                  onClick={() => goToStep(STEPS[currentStep])} 
                  className="gap-2 bg-primary hover:bg-amber-dark text-primary-foreground transition-all duration-200"
                >
                  Next
                  <ChevronRight className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
