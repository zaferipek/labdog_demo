import { Sidebar } from "@/components/Sidebar";
import { useStats } from "@/hooks/use-stats";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, PieChart, Pie, LineChart, Line } from "recharts";
import { Loader2, ArrowLeft, TrendingUp, CheckCircle2, FlaskConical, AlertCircle } from "lucide-react";
import { Link } from "wouter";
import { Button } from "@/components/ui/button";

export default function PerformanceDashboard() {
  const { data: stats, isLoading } = useStats();

  if (isLoading) {
    return (
      <div className="flex min-h-screen bg-slate-50 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  // Mock performance data based on existing stats
  const performanceData = stats?.map(s => ({
    name: s.expertiseArea,
    successRate: Math.floor(Math.random() * 30) + 60, // 60-90% success rate
    expCount: s.count * 3 + Math.floor(Math.random() * 5),
    efficiency: Math.floor(Math.random() * 20) + 75
  })) || [];

  const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      <main className="flex-1 ml-0 md:ml-64 p-8">
        <div className="flex items-center gap-4 mb-8">
          <Link href="/">
            <Button variant="ghost" size="icon" className="rounded-full">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-display font-bold text-slate-900">Ar-Ge Performans Analizi</h1>
            <p className="text-slate-500 mt-1">Laboratuvar verimliliği ve başarı metrikleri.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="border-none shadow-sm">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" /> Ortalama Başarı Oranı
              </CardDescription>
              <CardTitle className="text-3xl font-bold">78%</CardTitle>
            </CardHeader>
          </Card>
          <Card className="border-none shadow-sm">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <FlaskConical className="h-4 w-4 text-blue-500" /> Haftalık Deney Sayısı
              </CardDescription>
              <CardTitle className="text-3xl font-bold">24</CardTitle>
            </CardHeader>
          </Card>
          <Card className="border-none shadow-sm">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-purple-500" /> Verimlilik Artışı
              </CardDescription>
              <CardTitle className="text-3xl font-bold">+12%</CardTitle>
            </CardHeader>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card className="border-none shadow-md">
            <CardHeader>
              <CardTitle>Bölüm Bazlı Başarı Oranları (%)</CardTitle>
            </CardHeader>
            <CardContent className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} />
                  <Tooltip 
                    contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)'}}
                  />
                  <Bar dataKey="successRate" radius={[4, 4, 0, 0]}>
                    {performanceData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card className="border-none shadow-md">
            <CardHeader>
              <CardTitle>Laboratuvar Yoğunluğu (Deney Sayısı)</CardTitle>
            </CardHeader>
            <CardContent className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={performanceData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="expCount"
                  >
                    {performanceData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
