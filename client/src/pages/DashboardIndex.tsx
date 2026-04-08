import { Sidebar } from "@/components/Sidebar";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Link } from "wouter";
import { LayoutDashboard, BarChart3, PieChart, Activity, ArrowRight } from "lucide-react";

export default function DashboardIndex() {
  const dashboards = [
    {
      id: "management",
      title: "Yönetim Bakışı",
      description: "Genel proje durumları, uzmanlık alanlarına göre dağılım ve son aktiviteler.",
      icon: LayoutDashboard,
      href: "/dashboard/management",
      color: "text-blue-600",
      bgColor: "bg-blue-50"
    },
    {
      id: "performance",
      title: "Ar-Ge Performans Analizi",
      description: "Deney başarı oranları, test yoğunluğu ve laboratuvar verimlilik metrikleri.",
      icon: BarChart3,
      href: "/dashboard/performance",
      color: "text-purple-600",
      bgColor: "bg-purple-50"
    }
  ];

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      <main className="flex-1 ml-0 md:ml-64 p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-display font-bold text-slate-900">Dashboardlar</h1>
          <p className="text-slate-500 mt-1">Analiz etmek istediğiniz veri görünümünü seçin.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-5xl">
          {dashboards.map((dash) => (
            <Link key={dash.id} href={dash.href}>
              <Card className="group border-none shadow-md hover:shadow-xl transition-all duration-300 cursor-pointer overflow-hidden">
                <CardHeader className="pb-4">
                  <div className={`h-12 w-12 ${dash.bgColor} ${dash.color} rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
                    <dash.icon className="h-6 w-6" />
                  </div>
                  <CardTitle className="text-xl group-hover:text-primary transition-colors">{dash.title}</CardTitle>
                  <CardDescription className="text-slate-500 leading-relaxed">
                    {dash.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center text-sm font-semibold text-primary gap-1 group-hover:gap-2 transition-all">
                    Görüntüle <ArrowRight className="h-4 w-4" />
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
