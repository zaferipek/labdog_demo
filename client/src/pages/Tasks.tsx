import { useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import { useTasks, useCreateTask, useUpdateTask, useDeleteTask } from "@/hooks/use-tasks";
import { useProjects } from "@/hooks/use-projects";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { motion } from "framer-motion";
import {
  Loader2,
  Plus,
  AlertCircle,
  MoreHorizontal,
  Calendar,
  User2,
  CheckCircle2,
  Clock,
  XCircle,
  Trash2,
  FolderOpen,
  Flag,
} from "lucide-react";
import { format } from "date-fns";
import { tr } from "date-fns/locale";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/hooks/use-auth";
import { useUserNames } from "@/hooks/use-users";
import type { Task } from "@shared/schema";

const taskStatuses = ["Beklemede", "Devam Ediyor", "Tamamlandı", "İptal"];
const taskPriorities = ["Düşük", "Orta", "Yüksek", "Acil"];

const statusColors: Record<string, string> = {
  "Beklemede": "bg-slate-100 text-slate-600 border-slate-200",
  "Devam Ediyor": "bg-blue-50 text-blue-700 border-blue-200",
  "Tamamlandı": "bg-emerald-50 text-emerald-700 border-emerald-200",
  "İptal": "bg-red-50 text-red-600 border-red-200",
};

const statusIcons: Record<string, typeof Clock> = {
  "Beklemede": Clock,
  "Devam Ediyor": Loader2,
  "Tamamlandı": CheckCircle2,
  "İptal": XCircle,
};

const priorityColors: Record<string, string> = {
  "Düşük": "bg-slate-100 text-slate-500",
  "Orta": "bg-blue-100 text-blue-600",
  "Yüksek": "bg-amber-100 text-amber-700",
  "Acil": "bg-red-100 text-red-700",
};

function getDefaultDueDate() {
  const d = new Date();
  d.setDate(d.getDate() + 7);
  return d.toISOString().split('T')[0];
}

function AddTaskDialog() {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [projectId, setProjectId] = useState<string>("");
  const [assignee, setAssignee] = useState("");
  const [priority, setPriority] = useState("Orta");
  const [dueDate, setDueDate] = useState(getDefaultDueDate());
  const createTask = useCreateTask();
  const { data: projects } = useProjects();
  const { data: user } = useAuth();
  const { data: userNames } = useUserNames();
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    try {
      await createTask.mutateAsync({
        title: title.trim(),
        description: description.trim() || undefined,
        projectId: projectId ? Number(projectId) : undefined,
        assignee: assignee || undefined,
        priority: priority as any,
        status: "Beklemede",
        dueDate: dueDate || undefined,
      });
      toast({ title: "Görev Oluşturuldu", description: `"${title}" başarıyla eklendi.` });
      setTitle("");
      setDescription("");
      setProjectId("");
      setAssignee(user?.name || "");
      setPriority("Orta");
      setDueDate(getDefaultDueDate());
      setOpen(false);
    } catch {
      toast({ variant: "destructive", title: "Hata", description: "Görev oluşturulamadı." });
    }
  };

  return (
    <Dialog open={open} onOpenChange={(v) => {
      setOpen(v);
      if (v) {
        setAssignee(user?.name || "");
        setDueDate(getDefaultDueDate());
      }
    }}>
      <DialogTrigger asChild>
        <Button className="gap-2" data-testid="button-add-task">
          <Plus className="h-4 w-4" /> Yeni Görev
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Yeni Görev Ekle</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          <div className="space-y-2">
            <Label htmlFor="task-title">Görev Başlığı *</Label>
            <Input
              id="task-title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Görev başlığını girin"
              data-testid="input-task-title"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="task-desc">Açıklama</Label>
            <Textarea
              id="task-desc"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Görev açıklaması"
              rows={3}
              data-testid="input-task-description"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Proje</Label>
              <Select value={projectId} onValueChange={setProjectId}>
                <SelectTrigger data-testid="select-task-project">
                  <SelectValue placeholder="Proje seçin" />
                </SelectTrigger>
                <SelectContent>
                  {projects?.map((p) => (
                    <SelectItem key={p.id} value={String(p.id)}>
                      {p.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Öncelik</Label>
              <Select value={priority} onValueChange={setPriority}>
                <SelectTrigger data-testid="select-task-priority">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {taskPriorities.map((p) => (
                    <SelectItem key={p} value={p}>{p}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Sorumlu</Label>
              <Select value={assignee} onValueChange={setAssignee}>
                <SelectTrigger data-testid="select-task-assignee">
                  <SelectValue placeholder="Kişi seçin" />
                </SelectTrigger>
                <SelectContent>
                  {userNames?.map(u => (
                    <SelectItem key={u.id} value={u.name}>{u.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="task-due">Bitiş Tarihi</Label>
              <Input
                id="task-due"
                type="date"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
                data-testid="input-task-due-date"
              />
            </div>
          </div>
          <Button type="submit" className="w-full" disabled={createTask.isPending} data-testid="button-submit-task">
            {createTask.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
            Görev Oluştur
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function TaskCard({ task, projects }: { task: Task; projects: any[] }) {
  const updateTask = useUpdateTask();
  const deleteTask = useDeleteTask();
  const { toast } = useToast();
  const StatusIcon = statusIcons[task.status] || Clock;
  const linkedProject = projects?.find((p: any) => p.id === task.projectId);

  const handleStatusChange = async (newStatus: string) => {
    try {
      await updateTask.mutateAsync({ id: task.id, data: { status: newStatus as any } });
      toast({ title: "Durum Güncellendi", description: `Görev durumu "${newStatus}" olarak değiştirildi.` });
    } catch {
      toast({ variant: "destructive", title: "Hata", description: "Durum güncellenemedi." });
    }
  };

  const handleDelete = async () => {
    try {
      await deleteTask.mutateAsync(task.id);
      toast({ title: "Görev Silindi" });
    } catch {
      toast({ variant: "destructive", title: "Hata", description: "Görev silinemedi." });
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="border shadow-sm hover:shadow-md transition-all group bg-white" data-testid={`card-task-${task.id}`}>
        <CardContent className="p-4">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2">
                <Badge variant="outline" className={`text-xs ${priorityColors[task.priority]}`}>
                  <Flag className="h-3 w-3 mr-1" />
                  {task.priority}
                </Badge>
                <Badge variant="outline" className={`text-xs ${statusColors[task.status]}`}>
                  <StatusIcon className="h-3 w-3 mr-1" />
                  {task.status}
                </Badge>
              </div>
              <h4 className={`font-semibold text-slate-800 leading-tight mb-1 ${task.status === "Tamamlandı" ? "line-through text-slate-400" : ""}`}>
                {task.title}
              </h4>
              {task.description && (
                <p className="text-sm text-slate-500 line-clamp-2 mt-1">{task.description}</p>
              )}
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity" data-testid={`button-task-menu-${task.id}`}>
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {taskStatuses.filter(s => s !== task.status).map(s => (
                  <DropdownMenuItem key={s} onClick={() => handleStatusChange(s)}>
                    Taşı: {s}
                  </DropdownMenuItem>
                ))}
                <DropdownMenuItem className="text-red-600" onClick={handleDelete}>
                  <Trash2 className="h-4 w-4 mr-2" /> Sil
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          <div className="flex items-center gap-4 text-xs text-slate-500 mt-3 pt-3 border-t">
            {linkedProject && (
              <div className="flex items-center gap-1">
                <FolderOpen className="h-3 w-3" />
                <span className="truncate max-w-[120px]">{linkedProject.name}</span>
              </div>
            )}
            {task.assignee && (
              <div className="flex items-center gap-1">
                <User2 className="h-3 w-3" />
                <span className="truncate max-w-[80px]">{task.assignee}</span>
              </div>
            )}
            {task.dueDate && (
              <div className="flex items-center gap-1 ml-auto">
                <Calendar className="h-3 w-3" />
                <span>{format(new Date(task.dueDate), "d MMM yyyy", { locale: tr })}</span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

export default function Tasks() {
  const { data: tasks, isLoading, error } = useTasks();
  const { data: projects } = useProjects();
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [filterPriority, setFilterPriority] = useState<string>("all");
  const [search, setSearch] = useState("");

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
          <p className="text-slate-500">Görevler yüklenirken bir sorun meydana geldi.</p>
          <Button onClick={() => window.location.reload()}>Tekrar Dene</Button>
        </div>
      </div>
    );
  }

  const filteredTasks = (tasks || []).filter((t) => {
    if (filterStatus !== "all" && t.status !== filterStatus) return false;
    if (filterPriority !== "all" && t.priority !== filterPriority) return false;
    if (search && !t.title.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const counts = {
    total: tasks?.length || 0,
    pending: tasks?.filter(t => t.status === "Beklemede").length || 0,
    inProgress: tasks?.filter(t => t.status === "Devam Ediyor").length || 0,
    done: tasks?.filter(t => t.status === "Tamamlandı").length || 0,
  };

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />

      <main className="flex-1 ml-0 md:ml-64 p-8 overflow-x-hidden">
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-display font-bold text-slate-900" data-testid="text-tasks-title">Görevler</h1>
            <p className="text-slate-500 mt-2">Projelerinize bağlı görevlerinizi yönetin ve takip edin.</p>
          </div>
          <AddTaskDialog />
        </header>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <Card className="border bg-white">
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-slate-800" data-testid="text-tasks-total">{counts.total}</p>
              <p className="text-xs text-slate-500">Toplam</p>
            </CardContent>
          </Card>
          <Card className="border bg-white">
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-slate-600" data-testid="text-tasks-pending">{counts.pending}</p>
              <p className="text-xs text-slate-500">Beklemede</p>
            </CardContent>
          </Card>
          <Card className="border bg-white">
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-blue-600" data-testid="text-tasks-progress">{counts.inProgress}</p>
              <p className="text-xs text-slate-500">Devam Ediyor</p>
            </CardContent>
          </Card>
          <Card className="border bg-white">
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-emerald-600" data-testid="text-tasks-done">{counts.done}</p>
              <p className="text-xs text-slate-500">Tamamlandı</p>
            </CardContent>
          </Card>
        </div>

        <div className="flex flex-col md:flex-row gap-3 mb-6">
          <Input
            placeholder="Görev ara..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="md:max-w-xs bg-white"
            data-testid="input-task-search"
          />
          <Select value={filterStatus} onValueChange={setFilterStatus}>
            <SelectTrigger className="md:w-[180px] bg-white" data-testid="select-filter-status">
              <SelectValue placeholder="Durum filtrele" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tüm Durumlar</SelectItem>
              {taskStatuses.map((s) => (
                <SelectItem key={s} value={s}>{s}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={filterPriority} onValueChange={setFilterPriority}>
            <SelectTrigger className="md:w-[180px] bg-white" data-testid="select-filter-priority">
              <SelectValue placeholder="Öncelik filtrele" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tüm Öncelikler</SelectItem>
              {taskPriorities.map((p) => (
                <SelectItem key={p} value={p}>{p}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {filteredTasks.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <CheckCircle2 className="h-16 w-16 text-slate-300 mb-4" />
            <h3 className="text-lg font-semibold text-slate-600">Görev Bulunamadı</h3>
            <p className="text-slate-400 mt-1">Yeni bir görev ekleyerek başlayın.</p>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredTasks.map((task) => (
              <TaskCard key={task.id} task={task} projects={projects || []} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
