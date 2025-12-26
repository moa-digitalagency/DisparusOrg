import { useI18n } from "@/lib/i18n";
import { Users, CheckCircle, Globe, MessageSquare } from "lucide-react";

interface StatsDisplayProps {
  missing: number;
  found: number;
  countries: number;
  contributions: number;
}

export function StatsDisplay({ missing, found, countries, contributions }: StatsDisplayProps) {
  const { t } = useI18n();

  const stats = [
    {
      icon: Users,
      value: missing,
      label: t("stats.missing"),
      color: "text-destructive",
    },
    {
      icon: CheckCircle,
      value: found,
      label: t("stats.found"),
      color: "text-green-600 dark:text-green-500",
    },
    {
      icon: Globe,
      value: countries,
      label: t("stats.countries"),
      color: "text-blue-600 dark:text-blue-500",
    },
    {
      icon: MessageSquare,
      value: contributions,
      label: t("stats.contributions"),
      color: "text-amber-600 dark:text-amber-500",
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
      {stats.map((stat) => (
        <div
          key={stat.label}
          className="bg-card border border-card-border rounded-lg p-4 md:p-6 text-center"
          data-testid={`stat-${stat.label.toLowerCase().replace(/\s/g, "-")}`}
        >
          <stat.icon className={`w-8 h-8 mx-auto mb-2 ${stat.color}`} />
          <p className="text-3xl md:text-4xl font-bold">{stat.value.toLocaleString()}</p>
          <p className="text-sm text-muted-foreground mt-1">{stat.label}</p>
        </div>
      ))}
    </div>
  );
}
