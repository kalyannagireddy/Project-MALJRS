import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { CaseData, getEmptyCaseData } from "@/types/case";
import { toast } from "sonner";

interface CaseContextValue {
  caseData: CaseData;
  updateCase: (partial: Partial<CaseData>) => void;
  saveDraft: () => void;
  currentStep: number;
  setCurrentStep: (step: number) => void;
}

const CaseContext = createContext<CaseContextValue | null>(null);

const STORAGE_KEY = "legal-case-draft";

export function CaseProvider({ children }: { children: React.ReactNode }) {
  const [caseData, setCaseData] = useState<CaseData>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? { ...getEmptyCaseData(), ...JSON.parse(saved) } : getEmptyCaseData();
    } catch {
      return getEmptyCaseData();
    }
  });
  const [currentStep, setCurrentStep] = useState(1);

  const updateCase = useCallback((partial: Partial<CaseData>) => {
    setCaseData((prev) => ({ ...prev, ...partial }));
  }, []);

  const saveDraft = useCallback(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(caseData));
    toast.success("Draft saved successfully");
  }, [caseData]);

  return (
    <CaseContext.Provider value={{ caseData, updateCase, saveDraft, currentStep, setCurrentStep }}>
      {children}
    </CaseContext.Provider>
  );
}

export function useCaseContext() {
  const ctx = useContext(CaseContext);
  if (!ctx) throw new Error("useCaseContext must be used within CaseProvider");
  return ctx;
}
