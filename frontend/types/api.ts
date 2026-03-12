export type User = {
  id: number;
  email: string;
  created_at: string;
  updated_at: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

export type ResumeSummary = {
  summary: string;
  technical_stack: string[];
  seniority: string;
  project_themes: string[];
  domains: string[];
  strengths: string[];
  evidence_notes: string[];
  resume_improvement_suggestions: string[];
};

export type Strategy = {
  target_role: string;
  interview_style: string;
  focus_areas: string[];
  emphasis: string[];
  fallback_used: boolean;
  difficulty_distribution: Record<string, number>;
  interview_tone: string;
};

export type AnswerFeedback = {
  id: number;
  score_json: {
    overall: number;
    relevance: number;
    clarity: number;
    technical_depth: number;
  };
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  improved_answer: string;
  created_at: string;
  updated_at: string;
};

export type UserAnswer = {
  id: number;
  question_id: number;
  answer_text: string;
  created_at: string;
  updated_at: string;
  feedback: AnswerFeedback | null;
};

export type QuestionItem = {
  id: number;
  difficulty: string;
  category: string;
  question: string;
  answer: string;
  intent: string;
  reference_from_resume: string;
  is_favorited: boolean;
  my_answer: UserAnswer | null;
  created_at: string;
};

export type InterviewSetListItem = {
  id: number;
  title: string;
  created_at: string;
  resume_session_id: number;
  resume_summary: ResumeSummary;
  total_question_count: number;
  difficulty_breakdown: Record<string, number>;
  target_role: string;
  interview_style: string;
  extraction_quality_score: number | null;
};

export type InterviewSetDetail = {
  id: number;
  title: string;
  created_at: string;
  resume_session_id: number;
  meta_json: Record<string, unknown>;
  job_description_text: string | null;
  resume_summary: ResumeSummary;
  strategy: Strategy;
  total_question_count: number;
  difficulty_breakdown: Record<string, number>;
  target_role: string;
  interview_style: string;
  extraction_status: string;
  extraction_quality_score: number | null;
  extraction_error_message: string | null;
  assessment: {
    answered_count: number;
    scored_count: number;
    average_overall_score: number;
    pass_rate: number;
  };
  questions: QuestionItem[];
};

export type PaginatedInterviewSets = {
  items: InterviewSetListItem[];
  total: number;
  page: number;
  page_size: number;
};

export type FavoriteItem = {
  favorite_id: number;
  favorited_at: string;
  question_id: number;
  difficulty: string;
  category: string;
  question: string;
  answer: string;
  intent: string;
  reference_from_resume: string;
  source_question_set_id: number;
  source_question_set_title: string;
};
