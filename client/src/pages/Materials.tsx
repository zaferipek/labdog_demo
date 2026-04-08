import { Sidebar } from "@/components/Sidebar";
import { useMaterials, useCreateMaterial } from "@/hooks/use-materials";
import { Loader2, Plus, Search, Filter, Database, Factory, Tag } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription } from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { insertRawMaterialSchema, materialApprovalStatuses, type InsertRawMaterial } from "@shared/schema";
import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Link } from "wouter";

const approvalColors: Record<string, string> = {
  "Onaylı": "bg-green-100 text-green-700 border-green-200",
  "Onaysız": "bg-red-100 text-red-700 border-red-200",
  "Testte": "bg-amber-100 text-amber-700 border-amber-200",
  "Yolda": "bg-blue-100 text-blue-700 border-blue-200",
};

export default function Materials() {
  const { data: materials, isLoading } = useMaterials();
  const [searchTerm, setSearchTerm] = useState("");

  const filteredMaterials = materials?.filter(m => 
    m.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    m.function.toLowerCase().includes(searchTerm.toLowerCase()) ||
    m.supplier.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (m.brand && m.brand.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (isLoading) {
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
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-display font-bold text-slate-900" data-testid="text-page-title">Hammadde Kütüphanesi</h1>
            <p className="text-slate-500 mt-2">Laboratuvar envanterindeki tüm hammaddeler ve muadilleri.</p>
          </div>
          <AddMaterialDialog />
        </header>

        <Card className="border-none shadow-md overflow-hidden">
          <CardHeader className="bg-white border-b pb-4">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <Input 
                  placeholder="Hammadde, tedarikçi, marka veya fonksiyon ara..." 
                  className="pl-10 bg-slate-50 border-slate-200 focus:bg-white transition-all"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  data-testid="input-search-materials"
                />
              </div>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" className="gap-2 text-slate-600">
                  <Filter className="h-4 w-4" /> Filtrele
                </Button>
                <Badge variant="secondary" className="bg-slate-100 text-slate-600 px-3 py-1" data-testid="text-material-count">
                  Toplam: {filteredMaterials?.length || 0}
                </Badge>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader className="bg-slate-50/50">
                  <TableRow>
                    <TableHead className="font-semibold text-slate-700 w-[200px]">Hammadde Adı</TableHead>
                    <TableHead className="font-semibold text-slate-700">Marka</TableHead>
                    <TableHead className="font-semibold text-slate-700">Tedarikçi</TableHead>
                    <TableHead className="font-semibold text-slate-700">Fonksiyon</TableHead>
                    <TableHead className="font-semibold text-slate-700">Durum</TableHead>
                    <TableHead className="font-semibold text-slate-700">TDS</TableHead>
                    <TableHead className="font-semibold text-slate-700">MSDS</TableHead>
                    <TableHead className="font-semibold text-slate-700">Geliş Tarihi</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredMaterials && filteredMaterials.length > 0 ? (
                    filteredMaterials.map((material) => (
                      <TableRow key={material.id} className="hover:bg-slate-50/80 transition-colors" data-testid={`row-material-${material.id}`}>
                        <TableCell className="font-medium">
                          <Link href={`/materials/${material.id}`}>
                            <div className="flex items-center gap-3 cursor-pointer hover:text-primary transition-colors">
                              <div className="h-8 w-8 bg-blue-50 text-blue-600 rounded flex items-center justify-center">
                                <Database className="h-4 w-4" />
                              </div>
                              {material.name}
                            </div>
                          </Link>
                        </TableCell>
                        <TableCell>
                          <span className="text-sm text-slate-600">
                            {material.brand || "-"}
                          </span>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2 text-slate-600 text-sm">
                            <Factory className="h-3.5 w-3.5" />
                            {material.supplier}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="font-normal bg-slate-50">
                            {material.function}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className={approvalColors[material.approvalStatus] || ""} data-testid={`status-material-${material.id}`}>
                            {material.approvalStatus}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {material.tdsUrl ? (
                            <a href={`/api/materials/${material.id}/doc/tds`} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline text-sm" data-testid={`link-tds-${material.id}`}>
                              Görüntüle
                            </a>
                          ) : (
                            <span className="text-slate-400 text-sm">-</span>
                          )}
                        </TableCell>
                        <TableCell>
                          {material.safetyDataSheetUrl ? (
                            <a href={`/api/materials/${material.id}/doc/sds`} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline text-sm" data-testid={`link-sds-${material.id}`}>
                              Görüntüle
                            </a>
                          ) : (
                            <span className="text-slate-400 text-sm">-</span>
                          )}
                        </TableCell>
                        <TableCell>
                          <span className="text-sm text-slate-600">
                            {material.arrivalDate || "-"}
                          </span>
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={8} className="h-32 text-center text-slate-400 italic">
                        Sonuç bulunamadı.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}

function AddMaterialDialog() {
  const [open, setOpen] = useState(false);
  const { toast } = useToast();
  const createMaterial = useCreateMaterial();
  
  const form = useForm<InsertRawMaterial>({
    resolver: zodResolver(insertRawMaterialSchema),
    defaultValues: {
      name: "",
      supplier: "",
      brand: "",
      function: "",
      notes: "",
      arrivalDate: "",
      approvalStatus: "Onaysız",
    },
  });

  async function onSubmit(data: InsertRawMaterial) {
    try {
      const cleaned = { ...data };
      if (!cleaned.arrivalDate) delete (cleaned as any).arrivalDate;
      if (!cleaned.brand) delete (cleaned as any).brand;
      await createMaterial.mutateAsync(cleaned);
      toast({ title: "Başarılı", description: "Hammadde eklendi." });
      setOpen(false);
      form.reset();
    } catch {
      toast({ variant: "destructive", title: "Hata", description: "Ekleme başarısız." });
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="bg-primary hover:bg-primary/90 gap-2 shadow-lg shadow-primary/20" data-testid="button-add-material">
          <Plus className="h-4 w-4" /> Yeni Hammadde
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Yeni Hammadde Ekle</DialogTitle>
          <DialogDescription>Envantere yeni bir kimyasal giriş yapın.</DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 pt-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Hammadde Adı</FormLabel>
                  <FormControl><Input placeholder="Örn: Butyl Acetate" {...field} data-testid="input-material-name" /></FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="supplier"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Tedarikçi</FormLabel>
                    <FormControl><Input placeholder="Firma Adı" {...field} data-testid="input-material-supplier" /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="brand"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Marka</FormLabel>
                    <FormControl><Input placeholder="Marka Adı" {...field} value={field.value || ''} data-testid="input-material-brand" /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="function"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Fonksiyon</FormLabel>
                    <FormControl><Input placeholder="Örn: Çözücü, Bağlayıcı" {...field} data-testid="input-material-function" /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="approvalStatus"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Onay Durumu</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger data-testid="select-material-approval">
                          <SelectValue placeholder="Durum seçin" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {materialApprovalStatuses.map(s => (
                          <SelectItem key={s} value={s}>{s}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <FormField
              control={form.control}
              name="arrivalDate"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Geliş Tarihi</FormLabel>
                  <FormControl><Input type="date" {...field} value={field.value || ''} data-testid="input-material-arrival-date" /></FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="notes"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Notlar (Opsiyonel)</FormLabel>
                  <FormControl><Input {...field} value={field.value || ''} data-testid="input-material-notes" /></FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit" className="w-full" disabled={createMaterial.isPending} data-testid="button-submit-material">
              {createMaterial.isPending ? "Kaydediliyor..." : "Kaydet"}
            </Button>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
