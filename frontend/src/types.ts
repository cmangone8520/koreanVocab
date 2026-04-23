export type Level = "beginner" | "intermediate" | "advanced";
export type Mode = "written" | "listening" | "mixed";
export type QuestionType =
  | "kr_to_en_multiple_choice"
  | "en_to_kr_multiple_choice"
  | "kr_to_en_free_text"
  | "en_to_kr_free_text"
  | "listening_multiple_choice"
  | "listening_free_text";

export interface LevelSummary {
  level: Level;
  word_count: number;
  categories: string[];
}

export interface Question {
  id: number;
  position: number;
  question_type: QuestionType;
  prompt: string;
  options: string[] | null;
  audio_text: string | null;
  correct_answer: string | null;
  user_answer: string | null;
  is_correct: boolean | null;
}

export interface Test {
  id: number;
  created_at: string;
  completed_at: string | null;
  level: Level;
  mode: Mode;
  num_questions: number;
  score: number | null;
  total: number | null;
  questions: Question[];
}

export interface TestSummary {
  id: number;
  created_at: string;
  completed_at: string | null;
  level: Level;
  mode: Mode;
  num_questions: number;
  score: number | null;
  total: number | null;
}

export interface Health {
  status: string;
  openai_configured: boolean;
}
