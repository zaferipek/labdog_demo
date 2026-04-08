import { useState } from "react";
import { useLocation } from "wouter";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";
import logoPath from "@assets/Gemini_Generated_Image_y7w169y7w169y7w1_1772522097082.png";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [, setLocation] = useLocation();
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const res = await apiRequest("POST", "/api/auth/login", { username, password });
      const user = await res.json();
      queryClient.setQueryData(["/api/auth/me"], user);
      setLocation("/");
    } catch {
      toast({ variant: "destructive", title: "Giriş Başarısız", description: "Kullanıcı adı veya şifre hatalı." });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex">
      <div className="hidden lg:flex lg:w-1/2 bg-[#0a1628] items-center justify-center p-12">
        <div className="max-w-lg text-center">
          <img src={logoPath} alt="LabForce" className="h-40 mx-auto mb-8 mix-blend-screen" style={{ filter: 'invert(1) grayscale(1) contrast(3) blur(0.2px)' }} />
          <p className="text-slate-500 text-sm leading-relaxed">
            Projelerinizi yönetin, hammaddelerinizi takip edin, deney sonuçlarınızı kaydedin.
          </p>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-sm">
          <div className="lg:hidden mb-10">
            <img src={logoPath} alt="LabForce" className="h-10 mx-auto" />
          </div>

          <div className="mb-8">
            <h2 className="text-2xl font-display font-bold text-slate-900">Hoş Geldiniz</h2>
            <p className="text-sm text-slate-500 mt-1">Devam etmek için oturum açın.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="username" className="text-slate-700">Kullanıcı Adı</Label>
              <Input
                id="username"
                placeholder="Kullanıcı adınızı girin"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="h-11 bg-white border-slate-200 focus:border-primary"
                data-testid="input-username"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password" className="text-slate-700">Şifre</Label>
              <Input
                id="password"
                type="password"
                placeholder="Şifrenizi girin"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="h-11 bg-white border-slate-200 focus:border-primary"
                data-testid="input-password"
              />
            </div>
            <Button type="submit" className="w-full h-11 gap-2 text-sm font-semibold" disabled={isLoading} data-testid="button-login">
              {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
              {isLoading ? "Giriş Yapılıyor..." : "Giriş Yap"}
            </Button>
          </form>

          <p className="text-center text-slate-400 text-xs mt-10">
            LabForce &copy; 2026
          </p>
        </div>
      </div>
    </div>
  );
}
