import { Link } from "wouter";
import { Button } from "@/components/ui/button";
import { useI18n } from "@/lib/i18n";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { AlertTriangle, Home, Search } from "lucide-react";

export default function NotFound() {
  const { t } = useI18n();

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header />
      
      <main className="flex-1 flex items-center justify-center px-4 py-16">
        <div className="text-center max-w-md">
          <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-muted flex items-center justify-center">
            <AlertTriangle className="w-10 h-10 text-muted-foreground" />
          </div>
          
          <h1 className="text-4xl font-bold mb-4">404</h1>
          <p className="text-lg text-muted-foreground mb-8">
            Page non trouvée
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/">
              <Button>
                <Home className="w-4 h-4 mr-2" />
                {t("nav.home")}
              </Button>
            </Link>
            <Link href="/recherche">
              <Button variant="outline">
                <Search className="w-4 h-4 mr-2" />
                {t("nav.search")}
              </Button>
            </Link>
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
}
