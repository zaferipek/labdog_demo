import { Link, useLocation } from "wouter";
import { 
  LayoutDashboard, 
  FlaskConical, 
  Settings, 
  Menu,
  X,
  Database,
  LogOut,
  ClipboardList
} from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { useAuth } from "@/hooks/use-auth";
import { canAccessSettings, roleLabels } from "@/lib/permissions";
import logoPath from "@assets/Gemini_Generated_Image_y7w169y7w169y7w1_1772522097082.png";

const allMenuItems = [
  { icon: LayoutDashboard, label: "Dashboard", href: "/", roles: null },
  { icon: FlaskConical, label: "Projeler", href: "/projects", roles: null },
  { icon: ClipboardList, label: "Görevler", href: "/tasks", roles: null },
  { icon: Database, label: "Hammaddeler", href: "/materials", roles: null },
  { icon: Settings, label: "Ayarlar", href: "/settings", roles: ["Admin"] as string[] },
];

export function Sidebar() {
  const [location] = useLocation();
  const [isOpen, setIsOpen] = useState(false);
  const { data: user } = useAuth();

  const menuItems = allMenuItems.filter(item => {
    if (!item.roles) return true;
    return user && item.roles.includes(user.role);
  });

  const handleLogout = async () => {
    await apiRequest("POST", "/api/auth/logout");
    queryClient.setQueryData(["/api/auth/me"], null);
    queryClient.clear();
  };

  const userInitials = user?.name
    ? user.name.split(" ").map((n: string) => n[0]).join("").toUpperCase().slice(0, 2)
    : "??";

  return (
    <>
      <Button 
        variant="ghost" 
        size="icon" 
        className="fixed top-4 left-4 z-50 md:hidden"
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
      </Button>

      <aside className={cn(
        "fixed inset-y-0 left-0 z-40 w-64 bg-slate-900 text-white transform transition-transform duration-200 ease-in-out md:translate-x-0",
        isOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="flex flex-col h-full">
          <div className="p-5 border-b border-slate-800">
            <img src={logoPath} alt="LabForce" className="h-20 mix-blend-screen" style={{ filter: 'invert(1) grayscale(1) contrast(3) blur(0.2px)' }} />
            <p className="text-[10px] text-slate-500 mt-2 ml-1">Ar-Ge Yönetim Sistemi</p>
          </div>

          <nav className="flex-1 px-4 py-6 space-y-2">
            {menuItems.map((item) => {
              const isActive = location === item.href;
              return (
                <Link key={item.href} href={item.href}>
                  <div className={cn(
                    "flex items-center gap-3 px-4 py-3 rounded-lg cursor-pointer transition-all duration-200 group",
                    isActive 
                      ? "bg-primary text-white shadow-md shadow-primary/20" 
                      : "text-slate-400 hover:bg-slate-800 hover:text-white"
                  )}>
                    <item.icon className={cn("h-5 w-5", isActive ? "text-white" : "text-slate-400 group-hover:text-white")} />
                    <span className="font-medium">{item.label}</span>
                  </div>
                </Link>
              );
            })}
          </nav>

          <div className="p-4 border-t border-slate-800 space-y-3">
            <div className="flex items-center gap-3 px-2 py-2 rounded-lg bg-slate-800/50">
              <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-blue-500 to-cyan-400 flex items-center justify-center text-xs font-bold">
                {userInitials}
              </div>
              <div className="overflow-hidden flex-1">
                <p className="text-sm font-medium truncate" data-testid="text-user-name">{user?.name || "Kullanıcı"}</p>
                <div className="flex items-center gap-1.5">
                  <p className="text-xs text-slate-400 truncate" data-testid="text-user-role">{roleLabels[user?.role || ""] || user?.role}</p>
                  {user?.expertiseGroup && (
                    <Badge variant="outline" className="text-[9px] px-1.5 py-0 border-slate-600 text-slate-400 h-4">
                      {user.expertiseGroup}
                    </Badge>
                  )}
                </div>
              </div>
            </div>
            <Button 
              variant="ghost" 
              size="sm" 
              className="w-full justify-start gap-2 text-slate-400 hover:text-white hover:bg-slate-800"
              onClick={handleLogout}
              data-testid="button-logout"
            >
              <LogOut className="h-4 w-4" /> Çıkış Yap
            </Button>
          </div>
        </div>
      </aside>

      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
}
