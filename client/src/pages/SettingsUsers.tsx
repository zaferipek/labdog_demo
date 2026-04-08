import { Sidebar } from "@/components/Sidebar";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/hooks/use-auth";
import { useUsers, useCreateUser, useUpdateUser, useDeleteUser } from "@/hooks/use-users";
import { canAccessSettings, roleLabels } from "@/lib/permissions";
import { Shield, Loader2, Plus, Trash2, ArrowLeft } from "lucide-react";
import { useState, useEffect } from "react";
import { expertiseAreas, userRoles } from "@shared/schema";
import { Link, useLocation } from "wouter";

function AddUserDialog() {
  const [open, setOpen] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [role, setRole] = useState<string>("Ar-Ge Uzmanı");
  const [expertiseGroup, setExpertiseGroup] = useState("Boya/Finish");
  const createUser = useCreateUser();
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password.trim() || !name.trim()) return;
    try {
      await createUser.mutateAsync({
        username: username.trim(),
        password: password.trim(),
        name: name.trim(),
        role: role as any,
        expertiseGroup: expertiseGroup as any,
      });
      toast({ title: "Kullanıcı Oluşturuldu", description: `"${name}" başarıyla eklendi.` });
      setUsername("");
      setPassword("");
      setName("");
      setRole("Ar-Ge Uzmanı");
      setExpertiseGroup("Boya/Finish");
      setOpen(false);
    } catch {
      toast({ variant: "destructive", title: "Hata", description: "Kullanıcı oluşturulamadı. Kullanıcı adı zaten kullanılıyor olabilir." });
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="gap-2" data-testid="button-add-user">
          <Plus className="h-4 w-4" /> Yeni Kullanıcı
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[450px]">
        <DialogHeader>
          <DialogTitle>Yeni Kullanıcı Ekle</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          <div className="space-y-2">
            <Label htmlFor="new-username">Kullanıcı Adı *</Label>
            <Input id="new-username" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="kullanici_adi" data-testid="input-new-username" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="new-password">Şifre *</Label>
            <Input id="new-password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Şifre" data-testid="input-new-password" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="new-name">Ad Soyad *</Label>
            <Input id="new-name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Ad Soyad" data-testid="input-new-name" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Rol</Label>
              <Select value={role} onValueChange={setRole}>
                <SelectTrigger data-testid="select-new-role">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {userRoles.map((r) => (
                    <SelectItem key={r} value={r}>{roleLabels[r] || r}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Uzmanlık Grubu</Label>
              <Select value={expertiseGroup} onValueChange={setExpertiseGroup}>
                <SelectTrigger data-testid="select-new-expertise">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {expertiseAreas.map((a) => (
                    <SelectItem key={a} value={a}>{a}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <Button type="submit" className="w-full" disabled={createUser.isPending} data-testid="button-submit-user">
            {createUser.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
            Kullanıcı Oluştur
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export default function SettingsUsers() {
  const { data: user, isLoading: isAuthLoading } = useAuth();
  const [, setLocation] = useLocation();
  const { data: users, isLoading: isUsersLoading } = useUsers();
  const updateUser = useUpdateUser();
  const deleteUser = useDeleteUser();
  const { toast } = useToast();

  useEffect(() => {
    if (!isAuthLoading && user && !canAccessSettings(user)) {
      setLocation("/");
    }
  }, [user, isAuthLoading, setLocation]);

  const handleRoleChange = async (userId: number, newRole: string) => {
    try {
      await updateUser.mutateAsync({ id: userId, data: { role: newRole as any } });
      toast({ title: "Rol Güncellendi" });
    } catch {
      toast({ variant: "destructive", title: "Hata", description: "Rol güncellenemedi." });
    }
  };

  const handleExpertiseChange = async (userId: number, newGroup: string) => {
    try {
      await updateUser.mutateAsync({ id: userId, data: { expertiseGroup: newGroup as any } });
      toast({ title: "Uzmanlık Grubu Güncellendi" });
    } catch {
      toast({ variant: "destructive", title: "Hata", description: "Uzmanlık grubu güncellenemedi." });
    }
  };

  const handleDelete = async (userId: number, userName: string) => {
    try {
      await deleteUser.mutateAsync(userId);
      toast({ title: "Kullanıcı Silindi", description: `"${userName}" silindi.` });
    } catch {
      toast({ variant: "destructive", title: "Hata", description: "Kullanıcı silinemedi." });
    }
  };

  if (isAuthLoading || isUsersLoading) {
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
          <div className="flex-1">
            <h1 className="text-3xl font-display font-bold text-slate-900">Kullanıcı Yönetimi</h1>
            <p className="text-slate-500 mt-1">Kullanıcı rolleri ve uzmanlık gruplarını yönetin.</p>
          </div>
          <AddUserDialog />
        </div>

        <div className="max-w-5xl">
          <Card className="border-none shadow-md">
            <CardHeader className="flex flex-row items-center gap-4">
              <div className="h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600">
                <Shield className="h-6 w-6" />
              </div>
              <div>
                <CardTitle>Yetki Matrisi</CardTitle>
                <CardDescription>Kullanıcıların rollerini ve uzmanlık gruplarını düzenleyin.</CardDescription>
              </div>
            </CardHeader>
            <CardContent>
              <div className="rounded-lg border overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-slate-50">
                      <TableHead className="font-semibold">Kullanıcı Adı</TableHead>
                      <TableHead className="font-semibold">Ad Soyad</TableHead>
                      <TableHead className="font-semibold">Rol</TableHead>
                      <TableHead className="font-semibold">Uzmanlık Grubu</TableHead>
                      <TableHead className="font-semibold w-[80px]"></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {(users || []).map((u: any) => {
                      const isSelf = user?.id === u.id;
                      return (
                        <TableRow key={u.id} data-testid={`row-user-${u.id}`}>
                          <TableCell className="font-mono text-sm">{u.username}</TableCell>
                          <TableCell>{u.name}</TableCell>
                          <TableCell>
                            <Select value={u.role} onValueChange={(val) => handleRoleChange(u.id, val)} disabled={isSelf}>
                              <SelectTrigger className="w-[180px] h-8 text-sm" data-testid={`select-role-${u.id}`}>
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                {userRoles.map((r) => (
                                  <SelectItem key={r} value={r}>{roleLabels[r] || r}</SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </TableCell>
                          <TableCell>
                            <Select value={u.expertiseGroup} onValueChange={(val) => handleExpertiseChange(u.id, val)}>
                              <SelectTrigger className="w-[140px] h-8 text-sm" data-testid={`select-expertise-${u.id}`}>
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                {expertiseAreas.map((a) => (
                                  <SelectItem key={a} value={a}>{a}</SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </TableCell>
                          <TableCell>
                            {!isSelf && (
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 text-red-500 hover:text-red-700 hover:bg-red-50"
                                onClick={() => handleDelete(u.id, u.name)}
                                data-testid={`button-delete-user-${u.id}`}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            )}
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
