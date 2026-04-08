import { Sidebar } from "@/components/Sidebar";
import { AddProjectDialog } from "@/components/AddProjectDialog";
import { useProjects, useUpdateProject } from "@/hooks/use-projects";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Link } from "wouter";
import { motion } from "framer-motion";
import { 
  Loader2, 
  Calendar, 
  User2, 
  MoreHorizontal, 
  AlertCircle
} from "lucide-react";
import { format } from "date-fns";
import { tr } from "date-fns/locale";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/hooks/use-auth";
import { canCreateProject, canEditProject } from "@/lib/permissions";

const statuses = [
  "Fikir",
  "Literatür Taraması",
  "Laboratuvar Testleri",
  "Pilot",
  "Tamamlandı"
];

const statusColors: Record<string, string> = {
  "Fikir": "bg-slate-100 text-slate-600 border-slate-200",
  "Literatür Taraması": "bg-purple-50 text-purple-700 border-purple-200",
  "Laboratuvar Testleri": "bg-amber-50 text-amber-700 border-amber-200",
  "Pilot": "bg-blue-50 text-blue-700 border-blue-200",
  "Tamamlandı": "bg-emerald-50 text-emerald-700 border-emerald-200",
};

export default function Projects() {
  const { data: projects, isLoading, error } = useProjects();
  const updateProject = useUpdateProject();
  const { toast } = useToast();
  const { data: user } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen bg-slate-50">
        <Sidebar />
        <div className="ml-0 md:ml-64 flex-1 flex items-center justify-center h-screen">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen bg-slate-50">
        <Sidebar />
        <div className="ml-0 md:ml-64 flex-1 flex flex-col items-center justify-center h-screen gap-4">
          <AlertCircle className="h-12 w-12 text-red-500" />
          <h2 className="text-xl font-bold text-slate-800">Bir Hata Oluştu</h2>
          <p className="text-slate-500">Projeler yüklenirken bir sorun meydana geldi.</p>
          <Button onClick={() => window.location.reload()}>Tekrar Dene</Button>
        </div>
      </div>
    );
  }

  const handleStatusChange = async (id: number, newStatus: string) => {
    try {
      await updateProject.mutateAsync({ id, status: newStatus as any });
      toast({ title: "Durum Güncellendi", description: `Proje durumu ${newStatus} olarak değiştirildi.` });
    } catch {
      toast({ variant: "destructive", title: "Hata", description: "Durum güncellenemedi." });
    }
  };

  const sortedProjects = [...(projects || [])].sort((a, b) => {
    if (!user) return 0;
    const aOwn = a.expertiseArea === user.expertiseGroup ? -1 : 1;
    const bOwn = b.expertiseArea === user.expertiseGroup ? -1 : 1;
    return aOwn - bOwn;
  });

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      
      <main className="flex-1 ml-0 md:ml-64 p-8 overflow-x-hidden">
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-display font-bold text-slate-900">Projeler</h1>
            <p className="text-slate-500 mt-2">Tüm Ar-Ge projelerinizi buradan yönetin ve takip edin.</p>
          </div>
          {user && canCreateProject(user) && <AddProjectDialog />}
        </header>

        <div className="flex overflow-x-auto pb-8 gap-6 snap-x">
          {statuses.map((status) => {
            const statusProjects = sortedProjects.filter(p => p.status === status);
            
            return (
              <div key={status} className="min-w-[300px] w-[350px] flex-shrink-0 snap-start">
                <div className="flex items-center justify-between mb-4 px-1">
                  <h3 className="font-semibold text-slate-700">{status}</h3>
                  <Badge variant="secondary" className="bg-slate-200 text-slate-700">
                    {statusProjects.length}
                  </Badge>
                </div>

                <div className="space-y-4">
                  {statusProjects.map((project) => {
                    const userCanEdit = user ? canEditProject(user, project) : false;
                    
                    return (
                      <motion.div
                        key={project.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3 }}
                      >
                        <Card className="border shadow-sm hover:shadow-md transition-all group relative bg-white" data-testid={`card-project-${project.id}`}>
                          <CardContent className="p-4">
                            {userCanEdit && (
                              <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                                <DropdownMenu>
                                  <DropdownMenuTrigger asChild>
                                    <Button variant="ghost" size="icon" className="h-8 w-8">
                                      <MoreHorizontal className="h-4 w-4" />
                                    </Button>
                                  </DropdownMenuTrigger>
                                  <DropdownMenuContent align="end">
                                    <DropdownMenuItem onClick={() => handleStatusChange(project.id, "Tamamlandı")}>
                                      Tamamlandı İşaretle
                                    </DropdownMenuItem>
                                    {statuses.filter(s => s !== project.status).map(s => (
                                      <DropdownMenuItem key={s} onClick={() => handleStatusChange(project.id, s)}>
                                        Taşı: {s}
                                      </DropdownMenuItem>
                                    ))}
                                  </DropdownMenuContent>
                                </DropdownMenu>
                              </div>
                            )}

                            <Link href={`/projects/${project.id}`}>
                              <div className="cursor-pointer block">
                                <div className="mb-3">
                                  <Badge variant="outline" className={`mb-2 ${statusColors[project.status]} border bg-opacity-50`}>
                                    {project.expertiseArea}
                                  </Badge>
                                  <h4 className="font-bold text-slate-800 leading-tight mb-1 hover:text-primary transition-colors">
                                    {project.name}
                                  </h4>
                                </div>

                                <div className="flex items-center gap-4 text-xs text-slate-500 mt-4 border-t pt-3">
                                  <div className="flex items-center gap-1">
                                    <User2 className="h-3 w-3" />
                                    <span className="truncate max-w-[80px]">{project.rdSpecialist}</span>
                                  </div>
                                  <div className="flex items-center gap-1 ml-auto">
                                    <Calendar className="h-3 w-3" />
                                    <span>{format(new Date(project.startDate), "d MMM", { locale: tr })}</span>
                                  </div>
                                </div>
                              </div>
                            </Link>
                          </CardContent>
                        </Card>
                      </motion.div>
                    );
                  })}
                  
                  {statusProjects.length === 0 && (
                    <div className="h-24 border-2 border-dashed border-slate-200 rounded-lg flex items-center justify-center text-slate-400 text-sm">
                      Proje Yok
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </main>
    </div>
  );
}
