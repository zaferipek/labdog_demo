
import type { Express, Request, Response, NextFunction } from "express";
import type { Server } from "http";
import { storage } from "./storage";
import { api } from "@shared/routes";
import { z } from "zod";
import multer from "multer";
import path from "path";
import fs from "fs";

const uploadsDir = path.join(process.cwd(), "uploads");
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

const upload = multer({
  storage: multer.diskStorage({
    destination: uploadsDir,
    filename: (_req, file, cb) => {
      const uniqueSuffix = Date.now() + "-" + Math.round(Math.random() * 1e9);
      cb(null, uniqueSuffix + "-" + file.originalname);
    },
  }),
  limits: { fileSize: 20 * 1024 * 1024 },
  fileFilter: (_req, file, cb) => {
    const allowed = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".png", ".jpg", ".jpeg"];
    const ext = path.extname(file.originalname).toLowerCase();
    cb(null, allowed.includes(ext));
  },
});

declare module "express-session" {
  interface SessionData {
    user: {
      id: number;
      username: string;
      name: string;
      role: string;
      expertiseGroup: string;
    };
  }
}

const WRITE_ROLES = ["Admin", "Yönetici", "Ar-Ge Mühendisi", "Ar-Ge Uzmanı", "Tekniker", "Kalite Kontrol"];
const MANAGER_ROLES = ["Admin", "Yönetici"];
const MATERIAL_WRITE_ROLES = [...WRITE_ROLES, "Satın Alma"];

function requireAuth(req: Request, res: Response, next: NextFunction) {
  if (!req.session.user) {
    return res.status(401).json({ message: "Oturum açılmamış." });
  }
  next();
}

function requireRole(...roles: string[]) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.session.user) {
      return res.status(401).json({ message: "Oturum açılmamış." });
    }
    if (!roles.includes(req.session.user.role)) {
      return res.status(403).json({ message: "Bu işlem için yetkiniz yok." });
    }
    next();
  };
}

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {

  // --- Auth Routes ---
  app.post("/api/auth/login", async (req, res) => {
    const { username, password } = req.body;
    const user = await storage.getUserByUsername(username);
    if (!user || user.password !== password) {
      return res.status(401).json({ message: "Kullanıcı adı veya şifre hatalı." });
    }
    req.session.user = {
      id: user.id,
      username: user.username,
      name: user.name,
      role: user.role,
      expertiseGroup: user.expertiseGroup,
    };
    res.json({
      id: user.id,
      username: user.username,
      name: user.name,
      role: user.role,
      expertiseGroup: user.expertiseGroup,
    });
  });

  app.get("/api/auth/me", (req, res) => {
    if (req.session.user) {
      return res.json(req.session.user);
    }
    res.status(401).json({ message: "Oturum açılmamış." });
  });

  app.post("/api/auth/logout", (req, res) => {
    req.session.destroy(() => {
      res.json({ ok: true });
    });
  });

  // --- Projects Routes ---
  app.get(api.projects.list.path, requireAuth, async (req, res) => {
    const projects = await storage.getProjects();
    res.json(projects);
  });

  app.get(api.projects.get.path, requireAuth, async (req, res) => {
    const project = await storage.getProject(Number(req.params.id));
    if (!project) return res.status(404).json({ message: "Project not found" });
    res.json(project);
  });

  app.post(api.projects.create.path, requireRole(...WRITE_ROLES), async (req, res) => {
    try {
      const input = api.projects.create.input.parse(req.body);
      const project = await storage.createProject(input);
      res.status(201).json(project);
    } catch (err) {
      if (err instanceof z.ZodError) {
        return res.status(400).json({ message: err.message });
      }
      throw err;
    }
  });

  app.patch("/api/projects/:id", requireRole(...WRITE_ROLES), async (req, res) => {
    try {
      const id = Number(req.params.id);
      const project = await storage.getProject(id);
      if (!project) {
        return res.status(404).json({ message: "Project not found" });
      }
      const user = req.session.user!;
      if (user.role !== "Admin" && user.expertiseGroup !== project.expertiseArea) {
        return res.status(403).json({ message: "Bu projeyi düzenleme yetkiniz yok." });
      }
      const input = api.projects.update.input.parse(req.body);
      const updated = await storage.updateProject(id, input);
      res.json(updated);
    } catch (err) {
      if (err instanceof z.ZodError) {
        return res.status(400).json({ message: err.message });
      }
      res.status(500).json({ message: "Internal server error" });
    }
  });

  app.delete(api.projects.delete.path, requireRole(...MANAGER_ROLES), async (req, res) => {
    await storage.deleteProject(Number(req.params.id));
    res.status(204).send();
  });

  // --- Materials Routes ---
  app.get(api.materials.list.path, requireAuth, async (req, res) => {
    const materials = await storage.getMaterials();
    res.json(materials);
  });

  app.post(api.materials.create.path, requireRole(...MATERIAL_WRITE_ROLES), async (req, res) => {
    try {
      const input = api.materials.create.input.parse(req.body);
      const material = await storage.createMaterial(input);
      res.status(201).json(material);
    } catch (err) {
      if (err instanceof z.ZodError) {
        return res.status(400).json({ message: err.message });
      }
      throw err;
    }
  });

  app.post(api.materials.addEquivalent.path, requireRole(...MATERIAL_WRITE_ROLES), async (req, res) => {
     try {
      const input = api.materials.addEquivalent.input.parse(req.body);
      const relation = await storage.addMaterialEquivalent(input);
      res.status(201).json(relation);
    } catch (err) {
      if (err instanceof z.ZodError) {
        return res.status(400).json({ message: err.message });
      }
      throw err;
    }
  });

  app.get("/api/materials/:id", requireAuth, async (req, res) => {
    const material = await storage.getMaterial(Number(req.params.id));
    if (!material) return res.status(404).json({ message: "Hammadde bulunamadı" });
    res.json(material);
  });

  app.patch("/api/materials/:id", requireRole(...MATERIAL_WRITE_ROLES), async (req, res) => {
    try {
      const id = Number(req.params.id);
      const material = await storage.getMaterial(id);
      if (!material) {
        return res.status(404).json({ message: "Hammadde bulunamadı" });
      }
      const input = api.materials.update.input.parse(req.body);
      const updated = await storage.updateMaterial(id, input);
      res.json(updated);
    } catch (err) {
      if (err instanceof z.ZodError) {
        return res.status(400).json({ message: err.message });
      }
      res.status(500).json({ message: "Internal server error" });
    }
  });

  app.post("/api/materials/:id/upload/:docType", requireRole(...MATERIAL_WRITE_ROLES), upload.single("file"), async (req, res) => {
    try {
      const id = Number(req.params.id);
      const docType = req.params.docType;
      if (!["sds", "tds"].includes(docType)) {
        return res.status(400).json({ message: "Geçersiz belge tipi. 'sds' veya 'tds' olmalı." });
      }
      const material = await storage.getMaterial(id);
      if (!material) {
        return res.status(404).json({ message: "Hammadde bulunamadı" });
      }
      if (!req.file) {
        return res.status(400).json({ message: "Dosya yüklenmedi." });
      }
      const fileUrl = `/uploads/${req.file.filename}`;
      const updates = docType === "sds"
        ? { safetyDataSheetUrl: fileUrl }
        : { tdsUrl: fileUrl };
      const updated = await storage.updateMaterial(id, updates);
      res.json(updated);
    } catch {
      res.status(500).json({ message: "Dosya yükleme hatası." });
    }
  });

  app.get("/api/materials/:id/doc/:docType", requireAuth, async (req, res) => {
    try {
      const id = Number(req.params.id);
      const docType = req.params.docType;
      if (!["sds", "tds"].includes(docType)) {
        return res.status(400).json({ message: "Geçersiz belge tipi." });
      }
      const material = await storage.getMaterial(id);
      if (!material) {
        return res.status(404).json({ message: "Hammadde bulunamadı" });
      }
      const fileUrl = docType === "sds" ? material.safetyDataSheetUrl : material.tdsUrl;
      if (!fileUrl) {
        return res.status(404).json({ message: "Belge bulunamadı." });
      }
      const filePath = path.join(process.cwd(), fileUrl);
      if (!fs.existsSync(filePath)) {
        return res.status(404).json({ message: "Dosya bulunamadı." });
      }
      res.sendFile(filePath);
    } catch {
      res.status(500).json({ message: "Dosya indirme hatası." });
    }
  });

  app.get(api.materials.getEquivalents.path, requireAuth, async (req, res) => {
    const equivalents = await storage.getMaterialEquivalents(Number(req.params.id));
    res.json(equivalents);
  });

  // --- Experiments & Tests Routes ---
  app.get(api.experiments.listByProject.path, requireAuth, async (req, res) => {
    const experiments = await storage.getExperimentsByProject(Number(req.params.id));
    res.json(experiments);
  });

  app.post(api.experiments.create.path, requireRole(...WRITE_ROLES), async (req, res) => {
    try {
      const input = api.experiments.create.input.parse(req.body);
      const user = req.session.user!;
      if (user.role !== "Admin") {
        const project = await storage.getProject(input.projectId);
        if (project && user.expertiseGroup !== project.expertiseArea) {
          return res.status(403).json({ message: "Bu projeye deney ekleme yetkiniz yok." });
        }
      }
      const experiment = await storage.createExperiment(input);
      res.status(201).json(experiment);
    } catch (err) {
      if (err instanceof z.ZodError) {
        return res.status(400).json({ message: err.message });
      }
      throw err;
    }
  });

  app.post(api.testResults.create.path, requireRole(...WRITE_ROLES), async (req, res) => {
    try {
      const input = api.testResults.create.input.parse(req.body);
      const result = await storage.createTestResult(input);
      res.status(201).json(result);
    } catch (err) {
      if (err instanceof z.ZodError) {
        return res.status(400).json({ message: err.message });
      }
      throw err;
    }
  });

  // --- Tasks Routes ---
  app.get(api.tasks.list.path, requireAuth, async (req, res) => {
    const tasks = await storage.getTasks();
    res.json(tasks);
  });

  app.get(api.tasks.get.path, requireAuth, async (req, res) => {
    const task = await storage.getTask(Number(req.params.id));
    if (!task) return res.status(404).json({ message: "Görev bulunamadı" });
    res.json(task);
  });

  app.post(api.tasks.create.path, requireRole(...WRITE_ROLES), async (req, res) => {
    try {
      const input = api.tasks.create.input.parse(req.body);
      const task = await storage.createTask(input);
      res.status(201).json(task);
    } catch (err) {
      if (err instanceof z.ZodError) {
        return res.status(400).json({ message: err.message });
      }
      throw err;
    }
  });

  app.patch("/api/tasks/:id", requireRole(...WRITE_ROLES), async (req, res) => {
    try {
      const id = Number(req.params.id);
      const input = api.tasks.update.input.parse(req.body);
      const task = await storage.updateTask(id, input);
      if (!task) {
        return res.status(404).json({ message: "Görev bulunamadı" });
      }
      res.json(task);
    } catch (err) {
      if (err instanceof z.ZodError) {
        return res.status(400).json({ message: err.message });
      }
      res.status(500).json({ message: "Internal server error" });
    }
  });

  app.delete(api.tasks.delete.path, requireRole(...MANAGER_ROLES), async (req, res) => {
    await storage.deleteTask(Number(req.params.id));
    res.status(204).send();
  });

  // --- Users Routes ---
  app.get("/api/users/names", requireAuth, async (req, res) => {
    const allUsers = await storage.getUsers();
    const names = allUsers.map(u => ({ id: u.id, name: u.name }));
    res.json(names);
  });

  app.get(api.users.list.path, requireRole("Admin"), async (req, res) => {
    const allUsers = await storage.getUsers();
    const safeUsers = allUsers.map(({ password, ...rest }) => rest);
    res.json(safeUsers);
  });

  app.post(api.users.create.path, requireRole("Admin"), async (req, res) => {
    try {
      const input = api.users.create.input.parse(req.body);
      const existing = await storage.getUserByUsername(input.username);
      if (existing) {
        return res.status(400).json({ message: "Bu kullanıcı adı zaten kullanılıyor." });
      }
      const user = await storage.createUser(input);
      const { password, ...safeUser } = user;
      res.status(201).json(safeUser);
    } catch (err) {
      if (err instanceof z.ZodError) {
        return res.status(400).json({ message: err.message });
      }
      throw err;
    }
  });

  app.patch("/api/users/:id", requireRole("Admin"), async (req, res) => {
    try {
      const id = Number(req.params.id);
      const input = api.users.update.input.parse(req.body);
      const user = await storage.updateUser(id, input);
      if (!user) {
        return res.status(404).json({ message: "Kullanıcı bulunamadı" });
      }
      const { password, ...safeUser } = user;
      res.json(safeUser);
    } catch (err) {
      if (err instanceof z.ZodError) {
        return res.status(400).json({ message: err.message });
      }
      res.status(500).json({ message: "Internal server error" });
    }
  });

  app.delete(api.users.delete.path, requireRole("Admin"), async (req, res) => {
    const id = Number(req.params.id);
    if (req.session.user?.id === id) {
      return res.status(400).json({ message: "Kendinizi silemezsiniz." });
    }
    await storage.deleteUser(id);
    res.status(204).send();
  });

  // --- Dashboard Stats ---
  app.get(api.dashboard.stats.path, requireAuth, async (req, res) => {
    const stats = await storage.getProjectStats();
    res.json(stats);
  });

  // --- Settings ---
  app.get(api.settings.get.path, requireAuth, async (req, res) => {
    const value = await storage.getSetting(req.params.key);
    if (value === undefined) {
      return res.status(404).json({ message: "Ayar bulunamadı" });
    }
    res.json({ value });
  });

  app.post(api.settings.set.path, requireRole("Admin"), async (req, res) => {
    const { key, value } = api.settings.set.input.parse(req.body);
    await storage.setSetting(key, value);
    res.json({ key, value });
  });

  // --- Seed Data ---
  await seedDatabase();

  return httpServer;
}

async function seedDatabase() {
  const existingUsers = await storage.getUsers();
  if (existingUsers.length === 0) {
    await storage.createUser({
      username: "admin",
      password: "admin",
      name: "Admin User",
      expertiseGroup: "Boya/Finish",
      role: "Admin",
    });
    await storage.createUser({
      username: "ahmet",
      password: "1234",
      name: "Ahmet Yılmaz",
      expertiseGroup: "Boya/Finish",
      role: "Yönetici",
    });
    await storage.createUser({
      username: "ayse",
      password: "1234",
      name: "Ayşe Demir",
      expertiseGroup: "Mürekkep",
      role: "Ar-Ge Uzmanı",
    });
    await storage.createUser({
      username: "mehmet",
      password: "1234",
      name: "Mehmet Kaya",
      expertiseGroup: "PUD",
      role: "Gözlemci",
    });
  }

  const projects = await storage.getProjects();
  if (projects.length === 0) {
    const m1 = await storage.createMaterial({ name: "Solvent A", supplier: "Kimya A.Ş.", function: "Çözücü", notes: "Standart solvent" });
    const m2 = await storage.createMaterial({ name: "Reçine X", supplier: "Polimer Ltd.", function: "Bağlayıcı", notes: "Yüksek dayanım" });
    const m3 = await storage.createMaterial({ name: "Solvent B (Muadil)", supplier: "Global Chem", function: "Çözücü", notes: "Solvent A muadili" });

    await storage.addMaterialEquivalent({ materialId: m1.id, equivalentId: m3.id, notes: "Birebir değişim" });

    const p1 = await storage.createProject({
      name: "Yeni Nesil Su Bazlı Boya",
      expertiseArea: "Boya/Finish",
      rdSpecialist: "Ahmet Yılmaz",
      startDate: new Date().toISOString(),
      targetDate: new Date(Date.now() + 86400000 * 30).toISOString(),
      status: "Laboratuvar Testleri",
      description: "Çevre dostu yeni formül geliştirme projesi."
    });

    const p2 = await storage.createProject({
      name: "Hızlı Kuruyan Mürekkep",
      expertiseArea: "Mürekkep",
      rdSpecialist: "Ayşe Demir",
      startDate: new Date().toISOString(),
      status: "Fikir",
      description: "Ambalaj sektörü için hızlı kuruma özelliği."
    });

    const exp1 = await storage.createExperiment({
      projectId: p1.id,
      title: "Viskozite Denemeleri #1",
      notes: "Farklı kıvamlaştırıcı oranları denendi.",
      date: new Date().toISOString()
    });

    await storage.createTestResult({
      experimentId: exp1.id,
      testName: "Viskozite (25°C)",
      measuredValue: "1200",
      unit: "cPs",
      observation: "Beklenen aralıkta.",
      isSuccessful: true
    });
  }
}
