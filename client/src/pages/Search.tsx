import { useState, useEffect } from "react";
import { useLocation, useSearch } from "wouter";
import { useQuery } from "@tanstack/react-query";
import { Skeleton } from "@/components/ui/skeleton";
import { useI18n } from "@/lib/i18n";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { MissingPersonCard } from "@/components/MissingPersonCard";
import { FilterBar } from "@/components/FilterBar";
import type { Disparu, SearchFilters } from "@shared/schema";

export default function Search() {
  const { t } = useI18n();
  const searchParams = useSearch();
  const [, setLocation] = useLocation();
  
  const params = new URLSearchParams(searchParams);
  const initialQuery = params.get("q") || "";
  
  const [filters, setFilters] = useState<SearchFilters>({
    query: initialQuery,
    status: "all",
    personType: "all",
  });

  const { data: disparus, isLoading, refetch } = useQuery<Disparu[]>({
    queryKey: ["/api/disparus", filters],
  });

  const handleSearch = () => {
    const queryParams = new URLSearchParams();
    if (filters.query) queryParams.set("q", filters.query);
    if (filters.status && filters.status !== "all") queryParams.set("status", filters.status);
    if (filters.personType && filters.personType !== "all") queryParams.set("personType", filters.personType);
    if (filters.country) queryParams.set("country", filters.country);
    setLocation(`/recherche?${queryParams.toString()}`);
    refetch();
  };

  const handleReset = () => {
    setFilters({
      query: "",
      status: "all",
      personType: "all",
    });
    setLocation("/recherche");
  };

  const handleHeaderSearch = (query: string) => {
    setFilters((prev) => ({ ...prev, query }));
    handleSearch();
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header onSearch={handleHeaderSearch} />

      <main className="flex-1 py-8 px-4">
        <div className="max-w-7xl mx-auto space-y-8">
          <div>
            <h1 className="text-3xl font-bold mb-2" data-testid="text-search-title">
              {t("nav.search")}
            </h1>
            <p className="text-muted-foreground">
              {disparus
                ? `${disparus.length} ${t("noResults").includes("No") ? "results" : "résultats"}`
                : t("loading")}
            </p>
          </div>

          <FilterBar
            filters={filters}
            onFiltersChange={setFilters}
            onSearch={handleSearch}
            onReset={handleReset}
          />

          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(9)].map((_, i) => (
                <div key={i} className="space-y-4">
                  <Skeleton className="aspect-square rounded-lg" />
                  <Skeleton className="h-6 w-3/4" />
                  <Skeleton className="h-4 w-1/2" />
                </div>
              ))}
            </div>
          ) : disparus && disparus.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {disparus.map((person) => (
                <MissingPersonCard key={person.id} person={person} />
              ))}
            </div>
          ) : (
            <div className="text-center py-16">
              <p className="text-lg text-muted-foreground">{t("noResults")}</p>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}
