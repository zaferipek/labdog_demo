
import { pgTable, text, serial, integer, boolean, timestamp, numeric, date } from "drizzle-orm/pg-core";
import { relations } from "drizzle-orm";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// === ENUMS ===
export const expertiseAreas = [
  "Boya/Finish",
  "Hot Melt",
  "Mürekkep",
  "PUD",
  "PU"
] as const;

export const projectStatuses = [
  "Fikir",
  "Literatür Taraması",
  "Laboratuvar Testleri",
  "Pilot",
  "Tamamlandı"
] as const;

export const materialApprovalStatuses = [
  "Onaylı",
  "Onaysız",
  "Testte",
  "Yolda"
] as const;

export const taskStatuses = [
  "Beklemede",
  "Devam Ediyor",
  "Tamamlandı",
  "İptal"
] as const;

export const taskPriorities = [
  "Düşük",
  "Orta",
  "Yüksek",
  "Acil"
] as const;

export const userRoles = [
  "Admin",
  "Yönetici",
  "Ar-Ge Mühendisi",
  "Ar-Ge Uzmanı",
  "Tekniker",
  "Kalite Kontrol",
  "Satın Alma",
  "Gözlemci"
] as const;

// === TABLE DEFINITIONS ===

// Projects (Salesforce 'Opportunity' Logic)
export const projects = pgTable("projects", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  expertiseArea: text("expertise_area", { enum: expertiseAreas }).notNull(),
  rdSpecialist: text("rd_specialist").notNull(),
  startDate: date("start_date").defaultNow().notNull(),
  targetDate: date("target_date"),
  status: text("status", { enum: projectStatuses }).default("Fikir").notNull(),
  description: text("description"),
  createdAt: timestamp("created_at").defaultNow(),
});

// Raw Materials
export const rawMaterials = pgTable("raw_materials", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  supplier: text("supplier").notNull(),
  brand: text("brand"),
  function: text("function").notNull(),
  casNumber: text("cas_number"),
  stockQuantity: numeric("stock_quantity").default("0"),
  unit: text("unit").default("kg"),
  arrivalDate: date("arrival_date"),
  approvalStatus: text("approval_status", { enum: materialApprovalStatuses }).default("Onaysız").notNull(),
  safetyDataSheetUrl: text("sds_url"),
  tdsUrl: text("tds_url"),
  notes: text("notes"),
  createdAt: timestamp("created_at").defaultNow(),
});

// Material Equivalents (Many-to-Many self reference or simple link)
// For simplicity in this MVP, we'll store direct 1-to-1 or use a mapping table if complex.
// Let's use a mapping table for flexibility.
export const materialEquivalents = pgTable("material_equivalents", {
  id: serial("id").primaryKey(),
  materialId: integer("material_id").references(() => rawMaterials.id).notNull(),
  equivalentId: integer("equivalent_id").references(() => rawMaterials.id).notNull(),
  notes: text("notes"),
});

// Lab Notebook / Experiment Notes
export const experiments = pgTable("experiments", {
  id: serial("id").primaryKey(),
  projectId: integer("project_id").references(() => projects.id).notNull(),
  title: text("title").notNull(),
  notes: text("notes").notNull(),
  date: date("date").defaultNow().notNull(),
  createdAt: timestamp("created_at").defaultNow(),
});

// Test Results
export const testResults = pgTable("test_results", {
  id: serial("id").primaryKey(),
  experimentId: integer("experiment_id").references(() => experiments.id).notNull(),
  testName: text("test_name").notNull(),
  measuredValue: numeric("measured_value").notNull(),
  unit: text("unit").notNull(),
  observation: text("observation"),
  isSuccessful: boolean("is_successful").default(true).notNull(),
  createdAt: timestamp("created_at").defaultNow(),
});

// Tasks (Görevler)
export const tasks = pgTable("tasks", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  description: text("description"),
  projectId: integer("project_id").references(() => projects.id),
  assignee: text("assignee"),
  status: text("status", { enum: taskStatuses }).default("Beklemede").notNull(),
  priority: text("priority", { enum: taskPriorities }).default("Orta").notNull(),
  dueDate: date("due_date"),
  createdAt: timestamp("created_at").defaultNow(),
});

// Users
export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").unique().notNull(),
  password: text("password").notNull(),
  name: text("name").notNull(),
  expertiseGroup: text("expertise_group", { enum: expertiseAreas }).notNull(),
  role: text("role", { enum: userRoles }).default("Gözlemci").notNull(),
  createdAt: timestamp("created_at").defaultNow(),
});

// App Settings (for AI prompt, etc.)
export const settings = pgTable("settings", {
  id: serial("id").primaryKey(),
  key: text("key").unique().notNull(),
  value: text("value").notNull(),
  updatedAt: timestamp("updated_at").defaultNow(),
});

// === RELATIONS ===

export const projectsRelations = relations(projects, ({ many }) => ({
  experiments: many(experiments),
  tasks: many(tasks),
}));

export const tasksRelations = relations(tasks, ({ one }) => ({
  project: one(projects, {
    fields: [tasks.projectId],
    references: [projects.id],
  }),
}));

export const rawMaterialsRelations = relations(rawMaterials, ({ many }) => ({
  equivalents: many(materialEquivalents, { relationName: "materialSource" }),
  equivalentTo: many(materialEquivalents, { relationName: "materialTarget" }),
}));

export const materialEquivalentsRelations = relations(materialEquivalents, ({ one }) => ({
  material: one(rawMaterials, {
    fields: [materialEquivalents.materialId],
    references: [rawMaterials.id],
    relationName: "materialSource",
  }),
  equivalent: one(rawMaterials, {
    fields: [materialEquivalents.equivalentId],
    references: [rawMaterials.id],
    relationName: "materialTarget",
  }),
}));

export const experimentsRelations = relations(experiments, ({ one, many }) => ({
  project: one(projects, {
    fields: [experiments.projectId],
    references: [projects.id],
  }),
  testResults: many(testResults),
}));

export const testResultsRelations = relations(testResults, ({ one }) => ({
  experiment: one(experiments, {
    fields: [testResults.experimentId],
    references: [experiments.id],
  }),
}));

// === BASE SCHEMAS ===
export const insertProjectSchema = createInsertSchema(projects).omit({ id: true, createdAt: true });
export const insertRawMaterialSchema = createInsertSchema(rawMaterials).omit({ id: true, createdAt: true });
export const insertMaterialEquivalentSchema = createInsertSchema(materialEquivalents).omit({ id: true });
export const insertExperimentSchema = createInsertSchema(experiments).omit({ id: true, createdAt: true });
export const insertTestResultSchema = createInsertSchema(testResults).omit({ id: true, createdAt: true });
export const insertTaskSchema = createInsertSchema(tasks).omit({ id: true, createdAt: true });
export const insertUserSchema = createInsertSchema(users).omit({ id: true, createdAt: true });

// === EXPLICIT API CONTRACT TYPES ===

export type Project = typeof projects.$inferSelect;
export type InsertProject = z.infer<typeof insertProjectSchema>;

export type RawMaterial = typeof rawMaterials.$inferSelect;
export type InsertRawMaterial = z.infer<typeof insertRawMaterialSchema>;

export type Experiment = typeof experiments.$inferSelect;
export type InsertExperiment = z.infer<typeof insertExperimentSchema>;

export type TestResult = typeof testResults.$inferSelect;
export type InsertTestResult = z.infer<typeof insertTestResultSchema>;

export type MaterialEquivalent = typeof materialEquivalents.$inferSelect;
export type InsertMaterialEquivalent = z.infer<typeof insertMaterialEquivalentSchema>;

export type Task = typeof tasks.$inferSelect;
export type InsertTask = z.infer<typeof insertTaskSchema>;

// Request Types
export type CreateProjectRequest = InsertProject;
export type UpdateProjectRequest = Partial<InsertProject>;

export type CreateRawMaterialRequest = InsertRawMaterial;
export type UpdateRawMaterialRequest = Partial<InsertRawMaterial>;

export type User = typeof users.$inferSelect;
export type InsertUser = z.infer<typeof insertUserSchema>;

export type CreateTaskRequest = InsertTask;
export type UpdateTaskRequest = Partial<InsertTask>;

export type CreateUserRequest = InsertUser;
export type UpdateUserRequest = Partial<InsertUser>;

// Response Types
export type ProjectResponse = Project;
export type RawMaterialResponse = RawMaterial;
