import { useState } from "react";
import { useParams, Link } from "wouter";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useI18n } from "@/lib/i18n";
import { useToast } from "@/hooks/use-toast";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { LeafletMap } from "@/components/LeafletMap";
import { Timeline } from "@/components/Timeline";
import { ModerationDialog } from "@/components/ModerationDialog";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { format } from "date-fns";
import { fr, enUS } from "date-fns/locale";
import type { Disparu, Contribution, Contact } from "@shared/schema";
import {
  ArrowLeft,
  User,
  MapPin,
  Calendar,
  Shirt,
  Package,
  Phone,
  Mail,
  Share2,
  Download,
  Loader2,
  Eye,
  Info,
  Shield,
  CheckCircle,
  HelpCircle,
} from "lucide-react";

const contributionSchema = z.object({
  contributionType: z.enum(["sighting", "info", "police_report", "found", "other"]),
  details: z.string().min(10),
  observationDate: z.date().optional(),
  latitude: z.number().optional(),
  longitude: z.number().optional(),
  foundState: z.enum(["safe", "injured", "deceased"]).optional(),
  returnCircumstances: z.string().optional(),
  contactName: z.string().optional(),
  contactPhone: z.string().optional(),
});

type ContributionFormData = z.infer<typeof contributionSchema>;

export default function DisparuDetail() {
  const { id } = useParams<{ id: string }>();
  const { t, language } = useI18n();
  const { toast } = useToast();
  const locale = language === "fr" ? fr : enUS;
  const [selectedPosition, setSelectedPosition] = useState<[number, number] | null>(null);

  const { data: disparu, isLoading } = useQuery<Disparu>({
    queryKey: ["/api/disparus", id],
  });

  const { data: contributions = [] } = useQuery<Contribution[]>({
    queryKey: ["/api/contributions", id],
    enabled: !!id,
  });

  const form = useForm<ContributionFormData>({
    resolver: zodResolver(contributionSchema),
    defaultValues: {
      contributionType: "info",
      details: "",
      contactName: "",
      contactPhone: "",
    },
  });

  const contributionType = form.watch("contributionType");

  const mutation = useMutation({
    mutationFn: async (data: ContributionFormData) => {
      return apiRequest("POST", "/api/contributions", {
        ...data,
        disparuId: disparu?.id,
      });
    },
    onSuccess: () => {
      toast({ title: t("success") });
      form.reset();
      setSelectedPosition(null);
      queryClient.invalidateQueries({ queryKey: ["/api/contributions", id] });
    },
    onError: () => {
      toast({ title: t("error"), variant: "destructive" });
    },
  });

  const handleMapClick = (lat: number, lng: number) => {
    setSelectedPosition([lat, lng]);
    form.setValue("latitude", lat);
    form.setValue("longitude", lng);
  };

  const onSubmit = (data: ContributionFormData) => {
    mutation.mutate(data);
  };

  const handleShare = async () => {
    if (navigator.share) {
      await navigator.share({
        title: `${disparu?.firstName} ${disparu?.lastName} - ${t("site.name")}`,
        url: window.location.href,
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      toast({ title: "Link copied!" });
    }
  };

  const statusColors: Record<string, string> = {
    missing: "bg-destructive text-destructive-foreground",
    found: "bg-green-600 text-white dark:bg-green-700",
    deceased: "bg-muted text-muted-foreground",
  };

  const typeIcons: Record<string, typeof Eye> = {
    sighting: Eye,
    info: Info,
    police_report: Shield,
    found: CheckCircle,
    other: HelpCircle,
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col bg-background">
        <Header />
        <main className="flex-1 py-8 px-4">
          <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-5 gap-8">
            <div className="md:col-span-2 space-y-4">
              <Skeleton className="aspect-[3/4] rounded-lg" />
              <Skeleton className="h-10 w-full" />
            </div>
            <div className="md:col-span-3 space-y-6">
              <Skeleton className="h-12 w-3/4" />
              <Skeleton className="h-40" />
              <Skeleton className="h-60" />
            </div>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (!disparu) {
    return (
      <div className="min-h-screen flex flex-col bg-background">
        <Header />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <p className="text-lg text-muted-foreground">{t("noResults")}</p>
            <Link href="/">
              <Button className="mt-4">
                <ArrowLeft className="w-4 h-4 mr-2" />
                {t("nav.home")}
              </Button>
            </Link>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  const contacts = (disparu.contacts as Contact[]) || [];
  const markers = disparu.latitude && disparu.longitude
    ? [{
        lat: disparu.latitude,
        lng: disparu.longitude,
        name: `${disparu.firstName} ${disparu.lastName}`,
        id: disparu.publicId,
        photoUrl: disparu.photoUrl || undefined,
      }]
    : [];

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header />

      <main className="flex-1 py-8 px-4">
        <div className="max-w-6xl mx-auto">
          <Link href="/" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-6">
            <ArrowLeft className="w-4 h-4 mr-1" />
            {t("nav.home")}
          </Link>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-8">
            <div className="md:col-span-2 space-y-4">
              <div className="relative aspect-[3/4] bg-muted rounded-lg overflow-hidden">
                {disparu.photoUrl ? (
                  <img
                    src={disparu.photoUrl}
                    alt={`${disparu.firstName} ${disparu.lastName}`}
                    className="w-full h-full object-cover"
                    data-testid="img-disparu-photo"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <User className="w-32 h-32 text-muted-foreground/50" />
                  </div>
                )}
                <Badge
                  className={`absolute top-4 left-4 ${statusColors[disparu.status || "missing"]}`}
                  data-testid="badge-detail-status"
                >
                  {t(`detail.status.${disparu.status || "missing"}`)}
                </Badge>
              </div>

              <div className="flex items-center justify-between">
                <Badge variant="outline" className="font-mono text-lg px-4 py-1" data-testid="badge-detail-id">
                  ID: {disparu.publicId}
                </Badge>
                <div className="flex gap-2">
                  <Button size="icon" variant="outline" onClick={handleShare} data-testid="button-share">
                    <Share2 className="w-4 h-4" />
                  </Button>
                  <ModerationDialog targetType="disparu" targetId={disparu.id} />
                </div>
              </div>

              <div className="space-y-2">
                <Button variant="outline" className="w-full" data-testid="button-download-pdf">
                  <Download className="w-4 h-4 mr-2" />
                  {t("detail.download.pdf")}
                </Button>
                <Button variant="outline" className="w-full" data-testid="button-download-image">
                  <Download className="w-4 h-4 mr-2" />
                  {t("detail.download.image")}
                </Button>
              </div>
            </div>

            <div className="md:col-span-3 space-y-6">
              <div>
                <h1 className="text-3xl font-bold" data-testid="text-detail-name">
                  {disparu.firstName} {disparu.lastName}
                </h1>
                <p className="text-lg text-muted-foreground mt-1">
                  {disparu.age} {t("card.age")} · {t(`form.sex.${disparu.sex}`)}
                </p>
              </div>

              <Card>
                <CardContent className="p-4 space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="flex items-start gap-3">
                      <MapPin className="w-5 h-5 text-muted-foreground shrink-0 mt-0.5" />
                      <div>
                        <p className="text-sm text-muted-foreground">{t("detail.lastSeen")}</p>
                        <p className="font-medium" data-testid="text-detail-location">
                          {disparu.city}, {disparu.country}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <Calendar className="w-5 h-5 text-muted-foreground shrink-0 mt-0.5" />
                      <div>
                        <p className="text-sm text-muted-foreground">{t("card.missing_since")}</p>
                        <p className="font-medium" data-testid="text-detail-date">
                          {format(new Date(disparu.disappearanceDate), "PPP", { locale })}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <Shirt className="w-5 h-5 text-muted-foreground shrink-0 mt-0.5" />
                      <div>
                        <p className="text-sm text-muted-foreground">{t("detail.clothing")}</p>
                        <p>{disparu.clothing}</p>
                      </div>
                    </div>
                    {disparu.belongings && (
                      <div className="flex items-start gap-3">
                        <Package className="w-5 h-5 text-muted-foreground shrink-0 mt-0.5" />
                        <div>
                          <p className="text-sm text-muted-foreground">{t("detail.belongings")}</p>
                          <p>{disparu.belongings}</p>
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-base">{t("detail.physicalDescription")}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p data-testid="text-detail-description">{disparu.physicalDescription}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-base">{t("detail.circumstances")}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p data-testid="text-detail-circumstances">{disparu.circumstances}</p>
                </CardContent>
              </Card>

              {disparu.latitude && disparu.longitude && (
                <LeafletMap
                  markers={markers}
                  center={[disparu.latitude, disparu.longitude]}
                  zoom={12}
                  height="h-64"
                  showGeolocation={false}
                />
              )}

              {contacts.length > 0 && (
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base">{t("detail.contacts")}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {contacts.map((contact, index) => (
                        <div key={index} className="flex items-center justify-between flex-wrap gap-2 p-3 bg-muted/50 rounded-lg">
                          <div>
                            <p className="font-medium">{contact.name}</p>
                            {contact.relation && (
                              <p className="text-sm text-muted-foreground">{contact.relation}</p>
                            )}
                          </div>
                          <div className="flex items-center gap-3">
                            <a
                              href={`tel:${contact.phone}`}
                              className="flex items-center gap-1 text-sm hover:text-primary"
                            >
                              <Phone className="w-4 h-4" />
                              {contact.phone}
                            </a>
                            {contact.email && (
                              <a
                                href={`mailto:${contact.email}`}
                                className="flex items-center gap-1 text-sm hover:text-primary"
                              >
                                <Mail className="w-4 h-4" />
                              </a>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              <Timeline disparu={disparu} contributions={contributions} />

              <Card>
                <CardHeader>
                  <CardTitle>{t("detail.contribute")}</CardTitle>
                </CardHeader>
                <CardContent>
                  <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                      <FormField
                        control={form.control}
                        name="contributionType"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>{t("contribution.type")} *</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                              <FormControl>
                                <SelectTrigger data-testid="select-contribution-type">
                                  <SelectValue />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                {(["sighting", "info", "police_report", "found", "other"] as const).map((type) => {
                                  const Icon = typeIcons[type];
                                  return (
                                    <SelectItem key={type} value={type}>
                                      <div className="flex items-center gap-2">
                                        <Icon className="w-4 h-4" />
                                        {t(`contribution.type.${type}`)}
                                      </div>
                                    </SelectItem>
                                  );
                                })}
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      {contributionType === "found" && (
                        <>
                          <FormField
                            control={form.control}
                            name="foundState"
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel>{t("contribution.foundState")} *</FormLabel>
                                <Select onValueChange={field.onChange}>
                                  <FormControl>
                                    <SelectTrigger data-testid="select-found-state">
                                      <SelectValue />
                                    </SelectTrigger>
                                  </FormControl>
                                  <SelectContent>
                                    <SelectItem value="safe">{t("contribution.foundState.safe")}</SelectItem>
                                    <SelectItem value="injured">{t("contribution.foundState.injured")}</SelectItem>
                                    <SelectItem value="deceased">{t("contribution.foundState.deceased")}</SelectItem>
                                  </SelectContent>
                                </Select>
                                <FormMessage />
                              </FormItem>
                            )}
                          />

                          <FormField
                            control={form.control}
                            name="returnCircumstances"
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel>{t("contribution.returnCircumstances")}</FormLabel>
                                <FormControl>
                                  <Textarea {...field} rows={2} data-testid="textarea-return" />
                                </FormControl>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                        </>
                      )}

                      <FormField
                        control={form.control}
                        name="observationDate"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>{t("contribution.date")}</FormLabel>
                            <FormControl>
                              <Input
                                type="datetime-local"
                                value={field.value ? field.value.toISOString().slice(0, 16) : ""}
                                onChange={(e) => field.onChange(e.target.value ? new Date(e.target.value) : undefined)}
                                data-testid="input-observation-date"
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <div>
                        <FormLabel>{t("contribution.location")}</FormLabel>
                        <LeafletMap
                          height="h-48"
                          onClick={handleMapClick}
                          selectedPosition={selectedPosition}
                          zoom={8}
                          className="mt-2"
                        />
                      </div>

                      <FormField
                        control={form.control}
                        name="details"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>{t("contribution.details")} *</FormLabel>
                            <FormControl>
                              <Textarea {...field} rows={4} data-testid="textarea-contribution-details" />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <FormField
                          control={form.control}
                          name="contactName"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>{t("form.contact.name")}</FormLabel>
                              <FormControl>
                                <Input {...field} data-testid="input-contributor-name" />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />

                        <FormField
                          control={form.control}
                          name="contactPhone"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>{t("form.contact.phone")}</FormLabel>
                              <FormControl>
                                <Input {...field} data-testid="input-contributor-phone" />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </div>

                      <Button type="submit" className="w-full" disabled={mutation.isPending} data-testid="button-submit-contribution">
                        {mutation.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                        {t("contribution.submit")}
                      </Button>
                    </form>
                  </Form>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
