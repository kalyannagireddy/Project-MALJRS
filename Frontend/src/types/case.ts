export interface TimelineEvent {
  id: string;
  date: string;
  description: string;
  peopleInvolved: string;
  proofAvailable: boolean;
}

export interface EvidenceItem {
  id: string;
  fileName: string;
  description: string;
  linkedTimelineEventId: string;
  strength: "Strong" | "Medium" | "Weak";
  type: "Document" | "Witness" | "Audio" | "Video" | "Digital";
}

export interface LawSection {
  id: string;
  actName: string;
  sectionNumber: string;
  description: string;
}

export interface WitnessInfo {
  id: string;
  name: string;
  knowledge: string;
  linkedTimelineEventId: string;
}

export interface CaseData {
  // Page 1
  caseTitle: string;
  caseType: string;
  courtJurisdiction: string;
  stageOfCase: string;
  plaintiffName: string;
  defendantName: string;
  // Page 2
  timeline: TimelineEvent[];
  // Page 3
  claims: string[];
  reliefRequested: string;
  // Page 4
  evidence: EvidenceItem[];
  // Page 5
  legalIssues: string[];
  // Page 6
  lawSections: LawSection[];
  // Page 7
  strengths: string;
  weaknesses: string;
  // Page 8
  witnesses: WitnessInfo[];
  // Page 9
  aiAssistance: string[];
}

export const CASE_TYPES = ["Civil", "Criminal", "Contract", "Property", "Family", "IPC", "Other"];
export const CASE_STAGES = ["Notice", "Filed", "Evidence", "Trial", "Appeal"];
export const EVIDENCE_STRENGTHS = ["Strong", "Medium", "Weak"] as const;
export const EVIDENCE_TYPES = ["Document", "Witness", "Audio", "Video", "Digital"] as const;
export const AI_OPTIONS = [
  "Identify legal issues",
  "Find relevant precedents",
  "Prepare arguments",
  "Find weaknesses",
  "Draft court notes",
  "Prepare cross-questions",
];

export const STEPS = [
  { number: 1, title: "Case Info", path: "/case-info" },
  { number: 2, title: "Timeline", path: "/timeline" },
  { number: 3, title: "Claims", path: "/claims" },
  { number: 4, title: "Evidence", path: "/evidence" },
  { number: 5, title: "Legal Issues", path: "/legal-issues" },
  { number: 6, title: "Laws & Sections", path: "/laws" },
  { number: 7, title: "Strengths & Weaknesses", path: "/strengths-weaknesses" },
  { number: 8, title: "Witnesses", path: "/witnesses" },
  { number: 9, title: "AI Assistance", path: "/ai-assistance" },
  { number: 10, title: "Review & Submit", path: "/review" },
];

export function getEmptyCaseData(): CaseData {
  return {
    caseTitle: "",
    caseType: "",
    courtJurisdiction: "",
    stageOfCase: "",
    plaintiffName: "",
    defendantName: "",
    timeline: [],
    claims: [],
    reliefRequested: "",
    evidence: [],
    legalIssues: [],
    lawSections: [],
    strengths: "",
    weaknesses: "",
    witnesses: [],
    aiAssistance: [],
  };
}
