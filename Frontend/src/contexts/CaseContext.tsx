import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { CaseData, getEmptyCaseData } from "@/types/case";
import { CaseService } from "@/services/api";
import { toast } from "sonner";

interface CaseContextValue {
  caseData: CaseData;
  updateCase: (partial: Partial<CaseData>) => void;
  saveDraft: () => void;
  loadExample: () => void;
  currentStep: number;
  setCurrentStep: (step: number) => void;
}

const CaseContext = createContext<CaseContextValue | null>(null);

const STORAGE_KEY = "legal-case-draft";

export function CaseProvider({ children }: { children: React.ReactNode }) {
  const [caseData, setCaseData] = useState<CaseData>(getEmptyCaseData());
  const [currentCaseId, setCurrentCaseId] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);

  // Load case or list cases on mount
  useEffect(() => {
    // For now, we'll just start fresh or maybe list cases in console to verify connection
    // In a real app, we'd check URL for case ID or load last active case
    console.log("CaseProvider mounted. API Base URL:", import.meta.env.VITE_API_URL);
  }, []);

  const updateCase = useCallback((partial: Partial<CaseData>) => {
    setCaseData((prev) => ({ ...prev, ...partial }));
  }, []);

  const saveDraft = useCallback(async () => {
    setIsLoading(true);
    try {
      if (currentCaseId) {
        // Update existing case
        await CaseService.updateCase(currentCaseId, caseData);
        toast.success("Case updated successfully");
      } else {
        // Create new case
        const result = await CaseService.createCase(caseData);
        if (result.success) {
          setCurrentCaseId(result.caseId);
          toast.success("Case created successfully");
        }
      }
    } catch (error) {
      console.error("Failed to save case:", error);
      toast.error("Failed to save to backend");
    } finally {
      setIsLoading(false);
    }
  }, [caseData, currentCaseId]);

  const loadExample = useCallback(() => {
    // Import the example data
    import('@/data/exampleCase.json').then((module) => {
      const exampleData = module.default as CaseData;
      setCaseData(exampleData);
      setCurrentStep(1);
      toast.success("Example case loaded successfully! Navigate through the steps to see all data.");
    }).catch((error) => {
      console.error("Failed to load example:", error);
      toast.error("Failed to load example case data");
    });
  }, []);

  return (
    <CaseContext.Provider value={{ caseData, updateCase, saveDraft, loadExample, currentStep, setCurrentStep }}>
      {children}
    </CaseContext.Provider>
  );
}

export function useCaseContext() {
  const ctx = useContext(CaseContext);
  if (!ctx) throw new Error("useCaseContext must be used within CaseProvider");
  return ctx;
}
