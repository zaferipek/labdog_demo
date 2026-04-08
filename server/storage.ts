
import { db } from "./db";
import {
  projects,
  rawMaterials,
  experiments,
  testResults,
  materialEquivalents,
  settings,
  tasks,
  users,
  type InsertProject,
  type InsertRawMaterial,
  type InsertExperiment,
  type InsertTestResult,
  type InsertMaterialEquivalent,
  type InsertTask,
  type InsertUser,
  type UpdateProjectRequest,
  type UpdateTaskRequest,
  type UpdateRawMaterialRequest,
  type UpdateUserRequest,
} from "@shared/schema";
import { eq, desc, sql } from "drizzle-orm";

export interface IStorage {
  // Projects
  getProjects(): Promise<typeof projects.$inferSelect[]>;
  getProject(id: number): Promise<typeof projects.$inferSelect | undefined>;
  createProject(project: InsertProject): Promise<typeof projects.$inferSelect>;
  updateProject(id: number, updates: UpdateProjectRequest): Promise<typeof projects.$inferSelect>;
  deleteProject(id: number): Promise<void>;
  getProjectStats(): Promise<{ expertiseArea: string; count: number; projects: typeof projects.$inferSelect[] }[]>;

  // Materials
  getMaterials(): Promise<typeof rawMaterials.$inferSelect[]>;
  getMaterial(id: number): Promise<typeof rawMaterials.$inferSelect | undefined>;
  createMaterial(material: InsertRawMaterial): Promise<typeof rawMaterials.$inferSelect>;
  updateMaterial(id: number, updates: UpdateRawMaterialRequest): Promise<typeof rawMaterials.$inferSelect>;
  addMaterialEquivalent(relation: InsertMaterialEquivalent): Promise<typeof materialEquivalents.$inferSelect>;
  getMaterialEquivalents(materialId: number): Promise<typeof rawMaterials.$inferSelect[]>;

  // Experiments
  getExperimentsByProject(projectId: number): Promise<(typeof experiments.$inferSelect & { testResults: typeof testResults.$inferSelect[] })[]>;
  createExperiment(experiment: InsertExperiment): Promise<typeof experiments.$inferSelect>;
  createTestResult(result: InsertTestResult): Promise<typeof testResults.$inferSelect>;

  // Tasks
  getTasks(): Promise<typeof tasks.$inferSelect[]>;
  getTask(id: number): Promise<typeof tasks.$inferSelect | undefined>;
  createTask(task: InsertTask): Promise<typeof tasks.$inferSelect>;
  updateTask(id: number, updates: UpdateTaskRequest): Promise<typeof tasks.$inferSelect>;
  deleteTask(id: number): Promise<void>;

  // Users
  getUsers(): Promise<typeof users.$inferSelect[]>;
  getUserById(id: number): Promise<typeof users.$inferSelect | undefined>;
  getUserByUsername(username: string): Promise<typeof users.$inferSelect | undefined>;
  createUser(user: InsertUser): Promise<typeof users.$inferSelect>;
  updateUser(id: number, updates: UpdateUserRequest): Promise<typeof users.$inferSelect>;
  deleteUser(id: number): Promise<void>;

  // Settings
  getSetting(key: string): Promise<string | undefined>;
  setSetting(key: string, value: string): Promise<void>;
}

export class DatabaseStorage implements IStorage {
  // --- Projects ---
  async getProjects() {
    return await db.select().from(projects).orderBy(desc(projects.createdAt));
  }

  async getProject(id: number) {
    const [project] = await db.select().from(projects).where(eq(projects.id, id));
    return project;
  }

  async createProject(project: InsertProject) {
    const [newProject] = await db.insert(projects).values(project).returning();
    return newProject;
  }

  async updateProject(id: number, updates: UpdateProjectRequest) {
    const [updated] = await db
      .update(projects)
      .set(updates)
      .where(eq(projects.id, id))
      .returning();
    return updated;
  }

  async deleteProject(id: number) {
    await db.delete(projects).where(eq(projects.id, id));
  }

  async getProjectStats() {
    const allProjects = await db.select().from(projects);
    const statsMap = new Map<string, typeof projects.$inferSelect[]>();
    
    // Group by expertise area
    allProjects.forEach(p => {
      const area = p.expertiseArea;
      if (!statsMap.has(area)) {
        statsMap.set(area, []);
      }
      statsMap.get(area)?.push(p);
    });

    const result = [];
    for (const [area, projs] of statsMap.entries()) {
      result.push({
        expertiseArea: area,
        count: projs.length,
        projects: projs
      });
    }
    return result;
  }

  // --- Materials ---
  async getMaterials() {
    return await db.select().from(rawMaterials).orderBy(rawMaterials.name);
  }

  async getMaterial(id: number) {
    const [material] = await db.select().from(rawMaterials).where(eq(rawMaterials.id, id));
    return material;
  }

  async createMaterial(material: InsertRawMaterial) {
    const [newMaterial] = await db.insert(rawMaterials).values(material).returning();
    return newMaterial;
  }

  async updateMaterial(id: number, updates: UpdateRawMaterialRequest) {
    const [updated] = await db.update(rawMaterials).set(updates).where(eq(rawMaterials.id, id)).returning();
    return updated;
  }

  async addMaterialEquivalent(relation: InsertMaterialEquivalent) {
    const [newRelation] = await db.insert(materialEquivalents).values(relation).returning();
    return newRelation;
  }

  async getMaterialEquivalents(materialId: number) {
    // This is a bit complex with a self-referencing many-to-many.
    // We need to find rows where materialId is source OR target.
    
    // 1. Find equivalents where current material is source
    const asSource = await db.select({
      material: rawMaterials
    })
    .from(materialEquivalents)
    .innerJoin(rawMaterials, eq(materialEquivalents.equivalentId, rawMaterials.id))
    .where(eq(materialEquivalents.materialId, materialId));

    // 2. Find equivalents where current material is target (reverse link)
    const asTarget = await db.select({
      material: rawMaterials
    })
    .from(materialEquivalents)
    .innerJoin(rawMaterials, eq(materialEquivalents.materialId, rawMaterials.id))
    .where(eq(materialEquivalents.equivalentId, materialId));

    return [...asSource.map(r => r.material), ...asTarget.map(r => r.material)];
  }

  // --- Experiments ---
  async getExperimentsByProject(projectId: number) {
    const exps = await db.select().from(experiments).where(eq(experiments.projectId, projectId)).orderBy(desc(experiments.date));
    
    // Fetch results for each experiment (could be optimized with a join, but this is clear)
    const experimentsWithResults = await Promise.all(exps.map(async (exp) => {
      const results = await db.select().from(testResults).where(eq(testResults.experimentId, exp.id));
      return { ...exp, testResults: results };
    }));

    return experimentsWithResults;
  }

  async createExperiment(experiment: InsertExperiment) {
    const [newExperiment] = await db.insert(experiments).values(experiment).returning();
    return newExperiment;
  }

  async createTestResult(result: InsertTestResult) {
    const [newResult] = await db.insert(testResults).values(result).returning();
    return newResult;
  }

  // --- Tasks ---
  async getTasks() {
    return await db.select().from(tasks).orderBy(desc(tasks.createdAt));
  }

  async getTask(id: number) {
    const [task] = await db.select().from(tasks).where(eq(tasks.id, id));
    return task;
  }

  async createTask(task: InsertTask) {
    const [newTask] = await db.insert(tasks).values(task).returning();
    return newTask;
  }

  async updateTask(id: number, updates: UpdateTaskRequest) {
    const [updated] = await db.update(tasks).set(updates).where(eq(tasks.id, id)).returning();
    return updated;
  }

  async deleteTask(id: number) {
    await db.delete(tasks).where(eq(tasks.id, id));
  }

  // --- Users ---
  async getUsers() {
    return await db.select().from(users).orderBy(users.name);
  }

  async getUserById(id: number) {
    const [user] = await db.select().from(users).where(eq(users.id, id));
    return user;
  }

  async getUserByUsername(username: string) {
    const [user] = await db.select().from(users).where(eq(users.username, username));
    return user;
  }

  async createUser(user: InsertUser) {
    const [newUser] = await db.insert(users).values(user).returning();
    return newUser;
  }

  async updateUser(id: number, updates: UpdateUserRequest) {
    const [updated] = await db.update(users).set(updates).where(eq(users.id, id)).returning();
    return updated;
  }

  async deleteUser(id: number) {
    await db.delete(users).where(eq(users.id, id));
  }

  // --- Settings ---
  async getSetting(key: string) {
    const [setting] = await db.select().from(settings).where(eq(settings.key, key));
    return setting?.value;
  }

  async setSetting(key: string, value: string) {
    await db
      .insert(settings)
      .values({ key, value })
      .onConflictDoUpdate({
        target: settings.key,
        set: { value, updatedAt: new Date() },
      });
  }
}

export const storage = new DatabaseStorage();
