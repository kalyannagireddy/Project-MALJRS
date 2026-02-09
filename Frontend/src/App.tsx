import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { CaseProvider } from "@/contexts/CaseContext";
import CaseLayout from "@/components/CaseLayout";
import CaseInfoPage from "@/pages/CaseInfoPage";
import TimelinePage from "@/pages/TimelinePage";
import ClaimsPage from "@/pages/ClaimsPage";
import EvidencePage from "@/pages/EvidencePage";
import LegalIssuesPage from "@/pages/LegalIssuesPage";
import LawsPage from "@/pages/LawsPage";
import StrengthsWeaknessesPage from "@/pages/StrengthsWeaknessesPage";
import WitnessesPage from "@/pages/WitnessesPage";
import AIAssistancePage from "@/pages/AIAssistancePage";
import ReviewPage from "@/pages/ReviewPage";
import NotFound from "@/pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <CaseProvider>
          <Routes>
            <Route path="/" element={<Navigate to="/case-info" replace />} />
            <Route element={<CaseLayout />}>
              <Route path="/case-info" element={<CaseInfoPage />} />
              <Route path="/timeline" element={<TimelinePage />} />
              <Route path="/claims" element={<ClaimsPage />} />
              <Route path="/evidence" element={<EvidencePage />} />
              <Route path="/legal-issues" element={<LegalIssuesPage />} />
              <Route path="/laws" element={<LawsPage />} />
              <Route path="/strengths-weaknesses" element={<StrengthsWeaknessesPage />} />
              <Route path="/witnesses" element={<WitnessesPage />} />
              <Route path="/ai-assistance" element={<AIAssistancePage />} />
              <Route path="/review" element={<ReviewPage />} />
            </Route>
            <Route path="*" element={<NotFound />} />
          </Routes>
        </CaseProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
