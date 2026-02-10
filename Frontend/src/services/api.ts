import axios from 'axios';
import { CaseData, StoredCase } from '@/types/case';

// Create axios instance with default config
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Case Service
export const CaseService = {
    // Create a new case
    createCase: async (data: CaseData): Promise<{ success: boolean; caseId: string; message: string }> => {
        const response = await api.post('/cases', { data });
        return response.data;
    },

    // Get a case by ID
    getCase: async (caseId: string): Promise<StoredCase> => {
        const response = await api.get(`/cases/${caseId}`);
        return response.data;
    },

    // Update a case
    updateCase: async (caseId: string, data: Partial<CaseData>): Promise<{ success: boolean; caseId: string; message: string }> => {
        const response = await api.put(`/cases/${caseId}`, { data });
        return response.data;
    },

    // Delete a case
    deleteCase: async (caseId: string): Promise<{ success: boolean; message: string }> => {
        const response = await api.delete(`/cases/${caseId}`);
        return response.data;
    },

    // List all cases
    listCases: async (): Promise<string[]> => {
        const response = await api.get('/cases');
        return response.data;
    },

    // AI Processing
    identifyIssues: async (caseData: CaseData): Promise<{ success: boolean; issues: string[]; confidence: number }> => {
        const response = await api.post('/ai/identify-issues', { caseData, options: ["Identify legal issues"] });
        return response.data;
    },

    processCase: async (caseData: CaseData, options: string[]): Promise<{ success: boolean; caseId: string; report: any }> => {
        const response = await api.post('/ai/process', { caseData, options });
        return response.data;
    },
};

export default api;
