import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { useAuth } from "@/hooks/use-auth";
import { Loader2 } from "lucide-react";
import NotFound from "@/pages/not-found";
import Login from "@/pages/Login";
import Dashboard from "@/pages/Dashboard";
import DashboardIndex from "@/pages/DashboardIndex";
import PerformanceDashboard from "@/pages/PerformanceDashboard";
import Projects from "@/pages/Projects";
import ProjectDetails from "@/pages/ProjectDetails";
import Tasks from "@/pages/Tasks";
import Materials from "@/pages/Materials";
import MaterialDetails from "@/pages/MaterialDetails";
import Settings from "@/pages/Settings";
import SettingsAI from "@/pages/SettingsAI";
import SettingsUsers from "@/pages/SettingsUsers";

function Router() {
  return (
    <Switch>
      <Route path="/" component={DashboardIndex} />
      <Route path="/dashboard/management" component={Dashboard} />
      <Route path="/dashboard/performance" component={PerformanceDashboard} />
      <Route path="/projects" component={Projects} />
      <Route path="/projects/:id" component={ProjectDetails} />
      <Route path="/tasks" component={Tasks} />
      <Route path="/materials" component={Materials} />
      <Route path="/materials/:id" component={MaterialDetails} />
      <Route path="/settings" component={Settings} />
      <Route path="/settings/ai" component={SettingsAI} />
      <Route path="/settings/users" component={SettingsUsers} />
      <Route component={NotFound} />
    </Switch>
  );
}

function AuthGuard() {
  const { data: user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!user) {
    return <Login />;
  }

  return <Router />;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <AuthGuard />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
