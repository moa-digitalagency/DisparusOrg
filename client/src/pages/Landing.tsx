import { useState } from "react";
import { Link, useLocation } from "wouter";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useI18n } from "@/lib/i18n";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { MissingPersonCard } from "@/components/MissingPersonCard";
import { StatsDisplay } from "@/components/StatsDisplay";
import { FilterBar } from "@/components/FilterBar";
import { LeafletMap } from "@/components/LeafletMap";
import { AlertTriangle, FileText, Share2, Eye, ArrowRight } from "lucide-react";
import type { Disparu, SearchFilters } from "@shared/schema";
import { COUNTRIES_CITIES } from "@shared/schema";

export default function Landing() {
  const { t } = useI18n();
  const [, setLocation] = useLocation();
  const [filters, setFilters] = useState<SearchFilters>({
    status: "all",
    personType: "all",
  });

  const { data: disparus, isLoading } = useQuery<Disparu[]>({
    queryKey: ["/api/disparus", filters],
  });

  const { data: stats } = useQuery<{
    total: number;
    found: number;
    countries: number;
    contributions: number;
  }>({
    queryKey: ["/api/stats"],
  });

  const handleSearch = (query?: string) => {
    if (query) {
      setFilters((prev) => ({ ...prev, query }));
    }
    setLocation(`/recherche?q=${encodeURIComponent(query || filters.query || "")}`);
  };

  const markers = (disparus || [])
    .filter((d) => d.latitude && d.longitude)
    .map((d) => ({
      lat: d.latitude!,
      lng: d.longitude!,
      name: `${d.firstName} ${d.lastName}`,
      id: d.publicId,
      photoUrl: d.photoUrl || undefined,
    }));

  const helpCards = [
    {
      icon: AlertTriangle,
      title: t("help.report.title"),
      desc: t("help.report.desc"),
      href: "/signaler",
      color: "text-destructive",
    },
    {
      icon: Eye,
      title: t("help.contribute.title"),
      desc: t("help.contribute.desc"),
      href: "/recherche",
      color: "text-blue-600 dark:text-blue-500",
    },
    {
      icon: Share2,
      title: t("help.share.title"),
      desc: t("help.share.desc"),
      href: "#",
      color: "text-green-600 dark:text-green-500",
    },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header onSearch={handleSearch} />

      <main className="flex-1">
        <section className="py-12 md:py-20 px-4 bg-gradient-to-b from-destructive/5 to-transparent">
          <div className="max-w-7xl mx-auto text-center space-y-6">
            <h1 className="text-3xl md:text-5xl font-bold leading-tight" data-testid="text-hero-title">
              {t("hero.title")}
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto" data-testid="text-hero-subtitle">
              {t("hero.subtitle")}
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
              <Link href="/signaler">
                <Button size="lg" data-testid="button-report-hero">
                  <AlertTriangle className="w-5 h-5 mr-2" />
                  {t("btn.report")}
                </Button>
              </Link>
              <Link href="/recherche">
                <Button size="lg" variant="outline" data-testid="button-search-hero">
                  {t("nav.search")}
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
            </div>
          </div>
        </section>

        <section className="py-8 px-4 -mt-8">
          <div className="max-w-7xl mx-auto">
            <StatsDisplay
              missing={stats?.total || 0}
              found={stats?.found || 0}
              countries={stats?.countries || Object.keys(COUNTRIES_CITIES).length}
              contributions={stats?.contributions || 0}
            />
          </div>
        </section>

        <section className="py-8 px-4">
          <div className="max-w-7xl mx-auto">
            <h2 className="text-2xl font-semibold mb-6">
              {t("nav.search")}
            </h2>
            <LeafletMap
              markers={markers}
              height="h-80 md:h-96"
              zoom={4}
              showGeolocation={false}
            />
          </div>
        </section>

        <section className="py-12 px-4">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
              <h2 className="text-2xl font-semibold">
                {t("stats.missing")}
              </h2>
              <Link href="/recherche">
                <Button variant="outline">
                  {t("viewMore")}
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
            </div>

            {isLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="space-y-4">
                    <Skeleton className="aspect-square rounded-lg" />
                    <Skeleton className="h-6 w-3/4" />
                    <Skeleton className="h-4 w-1/2" />
                  </div>
                ))}
              </div>
            ) : disparus && disparus.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {disparus.slice(0, 6).map((person) => (
                  <MissingPersonCard key={person.id} person={person} />
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                <p>{t("noResults")}</p>
                <Link href="/signaler">
                  <Button className="mt-4">
                    {t("btn.report")}
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </section>

        <section className="py-12 px-4 bg-muted/30">
          <div className="max-w-7xl mx-auto">
            <h2 className="text-2xl font-semibold text-center mb-8">
              {t("help.title")}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {helpCards.map((card) => (
                <Link key={card.title} href={card.href}>
                  <div className="bg-card border border-card-border rounded-lg p-6 text-center hover-elevate transition-all h-full">
                    <card.icon className={`w-12 h-12 mx-auto mb-4 ${card.color}`} />
                    <h3 className="font-semibold text-lg mb-2">{card.title}</h3>
                    <p className="text-sm text-muted-foreground">{card.desc}</p>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
