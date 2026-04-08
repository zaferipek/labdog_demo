import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, buildUrl, type InsertExperiment, type InsertTestResult } from "@shared/routes";

export function useProjectExperiments(projectId: number) {
  return useQuery({
    queryKey: [api.experiments.listByProject.path, projectId],
    queryFn: async () => {
      const url = buildUrl(api.experiments.listByProject.path, { id: projectId });
      const res = await fetch(url, { credentials: "include" });
      if (!res.ok) throw new Error("Failed to fetch experiments");
      return api.experiments.listByProject.responses[200].parse(await res.json());
    },
    enabled: !!projectId,
  });
}

export function useCreateExperiment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: InsertExperiment) => {
      const res = await fetch(api.experiments.create.path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        credentials: "include",
      });
      if (!res.ok) throw new Error("Failed to create experiment");
      return api.experiments.create.responses[201].parse(await res.json());
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [api.experiments.listByProject.path, variables.projectId] });
    },
  });
}

export function useCreateTestResult() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: InsertTestResult) => {
      const res = await fetch(api.testResults.create.path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        credentials: "include",
      });
      if (!res.ok) throw new Error("Failed to add test result");
      return api.testResults.create.responses[201].parse(await res.json());
    },
    onSuccess: () => {
      // Invalidate all experiment lists to update the view
      // A more specific invalidation would be better but this is safe
      queryClient.invalidateQueries({ queryKey: [api.experiments.listByProject.path] });
    },
  });
}
