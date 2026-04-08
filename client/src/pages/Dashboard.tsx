import { Sidebar } from "@/components/Sidebar";
import { useStats } from "@/hooks/use-stats";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { motion } from "framer-motion";
import { Loader2, Beaker, FileText, CheckCircle2, FlaskConical, Droplet, Layers } from "lucide-react";
import { format } from "date-fns";
import { tr } from "date-fns/locale";

const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const item = {
  hidden: { y: 20, opacity: 0 },
  show: { y: 0, opacity: 1 }
};

export default function Dashboard() {
  const { data: stats, isLoading } = useStats();

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

  // Calculate total projects
  const totalProjects = stats?.reduce((acc, curr) => acc + curr.count, 0) || 0;

  // Flatten recent projects for activity feed
  const recentProjects = stats
    ?.flatMap(s => s.projects)
    .sort((a, b) => new Date(b.createdAt!).getTime() - new Date(a.createdAt!).getTime())
    .slice(0, 5) || [];

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      
      <main className="flex-1 ml-0 md:ml-64 p-8 overflow-y-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-display font-bold text-slate-900">Hoş Geldiniz</h1>
          <p className="text-slate-500 mt-2">Ar-Ge projelerinizin genel durumu ve istatistikleri.</p>
        </header>

        <motion.div 
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          {/* Summary Cards */}
          <motion.div variants={item}>
            <Card className="border-none shadow-md hover:shadow-lg transition-all">
              <CardContent className="p-6 flex items-center gap-4">
                <div className="p-3 bg-blue-100 rounded-xl text-blue-600">
                  <FlaskConical className="h-8 w-8" />
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-500">Toplam Proje</p>
                  <h3 className="text-2xl font-bold text-slate-900">{totalProjects}</h3>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={item}>
            <Card className="border-none shadow-md hover:shadow-lg transition-all">
              <CardContent className="p-6 flex items-center gap-4">
                <div className="p-3 bg-emerald-100 rounded-xl text-emerald-600">
                  <CheckCircle2 className="h-8 w-8" />
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-500">Tamamlanan</p>
                  <h3 className="text-2xl font-bold text-slate-900">
                    {stats?.flatMap(s => s.projects).filter(p => p.status === 'Tamamlandı').length || 0}
                  </h3>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={item}>
            <Card className="border-none shadow-md hover:shadow-lg transition-all">
              <CardContent className="p-6 flex items-center gap-4">
                <div className="p-3 bg-amber-100 rounded-xl text-amber-600">
                  <Beaker className="h-8 w-8" />
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-500">Lab Aşamasında</p>
                  <h3 className="text-2xl font-bold text-slate-900">
                    {stats?.flatMap(s => s.projects).filter(p => p.status === 'Laboratuvar Testleri').length || 0}
                  </h3>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={item}>
            <Card className="border-none shadow-md hover:shadow-lg transition-all">
              <CardContent className="p-6 flex items-center gap-4">
                <div className="p-3 bg-purple-100 rounded-xl text-purple-600">
                  <FileText className="h-8 w-8" />
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-500">Literatür Taraması</p>
                  <h3 className="text-2xl font-bold text-slate-900">
                    {stats?.flatMap(s => s.projects).filter(p => p.status === 'Literatür Taraması').length || 0}
                  </h3>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Chart Section */}
          <motion.div 
            variants={item}
            initial="hidden"
            animate="show"
            className="lg:col-span-2"
          >
            <Card className="shadow-lg border-none h-full">
              <CardHeader>
                <CardTitle className="text-lg font-bold text-slate-800">Uzmanlık Alanına Göre Dağılım</CardTitle>
              </CardHeader>
              <CardContent className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={stats}>
                    <XAxis 
                      dataKey="expertiseArea" 
                      stroke="#888888"
                      fontSize={12}
                      tickLine={false}
                      axisLine={false}
                    />
                    <YAxis
                      stroke="#888888"
                      fontSize={12}
                      tickLine={false}
                      axisLine={false}
                      tickFormatter={(value) => `${value}`}
                    />
                    <Tooltip 
                      cursor={{ fill: 'transparent' }}
                      contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                    />
                    <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                      {stats?.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>

          {/* Activity Feed */}
          <motion.div 
            variants={item}
            initial="hidden"
            animate="show"
          >
            <Card className="shadow-lg border-none h-full">
              <CardHeader>
                <CardTitle className="text-lg font-bold text-slate-800">Son Aktiviteler</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {recentProjects.map((project, i) => (
                    <div key={project.id} className="flex gap-4">
                      <div className="relative mt-1">
                        <div className="h-2 w-2 rounded-full bg-blue-500 z-10 relative"></div>
                        {i !== recentProjects.length - 1 && (
                          <div className="absolute top-2 left-1 h-full w-[1px] bg-slate-200"></div>
                        )}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-slate-800 line-clamp-1">{project.name}</p>
                        <p className="text-xs text-slate-500">
                          {project.rdSpecialist} • {format(new Date(project.createdAt!), "d MMM yyyy", { locale: tr })}
                        </p>
                        <span className="inline-block mt-1 px-2 py-0.5 bg-slate-100 text-slate-600 text-[10px] rounded-full font-medium border border-slate-200">
                          {project.status}
                        </span>
                      </div>
                    </div>
                  ))}
                  
                  {recentProjects.length === 0 && (
                    <div className="text-center py-8 text-slate-400 text-sm">
                      Henüz aktivite bulunmuyor.
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </main>
    </div>
  );
}
