
import { z } from 'zod';
import { 
  insertProjectSchema, 
  insertRawMaterialSchema, 
  insertExperimentSchema, 
  insertTestResultSchema,
  insertMaterialEquivalentSchema,
  insertTaskSchema,
  insertUserSchema,
  projects,
  rawMaterials,
  experiments,
  testResults,
  materialEquivalents,
  tasks,
  users
} from './schema';

// ============================================
// SHARED ERROR SCHEMAS
// ============================================
export const errorSchemas = {
  validation: z.object({
    message: z.string(),
    field: z.string().optional(),
  }),
  notFound: z.object({
    message: z.string(),
  }),
  internal: z.object({
    message: z.string(),
  }),
};

// ============================================
// API CONTRACT
// ============================================
export const api = {
  // --- Projects ---
  projects: {
    list: {
      method: 'GET' as const,
      path: '/api/projects' as const,
      responses: {
        200: z.array(z.custom<typeof projects.$inferSelect>()),
      },
    },
    get: {
      method: 'GET' as const,
      path: '/api/projects/:id' as const,
      responses: {
        200: z.custom<typeof projects.$inferSelect>(),
        404: errorSchemas.notFound,
      },
    },
    create: {
      method: 'POST' as const,
      path: '/api/projects' as const,
      input: insertProjectSchema,
      responses: {
        201: z.custom<typeof projects.$inferSelect>(),
        400: errorSchemas.validation,
      },
    },
    update: {
      method: 'PATCH' as const,
      path: '/api/projects/:id' as const,
      input: insertProjectSchema.partial(),
      responses: {
        200: z.custom<typeof projects.$inferSelect>(),
        400: errorSchemas.validation,
        404: errorSchemas.notFound,
      },
    },
    delete: {
      method: 'DELETE' as const,
      path: '/api/projects/:id' as const,
      responses: {
        204: z.void(),
        404: errorSchemas.notFound,
      },
    },
  },

  // --- Raw Materials ---
  materials: {
    list: {
      method: 'GET' as const,
      path: '/api/materials' as const,
      responses: {
        200: z.array(z.custom<typeof rawMaterials.$inferSelect>()),
      },
    },
    create: {
      method: 'POST' as const,
      path: '/api/materials' as const,
      input: insertRawMaterialSchema,
      responses: {
        201: z.custom<typeof rawMaterials.$inferSelect>(),
        400: errorSchemas.validation,
      },
    },
    addEquivalent: {
      method: 'POST' as const,
      path: '/api/materials/equivalents' as const,
      input: insertMaterialEquivalentSchema,
      responses: {
        201: z.custom<typeof materialEquivalents.$inferSelect>(),
        400: errorSchemas.validation,
      },
    },
    get: {
      method: 'GET' as const,
      path: '/api/materials/:id' as const,
      responses: {
        200: z.custom<typeof rawMaterials.$inferSelect>(),
        404: errorSchemas.notFound,
      },
    },
    update: {
      method: 'PATCH' as const,
      path: '/api/materials/:id' as const,
      input: insertRawMaterialSchema.partial(),
      responses: {
        200: z.custom<typeof rawMaterials.$inferSelect>(),
        400: errorSchemas.validation,
        404: errorSchemas.notFound,
      },
    },
    getEquivalents: {
      method: 'GET' as const,
      path: '/api/materials/:id/equivalents' as const,
      responses: {
        200: z.array(z.custom<typeof rawMaterials.$inferSelect>()),
      },
    }
  },

  // --- Experiments & Tests ---
  experiments: {
    listByProject: {
      method: 'GET' as const,
      path: '/api/projects/:id/experiments' as const,
      responses: {
        200: z.array(z.custom<typeof experiments.$inferSelect & { testResults: typeof testResults.$inferSelect[] }>()),
      },
    },
    create: {
      method: 'POST' as const,
      path: '/api/experiments' as const,
      input: insertExperimentSchema,
      responses: {
        201: z.custom<typeof experiments.$inferSelect>(),
        400: errorSchemas.validation,
      },
    },
  },

  testResults: {
    create: {
      method: 'POST' as const,
      path: '/api/test-results' as const,
      input: insertTestResultSchema,
      responses: {
        201: z.custom<typeof testResults.$inferSelect>(),
        400: errorSchemas.validation,
      },
    },
  },
  
  // --- Tasks ---
  tasks: {
    list: {
      method: 'GET' as const,
      path: '/api/tasks' as const,
      responses: {
        200: z.array(z.custom<typeof tasks.$inferSelect>()),
      },
    },
    get: {
      method: 'GET' as const,
      path: '/api/tasks/:id' as const,
      responses: {
        200: z.custom<typeof tasks.$inferSelect>(),
        404: errorSchemas.notFound,
      },
    },
    create: {
      method: 'POST' as const,
      path: '/api/tasks' as const,
      input: insertTaskSchema,
      responses: {
        201: z.custom<typeof tasks.$inferSelect>(),
        400: errorSchemas.validation,
      },
    },
    update: {
      method: 'PATCH' as const,
      path: '/api/tasks/:id' as const,
      input: insertTaskSchema.partial(),
      responses: {
        200: z.custom<typeof tasks.$inferSelect>(),
        400: errorSchemas.validation,
        404: errorSchemas.notFound,
      },
    },
    delete: {
      method: 'DELETE' as const,
      path: '/api/tasks/:id' as const,
      responses: {
        204: z.void(),
        404: errorSchemas.notFound,
      },
    },
  },

  // --- Users ---
  users: {
    list: {
      method: 'GET' as const,
      path: '/api/users' as const,
      responses: {
        200: z.array(z.custom<typeof users.$inferSelect>()),
      },
    },
    get: {
      method: 'GET' as const,
      path: '/api/users/:id' as const,
      responses: {
        200: z.custom<typeof users.$inferSelect>(),
        404: errorSchemas.notFound,
      },
    },
    create: {
      method: 'POST' as const,
      path: '/api/users' as const,
      input: insertUserSchema,
      responses: {
        201: z.custom<typeof users.$inferSelect>(),
        400: errorSchemas.validation,
      },
    },
    update: {
      method: 'PATCH' as const,
      path: '/api/users/:id' as const,
      input: insertUserSchema.partial(),
      responses: {
        200: z.custom<typeof users.$inferSelect>(),
        400: errorSchemas.validation,
        404: errorSchemas.notFound,
      },
    },
    delete: {
      method: 'DELETE' as const,
      path: '/api/users/:id' as const,
      responses: {
        204: z.void(),
        404: errorSchemas.notFound,
      },
    },
  },

  // --- Dashboard ---
  dashboard: {
    stats: {
      method: 'GET' as const,
      path: '/api/stats' as const,
      responses: {
        200: z.array(z.object({
          expertiseArea: z.string(),
          count: z.number(),
          projects: z.array(z.custom<typeof projects.$inferSelect>())
        })),
      },
    }
  },

  // --- Settings ---
  settings: {
    get: {
      method: 'GET' as const,
      path: '/api/settings/:key' as const,
      responses: {
        200: z.object({ value: z.string() }),
        404: errorSchemas.notFound,
      },
    },
    set: {
      method: 'POST' as const,
      path: '/api/settings' as const,
      input: z.object({ key: z.string(), value: z.string() }),
      responses: {
        200: z.object({ key: z.string(), value: z.string() }),
      },
    },
  },
};

// ============================================
// HELPER FUNCTIONS
// ============================================
export function buildUrl(path: string, params?: Record<string, string | number>): string {
  let url = path;
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (url.includes(`:${key}`)) {
        url = url.replace(`:${key}`, String(value));
      }
    });
  }
  return url;
}
