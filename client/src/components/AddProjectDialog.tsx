import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { insertProjectSchema } from "@shared/schema";
import { useCreateProject } from "@/hooks/use-projects";
import { useAuth } from "@/hooks/use-auth";
import { useUserNames } from "@/hooks/use-users";
import { useToast } from "@/hooks/use-toast";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogDescription
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Plus } from "lucide-react";
import { useState } from "react";
import type { InsertProject } from "@shared/schema";

const expertiseAreas = [
  "Boya/Finish",
  "Hot Melt",
  "Mürekkep",
  "PUD",
  "PU"
];

export function AddProjectDialog() {
  const [open, setOpen] = useState(false);
  const { toast } = useToast();
  const createProject = useCreateProject();
  const { data: user } = useAuth();
  const { data: userNames } = useUserNames();

  const form = useForm<InsertProject>({
    resolver: zodResolver(insertProjectSchema),
    defaultValues: {
      name: "",
      rdSpecialist: user?.name || "",
      expertiseArea: "PU",
      status: "Fikir",
      description: "",
      startDate: new Date().toISOString().split('T')[0],
    },
  });

  async function onSubmit(data: InsertProject) {
    try {
      await createProject.mutateAsync(data);
      toast({
        title: "Başarılı",
        description: "Proje başarıyla oluşturuldu.",
      });
      setOpen(false);
      form.reset({
        name: "",
        rdSpecialist: user?.name || "",
        expertiseArea: "PU",
        status: "Fikir",
        description: "",
        startDate: new Date().toISOString().split('T')[0],
      });
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Hata",
        description: "Proje oluşturulurken bir hata oluştu.",
      });
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => {
      setOpen(v);
      if (v && user?.name) {
        form.setValue("rdSpecialist", user.name);
      }
    }}>
      <DialogTrigger asChild>
        <Button className="bg-primary hover:bg-primary/90 gap-2 shadow-lg shadow-primary/20 hover:shadow-primary/40 transition-all">
          <Plus className="h-4 w-4" /> Yeni Proje
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Yeni Proje Oluştur</DialogTitle>
          <DialogDescription>
            Yeni bir Ar-Ge projesi başlatmak için detayları girin.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 pt-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Proje Adı</FormLabel>
                  <FormControl>
                    <Input placeholder="Örn: Yeni Poliüretan Kaplama" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="expertiseArea"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Uzmanlık Alanı</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Seçiniz" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {expertiseAreas.map(area => (
                          <SelectItem key={area} value={area}>{area}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="rdSpecialist"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Ar-Ge Uzmanı</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger data-testid="select-project-specialist">
                          <SelectValue placeholder="Kişi seçin" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {userNames?.map(u => (
                          <SelectItem key={u.id} value={u.name}>{u.name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="startDate"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Başlangıç Tarihi</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="targetDate"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Hedef Tarih</FormLabel>
                    <FormControl>
                      <Input type="date" value={field.value || ''} onChange={field.onChange} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Açıklama</FormLabel>
                  <FormControl>
                    <Input placeholder="Proje hakkında kısa notlar..." {...field} value={field.value || ''} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="flex justify-end pt-2">
              <Button type="submit" disabled={createProject.isPending}>
                {createProject.isPending ? "Oluşturuluyor..." : "Proje Oluştur"}
              </Button>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
