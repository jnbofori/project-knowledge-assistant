export type ProjectRole = 'owner' | 'admin' | 'member' | 'viewer';

export type DocumentStatus = 'pending' | 'processing' | 'ready' | 'failed';

export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface UserRegister {
  email: string;
  password: string;
}

export interface Project {
  id: string;
  name: string;
  description: string | null;
  created_by: string;
  created_at: string;
  current_user_role: ProjectRole;
}

export interface ProjectCreate {
  name: string;
  description?: string | null;
}

export interface ProjectMember {
  id: string;
  user_id: string;
  email: string;
  role: ProjectRole;
  created_at: string;
}

export interface ProjectMemberCreate {
  email: string;
  role: ProjectRole;
}

export interface Document {
  id: string;
  project_id: string;
  filename: string;
  status: DocumentStatus;
  uploaded_by: string;
  chunk_count: number;
  error_message: string | null;
  created_at: string;
}

export interface SourceCitation {
  document_id: string | null;
  filename: string | null;
  text: string;
  score: number | null;
}

export interface Query {
  id: string;
  question: string;
  answer: string;
  sources: SourceCitation[];
  created_at: string;
}

export interface QueryCreate {
  question: string;
}

export const ROLE_RANK: Record<ProjectRole, number> = {
  viewer: 0,
  member: 1,
  admin: 2,
  owner: 3
};

export const SUPPORTED_EXTENSIONS = ['.txt', '.md', '.pdf', '.docx'];
