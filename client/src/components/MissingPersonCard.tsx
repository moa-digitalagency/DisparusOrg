import { Link } from "wouter";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useI18n } from "@/lib/i18n";
import { MapPin, Calendar, User, ArrowRight } from "lucide-react";
import type { Disparu } from "@shared/schema";
import { formatDistanceToNow, differenceInHours } from "date-fns";
import { fr, enUS } from "date-fns/locale";

interface MissingPersonCardProps {
  person: Disparu;
}

export function MissingPersonCard({ person }: MissingPersonCardProps) {
  const { t, language } = useI18n();
  const locale = language === "fr" ? fr : enUS;

  const isUrgent =
    person.status === "missing" &&
    differenceInHours(new Date(), new Date(person.disappearanceDate)) < 48;

  const statusColors: Record<string, string> = {
    missing: "bg-destructive text-destructive-foreground",
    found: "bg-green-600 text-white dark:bg-green-700",
    deceased: "bg-muted text-muted-foreground",
  };

  const personTypeLabels: Record<string, string> = {
    child: t("filter.children"),
    adult: t("filter.adults"),
    senior: t("filter.seniors"),
  };

  const sexLabels: Record<string, string> = {
    male: t("form.sex.male"),
    female: t("form.sex.female"),
    unspecified: t("form.sex.unspecified"),
  };

  return (
    <Card className="overflow-hidden group" data-testid={`card-person-${person.publicId}`}>
      <div className="relative aspect-square bg-muted">
        {person.photoUrl ? (
          <img
            src={person.photoUrl}
            alt={`${person.firstName} ${person.lastName}`}
            className="w-full h-full object-cover"
            data-testid={`img-person-${person.publicId}`}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <User className="w-24 h-24 text-muted-foreground/50" />
          </div>
        )}
        
        {isUrgent && (
          <Badge
            className="absolute top-2 right-2 bg-destructive text-destructive-foreground animate-pulse"
            data-testid={`badge-urgent-${person.publicId}`}
          >
            {t("card.urgent")}
          </Badge>
        )}

        <Badge
          className={`absolute top-2 left-2 ${statusColors[person.status || "missing"]}`}
          data-testid={`badge-status-${person.publicId}`}
        >
          {t(`detail.status.${person.status || "missing"}`)}
        </Badge>
      </div>

      <CardContent className="p-4 space-y-3">
        <div>
          <h3 className="font-semibold text-lg leading-tight" data-testid={`text-name-${person.publicId}`}>
            {person.firstName} {person.lastName}
          </h3>
          <div className="flex items-center gap-2 text-sm text-muted-foreground mt-1">
            <span>{person.age} {t("card.age")}</span>
            <span>·</span>
            <span>{sexLabels[person.sex]}</span>
          </div>
        </div>

        <div className="space-y-1.5 text-sm">
          <div className="flex items-center gap-2 text-muted-foreground">
            <MapPin className="w-4 h-4 shrink-0" />
            <span className="truncate" data-testid={`text-location-${person.publicId}`}>
              {person.city}, {person.country}
            </span>
          </div>
          <div className="flex items-center gap-2 text-muted-foreground">
            <Calendar className="w-4 h-4 shrink-0" />
            <span data-testid={`text-date-${person.publicId}`}>
              {t("card.missing_since")}{" "}
              {formatDistanceToNow(new Date(person.disappearanceDate), {
                addSuffix: true,
                locale,
              })}
            </span>
          </div>
        </div>

        <div className="flex items-center justify-between pt-2">
          <Badge variant="outline" className="font-mono text-xs" data-testid={`badge-id-${person.publicId}`}>
            ID: {person.publicId}
          </Badge>
          <Badge variant="secondary" className="text-xs">
            {personTypeLabels[person.personType]}
          </Badge>
        </div>

        <Link href={`/disparu/${person.publicId}`}>
          <Button className="w-full mt-2" data-testid={`button-view-${person.publicId}`}>
            {t("card.view_details")}
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </Link>
      </CardContent>
    </Card>
  );
}
