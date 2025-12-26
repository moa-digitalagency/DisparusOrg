import { Link, useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useI18n, type Language } from "@/lib/i18n";
import { useTheme } from "@/lib/theme";
import { Search, AlertTriangle, Menu, X, Sun, Moon, Globe } from "lucide-react";
import { useState } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface HeaderProps {
  onSearch?: (query: string) => void;
}

export function Header({ onSearch }: HeaderProps) {
  const { t, language, setLanguage } = useI18n();
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [location] = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch?.(searchQuery);
  };

  const toggleLanguage = () => {
    setLanguage(language === "fr" ? "en" : "fr");
  };

  return (
    <header className="sticky top-0 z-50 bg-background/95 backdrop-blur-sm border-b">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between gap-4 h-16 md:h-20">
          <Link href="/" className="flex items-center gap-2 shrink-0">
            <div className="w-10 h-10 rounded-lg bg-destructive flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-white" />
            </div>
            <div className="hidden sm:block">
              <h1 className="text-lg font-bold leading-tight" data-testid="text-site-name">
                {t("site.name")}
              </h1>
              <p className="text-xs text-muted-foreground">{t("site.tagline")}</p>
            </div>
          </Link>

          <form
            onSubmit={handleSearch}
            className="hidden md:flex flex-1 max-w-md mx-4"
          >
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                type="search"
                placeholder={t("search.placeholder")}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 h-10"
                data-testid="input-search"
              />
            </div>
          </form>

          <div className="flex items-center gap-2">
            <Button
              size="icon"
              variant="ghost"
              onClick={toggleLanguage}
              data-testid="button-language"
            >
              <Globe className="w-5 h-5" />
            </Button>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button size="icon" variant="ghost" data-testid="button-theme">
                  {resolvedTheme === "dark" ? (
                    <Moon className="w-5 h-5" />
                  ) : (
                    <Sun className="w-5 h-5" />
                  )}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => setTheme("light")}>
                  <Sun className="w-4 h-4 mr-2" />
                  Light
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setTheme("dark")}>
                  <Moon className="w-4 h-4 mr-2" />
                  Dark
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setTheme("system")}>
                  System
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <Link href="/signaler" className="hidden sm:block">
              <Button variant="default" data-testid="button-report-header">
                <AlertTriangle className="w-4 h-4 mr-2" />
                {t("btn.report")}
              </Button>
            </Link>

            <Button
              size="icon"
              variant="ghost"
              className="md:hidden"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              data-testid="button-mobile-menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>
          </div>
        </div>

        {mobileMenuOpen && (
          <div className="md:hidden pb-4 space-y-4">
            <form onSubmit={handleSearch}>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  type="search"
                  placeholder={t("search.placeholder")}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                  data-testid="input-search-mobile"
                />
              </div>
            </form>
            <nav className="flex flex-col gap-2">
              <Link href="/" onClick={() => setMobileMenuOpen(false)}>
                <Button variant={location === "/" ? "secondary" : "ghost"} className="w-full justify-start">
                  {t("nav.home")}
                </Button>
              </Link>
              <Link href="/signaler" onClick={() => setMobileMenuOpen(false)}>
                <Button variant="default" className="w-full">
                  <AlertTriangle className="w-4 h-4 mr-2" />
                  {t("btn.report")}
                </Button>
              </Link>
            </nav>
            <div className="flex items-center justify-between border-t pt-4">
              <span className="text-sm text-muted-foreground">
                {language === "fr" ? "Français" : "English"}
              </span>
              <Button size="sm" variant="outline" onClick={toggleLanguage}>
                {language === "fr" ? "EN" : "FR"}
              </Button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
