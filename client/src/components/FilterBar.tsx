import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { useI18n } from "@/lib/i18n";
import { COUNTRIES_CITIES, type SearchFilters } from "@shared/schema";
import { Search, Filter, X } from "lucide-react";

interface FilterBarProps {
  filters: SearchFilters;
  onFiltersChange: (filters: SearchFilters) => void;
  onSearch: () => void;
  onReset: () => void;
}

export function FilterBar({ filters, onFiltersChange, onSearch, onReset }: FilterBarProps) {
  const { t } = useI18n();
  const countries = Object.keys(COUNTRIES_CITIES);

  const updateFilter = <K extends keyof SearchFilters>(key: K, value: SearchFilters[K]) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder={t("search.placeholder")}
            value={filters.query || ""}
            onChange={(e) => updateFilter("query", e.target.value)}
            className="pl-10"
            data-testid="input-filter-search"
          />
        </div>
        <div className="flex gap-2">
          <Button onClick={onSearch} data-testid="button-filter-search">
            <Search className="w-4 h-4 mr-2" />
            {t("nav.search")}
          </Button>
          <Button variant="outline" onClick={onReset} data-testid="button-filter-reset">
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <div className="flex flex-wrap gap-3 items-center">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">Filters:</span>
        </div>

        <Select
          value={filters.status || "all"}
          onValueChange={(value) => updateFilter("status", value as any)}
        >
          <SelectTrigger className="w-40" data-testid="select-filter-status">
            <SelectValue placeholder={t("filter.status")} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">{t("filter.status.all")}</SelectItem>
            <SelectItem value="missing">{t("filter.status.missing")}</SelectItem>
            <SelectItem value="found">{t("filter.status.found")}</SelectItem>
            <SelectItem value="deceased">{t("filter.status.deceased")}</SelectItem>
          </SelectContent>
        </Select>

        <Select
          value={filters.personType || "all"}
          onValueChange={(value) => updateFilter("personType", value as any)}
        >
          <SelectTrigger className="w-40" data-testid="select-filter-type">
            <SelectValue placeholder={t("form.personType")} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">{t("filter.all")}</SelectItem>
            <SelectItem value="child">{t("filter.children")}</SelectItem>
            <SelectItem value="adult">{t("filter.adults")}</SelectItem>
            <SelectItem value="senior">{t("filter.seniors")}</SelectItem>
          </SelectContent>
        </Select>

        <Select
          value={filters.country || "all"}
          onValueChange={(value) => updateFilter("country", value === "all" ? undefined : value)}
        >
          <SelectTrigger className="w-48" data-testid="select-filter-country">
            <SelectValue placeholder={t("filter.country")} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">{t("filter.country.all")}</SelectItem>
            {countries.map((country) => (
              <SelectItem key={country} value={country}>
                {country}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <div className="flex items-center gap-2">
          <Checkbox
            id="hasPhoto"
            checked={filters.hasPhoto || false}
            onCheckedChange={(checked) => updateFilter("hasPhoto", checked as boolean)}
            data-testid="checkbox-filter-photo"
          />
          <Label htmlFor="hasPhoto" className="text-sm cursor-pointer">
            {t("filter.hasPhoto")}
          </Label>
        </div>
      </div>
    </div>
  );
}
