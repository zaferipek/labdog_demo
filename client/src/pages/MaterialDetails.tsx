import { Sidebar } from "@/components/Sidebar";
import { useMaterial, useMaterialEquivalents, useUpdateMaterial, useUploadMaterialDoc } from "@/hooks/use-materials";
import { useRoute, Link } from "wouter";
import { Loader2, ArrowLeft, Database, Factory, Tag, FileText, ShieldAlert, Package, Save, Upload, X, Pencil, Calendar, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { insertRawMaterialSchema, materialApprovalStatuses, type InsertRawMaterial } from "@shared/schema";
import { useToast } from "@/hooks/use-toast";
import { useState, useRef } from "react";

const approvalColors: Record<string, string> = {
  "Onaylı": "bg-green-100 text-green-700 border-green-200",
  "Onaysız": "bg-red-100 text-red-700 border-red-200",
  "Testte": "bg-amber-100 text-amber-700 border-amber-200",
  "Yolda": "bg-blue-100 text-blue-700 border-blue-200",
};

export default function MaterialDetails() {
  const [, params] = useRoute("/materials/:id");
  const id = params ? parseInt(params.id) : 0;
  
  const { data: material, isLoading: isMaterialLoading } = useMaterial(id);
  const { data: equivalents, isLoading: isEquivalentsLoading } = useMaterialEquivalents(id);
  const [editOpen, setEditOpen] = useState(false);

  if (isMaterialLoading || isEquivalentsLoading) {
    return (
      <div className="flex min-h-screen bg-slate-50 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!material) {
    return (
      <div className="flex min-h-screen bg-slate-50 items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-bold">Hammadde bulunamadı</h2>
          <Link href="/materials">
            <Button variant="link">Listeye geri dön</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      <main className="flex-1 ml-0 md:ml-64 p-8">
        <div className="flex items-center gap-4 mb-8">
          <Link href="/materials">
            <Button variant="ghost" size="icon" className="rounded-full" data-testid="button-back-materials">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-display font-bold text-slate-900" data-testid="text-material-name">{material.name}</h1>
              <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                {material.function}
              </Badge>
              <Badge variant="outline" className={approvalColors[material.approvalStatus] || ""} data-testid="status-material-approval">
                {material.approvalStatus}
              </Badge>
            </div>
            <p className="text-slate-500 mt-1">{material.supplier}{material.brand ? ` — ${material.brand}` : ""}</p>
          </div>
          <Button className="gap-2" onClick={() => setEditOpen(true)} data-testid="button-edit-material">
            <Pencil className="h-4 w-4" /> Düzenle
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <Card className="border-none shadow-md">
              <CardHeader>
                <CardTitle>Genel Bilgiler</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-1">
                  <p className="text-sm font-medium text-slate-500 flex items-center gap-2">
                    <Tag className="h-4 w-4" /> CAS Numarası
                  </p>
                  <p className="text-slate-900 font-mono" data-testid="text-cas-number">{material.casNumber || "Belirtilmemiş"}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-slate-500 flex items-center gap-2">
                    <Package className="h-4 w-4" /> Stok Durumu
                  </p>
                  <p className="text-slate-900">{material.stockQuantity || "0"} {material.unit || "kg"}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-slate-500 flex items-center gap-2">
                    <Factory className="h-4 w-4" /> Üretici/Tedarikçi
                  </p>
                  <p className="text-slate-900">{material.supplier}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-slate-500 flex items-center gap-2">
                    <Tag className="h-4 w-4" /> Marka
                  </p>
                  <p className="text-slate-900" data-testid="text-brand">{material.brand || "Belirtilmemiş"}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-slate-500 flex items-center gap-2">
                    <Calendar className="h-4 w-4" /> Geliş Tarihi
                  </p>
                  <p className="text-slate-900" data-testid="text-arrival-date">{material.arrivalDate || "Belirtilmemiş"}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-slate-500 flex items-center gap-2">
                    <CheckCircle className="h-4 w-4" /> Onay Durumu
                  </p>
                  <Badge variant="outline" className={approvalColors[material.approvalStatus] || ""}>
                    {material.approvalStatus}
                  </Badge>
                </div>
              </CardContent>
            </Card>

            <Card className="border-none shadow-md">
              <CardHeader>
                <CardTitle>Teknik Belgeler</CardTitle>
                <CardDescription>TDS ve MSDS dosyalarını yükleyin veya görüntüleyin.</CardDescription>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <DocumentUploadSection
                  materialId={id}
                  docType="tds"
                  label="Teknik Veri Sayfası (TDS)"
                  currentUrl={material.tdsUrl}
                />
                <DocumentUploadSection
                  materialId={id}
                  docType="sds"
                  label="Güvenlik Bilgi Formu (MSDS)"
                  currentUrl={material.safetyDataSheetUrl}
                />
              </CardContent>
            </Card>

            <Card className="border-none shadow-md">
              <CardHeader>
                <CardTitle>Teknik Notlar</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-slate-700 bg-slate-50 p-4 rounded-xl border border-slate-100 min-h-[100px]">
                  {material.notes || "Hammadde hakkında teknik not bulunmuyor."}
                </p>
              </CardContent>
            </Card>

            <Card className="border-none shadow-md">
              <CardHeader>
                <CardTitle>Muadil Hammaddeler</CardTitle>
                <CardDescription>Bu hammadde yerine kullanılabilecek alternatifler.</CardDescription>
              </CardHeader>
              <CardContent>
                {equivalents && equivalents.length > 0 ? (
                  <div className="space-y-4">
                    {equivalents.map(eq => (
                      <Link key={eq.id} href={`/materials/${eq.id}`}>
                        <div className="flex items-center justify-between p-4 rounded-xl border border-slate-100 hover:border-primary hover:bg-blue-50/30 transition-all cursor-pointer group">
                          <div className="flex items-center gap-4">
                            <div className="h-10 w-10 bg-white shadow-sm rounded-lg flex items-center justify-center text-blue-600">
                              <Database className="h-5 w-5" />
                            </div>
                            <div>
                              <p className="font-semibold text-slate-900 group-hover:text-primary transition-colors">{eq.name}</p>
                              <p className="text-xs text-slate-500">{eq.supplier}</p>
                            </div>
                          </div>
                          <Badge variant="secondary" className="bg-white border">
                            {eq.function}
                          </Badge>
                        </div>
                      </Link>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-slate-400 italic bg-slate-50/50 rounded-xl border border-dashed">
                    Henüz muadil hammadde tanımlanmamış.
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          <div className="space-y-8">
            <Card className="border-none shadow-md bg-primary text-white">
              <CardHeader>
                <CardTitle className="text-lg">Kullanım İstatistikleri</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center border-b border-white/10 pb-2">
                  <span className="text-sm text-blue-100">Aktif Projeler</span>
                  <span className="text-xl font-bold">4</span>
                </div>
                <div className="flex justify-between items-center border-b border-white/10 pb-2">
                  <span className="text-sm text-blue-100">Toplam Deney</span>
                  <span className="text-xl font-bold">12</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-blue-100">Son Kullanım</span>
                  <span className="text-sm font-medium">12.02.2026</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        <EditMaterialDialog
          material={material}
          open={editOpen}
          onOpenChange={setEditOpen}
        />
      </main>
    </div>
  );
}

function DocumentUploadSection({ materialId, docType, label, currentUrl }: {
  materialId: number;
  docType: "sds" | "tds";
  label: string;
  currentUrl: string | null;
}) {
  const { toast } = useToast();
  const uploadDoc = useUploadMaterialDoc();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      await uploadDoc.mutateAsync({ id: materialId, docType, file });
      toast({ title: "Başarılı", description: `${label} yüklendi.` });
    } catch {
      toast({ variant: "destructive", title: "Hata", description: "Dosya yükleme başarısız." });
    }
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className="space-y-3 p-4 rounded-xl border border-slate-100 bg-slate-50/50">
      <div className="flex items-center gap-2">
        {docType === "tds" ? <FileText className="h-4 w-4 text-blue-600" /> : <ShieldAlert className="h-4 w-4 text-amber-600" />}
        <p className="text-sm font-medium text-slate-700">{label}</p>
      </div>
      {currentUrl ? (
        <div className="flex items-center gap-2">
          <a href={`/api/materials/${materialId}/doc/${docType}`} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline flex items-center gap-1 text-sm" data-testid={`link-${docType}-view`}>
            <FileText className="h-4 w-4" /> Belgeyi Görüntüle
          </a>
        </div>
      ) : (
        <p className="text-slate-400 italic text-sm">Dosya yüklenmemiş</p>
      )}
      <div>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg"
          className="hidden"
          onChange={handleUpload}
          data-testid={`input-upload-${docType}`}
        />
        <Button
          variant="outline"
          size="sm"
          className="gap-2"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploadDoc.isPending}
          data-testid={`button-upload-${docType}`}
        >
          {uploadDoc.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Upload className="h-4 w-4" />
          )}
          {currentUrl ? "Yeniden Yükle" : "Dosya Yükle"}
        </Button>
      </div>
    </div>
  );
}

function EditMaterialDialog({ material, open, onOpenChange }: {
  material: any;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const { toast } = useToast();
  const updateMaterial = useUpdateMaterial();

  const form = useForm<InsertRawMaterial>({
    resolver: zodResolver(insertRawMaterialSchema),
    defaultValues: {
      name: material.name || "",
      supplier: material.supplier || "",
      brand: material.brand || "",
      function: material.function || "",
      casNumber: material.casNumber || "",
      stockQuantity: material.stockQuantity || "0",
      unit: material.unit || "kg",
      arrivalDate: material.arrivalDate || "",
      approvalStatus: material.approvalStatus || "Onaysız",
      notes: material.notes || "",
    },
  });

  async function onSubmit(data: InsertRawMaterial) {
    try {
      const cleaned = { ...data };
      if (!cleaned.arrivalDate) delete (cleaned as any).arrivalDate;
      if (!cleaned.brand) delete (cleaned as any).brand;
      if (!cleaned.casNumber) delete (cleaned as any).casNumber;
      await updateMaterial.mutateAsync({ id: material.id, data: cleaned });
      toast({ title: "Başarılı", description: "Hammadde güncellendi." });
      onOpenChange(false);
    } catch {
      toast({ variant: "destructive", title: "Hata", description: "Güncelleme başarısız." });
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Hammadde Düzenle</DialogTitle>
          <DialogDescription>Hammadde bilgilerini güncelleyin.</DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 pt-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Hammadde Adı</FormLabel>
                  <FormControl><Input {...field} data-testid="input-edit-material-name" /></FormControl>
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
                    <FormControl><Input {...field} data-testid="input-edit-material-supplier" /></FormControl>
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
                    <FormControl><Input {...field} value={field.value || ''} data-testid="input-edit-material-brand" /></FormControl>
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
                    <FormControl><Input {...field} data-testid="input-edit-material-function" /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="casNumber"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>CAS Numarası</FormLabel>
                    <FormControl><Input {...field} value={field.value || ''} data-testid="input-edit-material-cas" /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="stockQuantity"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Stok Miktarı</FormLabel>
                    <FormControl><Input {...field} value={field.value || ''} data-testid="input-edit-material-stock" /></FormControl>
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
                    <FormControl><Input {...field} value={field.value || ''} data-testid="input-edit-material-unit" /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="approvalStatus"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Onay Durumu</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger data-testid="select-edit-material-approval">
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
              <FormField
                control={form.control}
                name="arrivalDate"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Geliş Tarihi</FormLabel>
                    <FormControl><Input type="date" {...field} value={field.value || ''} data-testid="input-edit-material-arrival" /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <FormField
              control={form.control}
              name="notes"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Notlar</FormLabel>
                  <FormControl><Textarea {...field} value={field.value || ''} rows={3} data-testid="input-edit-material-notes" /></FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit" className="w-full" disabled={updateMaterial.isPending} data-testid="button-submit-edit-material">
              {updateMaterial.isPending ? "Kaydediliyor..." : "Güncelle"}
            </Button>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
