import { Link } from "wouter";
import { useI18n } from "@/lib/i18n";
import { AlertTriangle, Heart } from "lucide-react";
import { COUNTRIES_CITIES } from "@shared/schema";

export function Footer() {
  const { t } = useI18n();
  const countries = Object.keys(COUNTRIES_CITIES).slice(0, 12);

  return (
    <footer className="bg-muted/50 border-t mt-auto">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-lg bg-destructive flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="font-bold">{t("site.name")}</h3>
                <p className="text-xs text-muted-foreground">{t("site.tagline")}</p>
              </div>
            </div>
            <p className="text-sm text-muted-foreground">
              {t("hero.subtitle")}
            </p>
          </div>

          <div>
            <h4 className="font-semibold mb-4">{t("footer.countries")}</h4>
            <div className="max-h-48 overflow-y-auto space-y-1">
              {countries.map((country) => (
                <p key={country} className="text-sm text-muted-foreground">
                  {country}
                </p>
              ))}
              <p className="text-sm text-muted-foreground font-medium">
                +{Object.keys(COUNTRIES_CITIES).length - 12} {t("viewMore")}...
              </p>
            </div>
          </div>

          <div>
            <h4 className="font-semibold mb-4">Navigation</h4>
            <nav className="space-y-2">
              <Link href="/" className="block text-sm text-muted-foreground hover:text-foreground">
                {t("nav.home")}
              </Link>
              <Link href="/signaler" className="block text-sm text-muted-foreground hover:text-foreground">
                {t("nav.report")}
              </Link>
              <Link href="/recherche" className="block text-sm text-muted-foreground hover:text-foreground">
                {t("nav.search")}
              </Link>
            </nav>
          </div>

          <div>
            <h4 className="font-semibold mb-4">Legal</h4>
            <nav className="space-y-2">
              <a href="#" className="block text-sm text-muted-foreground hover:text-foreground">
                {t("footer.about")}
              </a>
              <a href="#" className="block text-sm text-muted-foreground hover:text-foreground">
                {t("footer.privacy")}
              </a>
              <a href="#" className="block text-sm text-muted-foreground hover:text-foreground">
                {t("footer.terms")}
              </a>
              <a href="#" className="block text-sm text-muted-foreground hover:text-foreground">
                {t("footer.contact")}
              </a>
            </nav>
          </div>
        </div>

        <div className="border-t mt-8 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
          <p>&copy; {new Date().getFullYear()} {t("site.name")}. All rights reserved.</p>
          <p className="flex items-center gap-1">
            Made with <Heart className="w-4 h-4 text-destructive" /> for Africa
          </p>
        </div>
      </div>
    </footer>
  );
}
