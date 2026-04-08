import { Sidebar } from "@/components/Sidebar";
import { useProject } from "@/hooks/use-projects";
import { useRoute } from "wouter";
import { Loader2, ArrowLeft, BrainCircuit, FileText, FlaskConical, Beaker, Plus, Check, X } from "lucide-react";
import { Link } from "wouter";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { format } from "date-fns";
import { tr } from "date-fns/locale";
import { useToast } from "@/hooks/use-toast";
import { useProjectExperiments, useCreateExperiment, useCreateTestResult } from "@/hooks/use-experiments";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription } from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { insertExperimentSchema, insertTestResultSchema, type InsertExperiment, type InsertTestResult } from "@shared/schema";
import { useState, useEffect } from "react";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Edit2 } from "lucide-react";
import { useUpdateProject } from "@/hooks/use-projects";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks/use-auth";
import { canEditProject, canCreateExperiment } from "@/lib/permissions";

export default function ProjectDetails() {
  const [, params] = useRoute("/projects/:id");
  const id = params ? parseInt(params.id) : 0;
  
  const { data: project, isLoading: isProjectLoading } = useProject(id);
  const { data: experiments, isLoading: isExpLoading } = useProjectExperiments(id);
  const { toast } = useToast();
  const { data: user } = useAuth();

  const handleAIAnalysis = () => {
    toast({
      title: "AI Analizi Başlatıldı",
      description: "Gemini AI proje verilerini analiz ediyor... (Bu özellik yakında aktif olacak)",
      duration: 3000,
    });
  };

  if (isProjectLoading || isExpLoading) {
    return (
      <div className="flex min-h-screen bg-slate-50 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!project) return <div>Proje bulunamadı</div>;

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      
      <main className="flex-1 ml-0 md:ml-64 p-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <Link href="/projects">
            <Button variant="ghost" size="icon" className="rounded-full">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div className="flex-1">
            <div className="flex items-center gap-3">
              {user && canEditProject(user, project) ? (
                <EditProjectNameDialog project={project} />
              ) : (
                <h1 className="text-2xl font-display font-bold text-slate-900">{project.name}</h1>
              )}
              <Badge variant="secondary" className="bg-blue-100 text-blue-700 hover:bg-blue-200">
                {project.status}
              </Badge>
            </div>
            <p className="text-sm text-slate-500 mt-1">
              {project.rdSpecialist} • {project.expertiseArea}
            </p>
          </div>
          {user && canEditProject(user, project) && (
            <Button 
              className="bg-purple-600 hover:bg-purple-700 text-white gap-2 shadow-lg shadow-purple-200"
              onClick={handleAIAnalysis}
            >
              <BrainCircuit className="h-4 w-4" /> AI Analiz Et
            </Button>
          )}
        </div>

        <Tabs defaultValue="experiments" className="w-full">
          <TabsList className="bg-white border p-1 rounded-xl mb-6">
            <TabsTrigger value="overview" className="rounded-lg data-[state=active]:bg-primary data-[state=active]:text-white">Genel Bakış</TabsTrigger>
            <TabsTrigger value="experiments" className="rounded-lg data-[state=active]:bg-primary data-[state=active]:text-white">Deneyler ve Sonuçlar</TabsTrigger>
          </TabsList>

          <TabsContent value="overview">
            <Card className="border-none shadow-md">
              <CardHeader>
                <CardTitle>Proje Detayları</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-slate-500">Açıklama</p>
                    <p className="text-slate-800">{project.description || "Açıklama girilmemiş."}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-slate-500">Uzmanlık Alanı</p>
                    <p className="text-slate-800">{project.expertiseArea}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-slate-500">Başlangıç Tarihi</p>
                    <p className="text-slate-800">{format(new Date(project.startDate), "d MMMM yyyy", { locale: tr })}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-slate-500">Hedef Tarih</p>
                    <p className="text-slate-800">
                      {project.targetDate ? format(new Date(project.targetDate), "d MMMM yyyy", { locale: tr }) : "-"}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="experiments">
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-lg font-bold text-slate-800">Laboratuvar Defteri</h2>
                {user && canCreateExperiment(user, project) && (
                  <AddExperimentDialog projectId={project.id} />
                )}
              </div>

              {experiments && experiments.length > 0 ? (
                <Accordion type="single" collapsible className="space-y-4">
                  {experiments.map((exp) => (
                    <AccordionItem key={exp.id} value={`item-${exp.id}`} className="bg-white border rounded-xl shadow-sm px-4">
                      <AccordionTrigger className="hover:no-underline py-4">
                        <div className="flex items-center gap-4 text-left">
                          <div className="p-2 bg-slate-100 rounded-lg text-slate-500">
                            <FlaskConical className="h-5 w-5" />
                          </div>
                          <div>
                            <h4 className="font-semibold text-slate-800">{exp.title}</h4>
                            <p className="text-xs text-slate-500">{format(new Date(exp.date), "d MMM yyyy", { locale: tr })}</p>
                          </div>
                        </div>
                      </AccordionTrigger>
                      <AccordionContent className="pb-4 pt-2">
                        <div className="pl-[52px]">
                          <p className="text-slate-600 mb-4 bg-slate-50 p-3 rounded-lg text-sm border">
                            {exp.notes}
                          </p>
                          
                          <div className="flex items-center justify-between mb-3 mt-6">
                            <h5 className="font-semibold text-sm text-slate-700 flex items-center gap-2">
                              <Beaker className="h-4 w-4" /> Test Sonuçları
                            </h5>
                            {user && canCreateExperiment(user, project) && (
                              <AddTestResultDialog experimentId={exp.id} />
                            )}
                          </div>

                          {exp.testResults && exp.testResults.length > 0 ? (
                            <div className="border rounded-lg overflow-hidden">
                              <table className="w-full text-sm">
                                <thead className="bg-slate-50 border-b">
                                  <tr>
                                    <th className="px-4 py-2 text-left font-medium text-slate-500">Test Adı</th>
                                    <th className="px-4 py-2 text-left font-medium text-slate-500">Değer</th>
                                    <th className="px-4 py-2 text-left font-medium text-slate-500">Birim</th>
                                    <th className="px-4 py-2 text-left font-medium text-slate-500">Durum</th>
                                  </tr>
                                </thead>
                                <tbody className="divide-y">
                                  {exp.testResults.map(result => (
                                    <tr key={result.id} className="hover:bg-slate-50">
                                      <td className="px-4 py-3">{result.testName}</td>
                                      <td className="px-4 py-3 font-mono">{result.measuredValue}</td>
                                      <td className="px-4 py-3 text-slate-500">{result.unit}</td>
                                      <td className="px-4 py-3">
                                        {result.isSuccessful ? (
                                          <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200 gap-1">
                                            <Check className="h-3 w-3" /> Başarılı
                                          </Badge>
                                        ) : (
                                          <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200 gap-1">
                                            <X className="h-3 w-3" /> Başarısız
                                          </Badge>
                                        )}
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          ) : (
                            <div className="text-center py-4 text-slate-400 text-sm border rounded-lg bg-slate-50/50">
                              Henüz test sonucu eklenmemiş.
                            </div>
                          )}
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  ))}
                </Accordion>
              ) : (
                <div className="text-center py-12 bg-white rounded-xl border border-dashed border-slate-300">
                  <div className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 mb-4">
                    <FlaskConical className="h-6 w-6 text-slate-400" />
                  </div>
                  <h3 className="text-lg font-medium text-slate-900">Deney Bulunamadı</h3>
                  <p className="text-slate-500 max-w-sm mx-auto mt-2 mb-4">
                    Bu proje için henüz bir deney kaydı oluşturulmamış. İlk deneyinizi ekleyerek başlayın.
                  </p>
                  {user && canCreateExperiment(user, project) && (
                    <AddExperimentDialog projectId={project.id} />
                  )}
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}

function AddExperimentDialog({ projectId }: { projectId: number }) {
  const [open, setOpen] = useState(false);
  const { toast } = useToast();
  const createExperiment = useCreateExperiment();
  
  const form = useForm<InsertExperiment>({
    resolver: zodResolver(insertExperimentSchema),
    defaultValues: {
      projectId,
      title: "",
      notes: "",
      date: new Date().toISOString().split('T')[0],
    },
  });

  async function onSubmit(data: InsertExperiment) {
    try {
      await createExperiment.mutateAsync(data);
      toast({ title: "Başarılı", description: "Deney notu eklendi." });
      setOpen(false);
      form.reset();
    } catch {
      toast({ variant: "destructive", title: "Hata", description: "Ekleme başarısız." });
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm" className="gap-2">
          <Plus className="h-4 w-4" /> Yeni Deney Ekle
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Yeni Deney Notu</DialogTitle>
          <DialogDescription>Yapılan deneyin detaylarını girin.</DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 pt-4">
            <FormField
              control={form.control}
              name="title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Deney Başlığı</FormLabel>
                  <FormControl><Input placeholder="Örn: Formülasyon V1.2 Testi" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="date"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Tarih</FormLabel>
                  <FormControl><Input type="date" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="notes"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Notlar & Gözlemler</FormLabel>
                  <FormControl><Textarea placeholder="Deney süreci, koşullar ve gözlemler..." className="min-h-[100px]" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit" className="w-full" disabled={createExperiment.isPending}>
              {createExperiment.isPending ? "Kaydediliyor..." : "Kaydet"}
            </Button>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}

function AddTestResultDialog({ experimentId }: { experimentId: number }) {
  const [open, setOpen] = useState(false);
  const { toast } = useToast();
  const createTestResult = useCreateTestResult();

  const form = useForm<InsertTestResult>({
    resolver: zodResolver(insertTestResultSchema),
    defaultValues: {
      experimentId,
      testName: "",
      measuredValue: "",
      unit: "",
      observation: "",
      isSuccessful: true,
    },
  });

  async function onSubmit(data: InsertTestResult) {
    try {
      await createTestResult.mutateAsync(data);
      toast({ title: "Başarılı", description: "Test sonucu eklendi." });
      setOpen(false);
      form.reset();
    } catch {
      toast({ variant: "destructive", title: "Hata", description: "Ekleme başarısız." });
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm" variant="outline" className="gap-2" data-testid={`button-add-test-result-${experimentId}`}>
          <Plus className="h-3 w-3" /> Sonuç Ekle
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Yeni Test Sonucu</DialogTitle>
          <DialogDescription>Deney için ölçüm sonuçlarını girin.</DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 pt-4">
            <FormField
              control={form.control}
              name="testName"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Test Adı</FormLabel>
                  <FormControl><Input placeholder="Örn: Viskozite (25°C)" {...field} data-testid="input-test-name" /></FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="measuredValue"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Ölçülen Değer</FormLabel>
                    <FormControl><Input placeholder="1200" {...field} data-testid="input-measured-value" /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="unit"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Birim</FormLabel>
                    <FormControl><Input placeholder="cPs" {...field} data-testid="input-unit" /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <FormField
              control={form.control}
              name="observation"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Gözlem</FormLabel>
                  <FormControl><Textarea placeholder="Ölçüm notu..." className="min-h-[60px]" {...field} value={field.value || ""} data-testid="textarea-observation" /></FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="isSuccessful"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Sonuç Durumu</FormLabel>
                  <Select value={field.value ? "true" : "false"} onValueChange={(v) => field.onChange(v === "true")}>
                    <FormControl>
                      <SelectTrigger data-testid="select-is-successful">
                        <SelectValue />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="true">Başarılı</SelectItem>
                      <SelectItem value="false">Başarısız</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit" className="w-full" disabled={createTestResult.isPending} data-testid="button-submit-test-result">
              {createTestResult.isPending ? "Kaydediliyor..." : "Kaydet"}
            </Button>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}

function EditProjectNameDialog({ project }: { project: any }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState(project.name);
  const { toast } = useToast();
  const updateProject = useUpdateProject();

  // Update local name when project prop changes (e.g. after a successful mutation)
  useEffect(() => {
    setName(project.name);
  }, [project.name]);

  const handleSave = async () => {
    try {
      await updateProject.mutateAsync({ id: project.id, name });
      toast({ title: "Başarılı", description: "Proje ismi güncellendi." });
      setOpen(false);
    } catch {
      toast({ variant: "destructive", title: "Hata", description: "Güncelleme başarısız." });
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <div className="group flex items-center gap-2">
        <h1 className="text-2xl font-display font-bold text-slate-900">{project.name}</h1>
        <DialogTrigger asChild>
          <Button variant="ghost" size="icon" className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity">
            <Edit2 className="h-4 w-4" />
          </Button>
        </DialogTrigger>
      </div>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Proje İsmini Düzenle</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 pt-4">
          <div className="space-y-2">
            <Label>Yeni Proje İsmi</Label>
            <Input value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <Button onClick={handleSave} className="w-full" disabled={updateProject.isPending}>
            {updateProject.isPending ? "Kaydediliyor..." : "Kaydet"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
