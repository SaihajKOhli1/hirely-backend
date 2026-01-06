export interface SectionAnalysis {
    name: string;
    score: number;
    feedback: string[];
    text: string;
    strengths: string[];
   }
   
   
   export interface Metrics {
    clarity: number;
    impact: number;
    professionalism: number;
   }
   
   
   export interface AnalysisResult {
    overallScore: number;
    sections: SectionAnalysis[];
    metrics: Metrics;
   }
   
   
   export type AnalysisStatus = 'idle' | 'analyzing' | 'success' | 'error';
   
   
   export interface AnalysisState {
    status: AnalysisStatus;
    result: AnalysisResult | null;
    error: string | null;
   }
   
   
   
   
   
   