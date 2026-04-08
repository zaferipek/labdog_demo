import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, buildUrl, type InsertRawMaterial, type InsertMaterialEquivalent } from "@shared/routes";
import type { UpdateRawMaterialRequest } from "@shared/schema";

export function useMaterials() {
  return useQuery({
    queryKey: [api.materials.list.path],
    queryFn: async () => {
      const res = await fetch(api.materials.list.path, { credentials: "include" });
      if (!res.ok) throw new Error("Failed to fetch materials");
      return api.materials.list.responses[200].parse(await res.json());
    },
  });
}

export function useMaterial(id: number) {
  return useQuery({
    queryKey: ['/api/materials', id],
    queryFn: async () => {
      const res = await fetch(`/api/materials/${id}`, { credentials: "include" });
      if (!res.ok) throw new Error("Failed to fetch material");
      return res.json();
    },
    enabled: !!id,
  });
}

export function useCreateMaterial() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: InsertRawMaterial) => {
      const res = await fetch(api.materials.create.path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        credentials: "include",
      });
      if (!res.ok) throw new Error("Failed to create material");
      return api.materials.create.responses[201].parse(await res.json());
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [api.materials.list.path] });
    },
  });
}

export function useUpdateMaterial() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: UpdateRawMaterialRequest }) => {
      const res = await fetch(`/api/materials/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        credentials: "include",
      });
      if (!res.ok) throw new Error("Failed to update material");
      return res.json();
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [api.materials.list.path] });
      queryClient.invalidateQueries({ queryKey: ['/api/materials', variables.id] });
    },
  });
}

export function useUploadMaterialDoc() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, docType, file }: { id: number; docType: "sds" | "tds"; file: File }) => {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`/api/materials/${id}/upload/${docType}`, {
        method: "POST",
        body: formData,
        credentials: "include",
      });
      if (!res.ok) throw new Error("Failed to upload document");
      return res.json();
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [api.materials.list.path] });
      queryClient.invalidateQueries({ queryKey: ['/api/materials', variables.id] });
    },
  });
}

export function useMaterialEquivalents(id: number) {
  return useQuery({
    queryKey: [api.materials.getEquivalents.path, id],
    queryFn: async () => {
      const url = buildUrl(api.materials.getEquivalents.path, { id });
      const res = await fetch(url, { credentials: "include" });
      if (!res.ok) throw new Error("Failed to fetch equivalents");
      return api.materials.getEquivalents.responses[200].parse(await res.json());
    },
    enabled: !!id,
  });
}

export function useAddEquivalent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: InsertMaterialEquivalent) => {
      const res = await fetch(api.materials.addEquivalent.path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        credentials: "include",
      });
      if (!res.ok) throw new Error("Failed to add equivalent");
      return api.materials.addEquivalent.responses[201].parse(await res.json());
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [api.materials.getEquivalents.path, variables.materialId] });
      queryClient.invalidateQueries({ queryKey: [api.materials.getEquivalents.path, variables.equivalentId] });
    },
  });
}
