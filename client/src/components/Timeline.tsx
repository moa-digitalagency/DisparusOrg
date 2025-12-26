import { useI18n } from "@/lib/i18n";
import { Eye, Info, Shield, CheckCircle, HelpCircle, Clock } from "lucide-react";
import { format } from "date-fns";
import { fr, enUS } from "date-fns/locale";
import type { Contribution, Disparu } from "@shared/schema";

interface TimelineProps {
  disparu: Disparu;
  contributions: Contribution[];
}

export function Timeline({ disparu, contributions }: TimelineProps) {
  const { t, language } = useI18n();
  const locale = language === "fr" ? fr : enUS;

  const typeIcons: Record<string, typeof Eye> = {
    sighting: Eye,
    info: Info,
    police_report: Shield,
    found: CheckCircle,
    other: HelpCircle,
    created: Clock,
  };

  const typeColors: Record<string, string> = {
    sighting: "bg-blue-500",
    info: "bg-amber-500",
    police_report: "bg-purple-500",
    found: "bg-green-500",
    other: "bg-muted-foreground",
    created: "bg-destructive",
  };

  const allEvents = [
    {
      id: "created",
      type: "created",
      date: disparu.createdAt,
      details: t("timeline.created"),
      location: `${disparu.city}, ${disparu.country}`,
    },
    ...contributions.map((c) => ({
      id: c.id,
      type: c.contributionType,
      date: c.observationDate || c.createdAt,
      details: c.details,
      location: c.latitude && c.longitude 
        ? `${c.latitude.toFixed(4)}, ${c.longitude.toFixed(4)}` 
        : null,
    })),
  ].sort((a, b) => new Date(b.date!).getTime() - new Date(a.date!).getTime());

  return (
    <div className="space-y-4" data-testid="timeline">
      <h3 className="font-semibold text-lg">{t("detail.timeline")}</h3>
      
      <div className="relative">
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-border" />
        
        <div className="space-y-6">
          {allEvents.map((event) => {
            const Icon = typeIcons[event.type] || HelpCircle;
            const color = typeColors[event.type] || "bg-muted-foreground";
            
            return (
              <div key={event.id} className="relative pl-10" data-testid={`timeline-event-${event.id}`}>
                <div
                  className={`absolute left-2 w-5 h-5 rounded-full ${color} flex items-center justify-center -translate-x-1/2`}
                >
                  <Icon className="w-3 h-3 text-white" />
                </div>
                
                <div className="bg-card border border-card-border rounded-lg p-4">
                  <div className="flex items-start justify-between gap-4 flex-wrap">
                    <div>
                      <p className="font-medium">
                        {t(`timeline.${event.type}`)}
                      </p>
                      <p className="text-sm text-muted-foreground mt-1">
                        {event.details}
                      </p>
                    </div>
                    {event.date && (
                      <time className="text-sm text-muted-foreground shrink-0">
                        {format(new Date(event.date), "PPp", { locale })}
                      </time>
                    )}
                  </div>
                  {event.location && (
                    <p className="text-xs text-muted-foreground mt-2">
                      {event.location}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
