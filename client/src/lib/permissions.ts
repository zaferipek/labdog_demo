import type { User, Project } from "@shared/schema";

type AuthUser = {
  id: number;
  username: string;
  name: string;
  role: string;
  expertiseGroup: string;
};

const ADMIN_ROLES = ["Admin"];
const MANAGER_ROLES = ["Admin", "Yönetici"];
const WRITE_ROLES = ["Admin", "Yönetici", "Ar-Ge Mühendisi", "Ar-Ge Uzmanı", "Tekniker", "Kalite Kontrol"];
const READONLY_ROLES = ["Gözlemci", "Satın Alma"];

export function isOwnExpertise(user: AuthUser, expertiseArea: string): boolean {
  return user.expertiseGroup === expertiseArea;
}

export function canCreateProject(user: AuthUser): boolean {
  return WRITE_ROLES.includes(user.role);
}

export function canEditProject(user: AuthUser, project?: { expertiseArea: string }): boolean {
  if (user.role === "Admin") return true;
  if (READONLY_ROLES.includes(user.role)) return false;
  if (!project) return true;
  return isOwnExpertise(user, project.expertiseArea);
}

export function canDeleteProject(user: AuthUser): boolean {
  return MANAGER_ROLES.includes(user.role);
}

export function canCreateExperiment(user: AuthUser, project?: { expertiseArea: string }): boolean {
  if (user.role === "Admin") return true;
  if (READONLY_ROLES.includes(user.role)) return false;
  if (!project) return WRITE_ROLES.includes(user.role);
  return WRITE_ROLES.includes(user.role) && isOwnExpertise(user, project.expertiseArea);
}

export function canCreateTask(user: AuthUser): boolean {
  return WRITE_ROLES.includes(user.role);
}

export function canDeleteTask(user: AuthUser): boolean {
  return MANAGER_ROLES.includes(user.role);
}

export function canManageUsers(user: AuthUser): boolean {
  return user.role === "Admin";
}

export function canAccessSettings(user: AuthUser): boolean {
  return user.role === "Admin";
}

export function canCreateMaterial(user: AuthUser): boolean {
  return [...WRITE_ROLES, "Satın Alma"].includes(user.role);
}

export const roleLabels: Record<string, string> = {
  "Admin": "Admin",
  "Yönetici": "Yönetici",
  "Ar-Ge Mühendisi": "Ar-Ge Mühendisi",
  "Ar-Ge Uzmanı": "Ar-Ge Uzmanı",
  "Tekniker": "Tekniker",
  "Kalite Kontrol": "Kalite Kontrol",
  "Satın Alma": "Satın Alma",
  "Gözlemci": "Gözlemci",
};
