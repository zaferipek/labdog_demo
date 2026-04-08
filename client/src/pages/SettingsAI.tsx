import { Sidebar } from "@/components/Sidebar";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useQuery, useMutation } from "@tanstack/react-query";
import { api, buildUrl } from "@shared/routes";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { useAuth } from "@/hooks/use-auth";
import { canAccessSettings } from "@/lib/permissions";
import { BrainCircuit, Save, Loader2, ArrowLeft } from "lucide-react";
import { useState, useEffect } from "react";
import { Link, useLocation } from "wouter";

export default function SettingsAI() {
  const { toast } = useToast();
  const { data: user, isLoading: isAuthLoading } = useAuth();
  const [, setLocation] = useLocation();

  useEffect(() => {
    if (!isAuthLoading && user && !canAccessSettings(user)) {
      setLocation("/");
    }
  }, [user, isAuthLoading, setLocation]);

  const { data: promptData, isLoading: isPromptLoading } = useQuery({
    queryKey: [buildUrl(api.settings.get.path, { key: "ai_prompt" })],
  });

  const { data: urlData, isLoading: isUrlLoading } = useQuery({
    queryKey: [buildUrl(api.settings.get.path, { key: "ai_api_url" })],
  });

  const [prompt, setPrompt] = useState("");
  const [apiUrl, setApiUrl] = useState("");

  useEffect(() => {
    if (promptData) setPrompt(promptData.value);
  }, [promptData]);

  useEffect(() => {
    if (urlData) setApiUrl(urlData.value);
  }, [urlData]);

  const mutation = useMutation({
    mutationFn: async (vars: { key: string; value: string }) => {
      return await apiRequest("POST", api.settings.set.path, vars);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/settings"] });
    },
  });

  const handleSave = async () => {
    try {
      await mutation.mutateAsync({ key: "ai_prompt", value: prompt });
      await mutation.mutateAsync({ key: "ai_api_url", value: apiUrl });
      toast({ title: "Başarılı", description: "AI ayarları kaydedildi." });
    } catch {
      toast({ variant: "destructive", title: "Hata", description: "Ayarlar kaydedilemedi." });
    }
  };

  if (isPromptLoading || isUrlLoading || isAuthLoading) {
    return (
      <div className="flex min-h-screen bg-slate-50 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      <main className="flex-1 ml-0 md:ml-64 p-8">
        <div className="flex items-center gap-4 mb-8">
          <Link href="/settings">
            <Button variant="ghost" size="icon" className="rounded-full" data-testid="button-back-settings">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-display font-bold text-slate-900">Yapay Zeka Yapılandırması</h1>
            <p className="text-slate-500 mt-1">Proje analizi için kullanılacak AI parametreleri.</p>
          </div>
        </div>

        <div className="max-w-3xl">
          <Card className="border-none shadow-md">
            <CardHeader className="flex flex-row items-center gap-4">
              <div className="h-10 w-10 bg-purple-100 rounded-lg flex items-center justify-center text-purple-600">
                <BrainCircuit className="h-6 w-6" />
              </div>
              <div>
                <CardTitle>AI Entegrasyonu</CardTitle>
                <CardDescription>API uç noktası ve sistem komutunu yapılandırın.</CardDescription>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="api-url">API Uç Noktası (Endpoint)</Label>
                <Input
                  id="api-url"
                  placeholder="https://api.openai.com/v1/chat/completions"
                  value={apiUrl}
                  onChange={(e) => setApiUrl(e.target.value)}
                  data-testid="input-ai-api-url"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="prompt">Sistem Komutu (System Prompt)</Label>
                <Textarea
                  id="prompt"
                  placeholder="AI'ya projeyi nasıl analiz etmesi gerektiğini söyleyin..."
                  className="min-h-[150px]"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  data-testid="textarea-ai-prompt"
                />
              </div>
              <div className="flex justify-end">
                <Button
                  onClick={handleSave}
                  disabled={mutation.isPending}
                  className="gap-2"
                  data-testid="button-save-ai-settings"
                >
                  {mutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                  Ayarları Kaydet
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
