import { Sidebar } from "@/components/Sidebar";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/use-auth";
import { canAccessSettings } from "@/lib/permissions";
import { BrainCircuit, Shield, ChevronRight, Loader2 } from "lucide-react";
import { useEffect } from "react";
import { Link, useLocation } from "wouter";

const settingsLinks = [
  {
    href: "/settings/ai",
    icon: BrainCircuit,
    iconBg: "bg-purple-100 text-purple-600",
    title: "Yapay Zeka Yapılandırması",
    description: "AI analiz parametreleri, API uç noktası ve sistem komutunu düzenleyin.",
  },
  {
    href: "/settings/users",
    icon: Shield,
    iconBg: "bg-blue-100 text-blue-600",
    title: "Kullanıcı Yönetimi",
    description: "Kullanıcı rolleri, uzmanlık grupları ve yetki matrisini yönetin.",
  },
];

export default function Settings() {
  const { data: user, isLoading } = useAuth();
  const [, setLocation] = useLocation();

  useEffect(() => {
    if (!isLoading && user && !canAccessSettings(user)) {
      setLocation("/");
    }
  }, [user, isLoading, setLocation]);

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
        <div className="mb-8">
          <h1 className="text-3xl font-display font-bold text-slate-900">Ayarlar</h1>
          <p className="text-slate-500 mt-1">Sistem yapılandırması ve yönetim araçları.</p>
        </div>

        <div className="max-w-3xl space-y-4">
          {settingsLinks.map((item) => (
            <Link key={item.href} href={item.href}>
              <Card className="border shadow-sm hover:shadow-md transition-all cursor-pointer group" data-testid={`link-${item.href.split("/").pop()}`}>
                <CardContent className="flex items-center gap-5 p-6">
                  <div className={`h-12 w-12 rounded-xl flex items-center justify-center shrink-0 ${item.iconBg}`}>
                    <item.icon className="h-6 w-6" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-slate-800 group-hover:text-primary transition-colors">{item.title}</h3>
                    <p className="text-sm text-slate-500 mt-0.5">{item.description}</p>
                  </div>
                  <ChevronRight className="h-5 w-5 text-slate-400 group-hover:text-primary transition-colors shrink-0" />
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
