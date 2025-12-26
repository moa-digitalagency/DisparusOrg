import { useState } from "react";
import { useLocation } from "wouter";
import { useForm, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Progress } from "@/components/ui/progress";
import {
  Form,
  FormControl,
  FormDescription,
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
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useI18n } from "@/lib/i18n";
import { useToast } from "@/hooks/use-toast";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { LeafletMap } from "@/components/LeafletMap";
import { apiRequest } from "@/lib/queryClient";
import { COUNTRIES_CITIES, contactSchema, insertDisparuSchema } from "@shared/schema";
import {
  ArrowLeft,
  ArrowRight,
  Loader2,
  Plus,
  Trash2,
  User,
  MapPin,
  FileText,
  Phone,
} from "lucide-react";

const formSchema = insertDisparuSchema.extend({
  consent: z.boolean().refine((val) => val === true, {
    message: "Consent is required",
  }),
});

type FormData = z.infer<typeof formSchema>;

const STEPS = ["identity", "location", "description", "contact"] as const;

export default function ReportForm() {
  const { t } = useI18n();
  const { toast } = useToast();
  const [, setLocation] = useLocation();
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedPosition, setSelectedPosition] = useState<[number, number] | null>(null);

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      personType: "adult",
      firstName: "",
      lastName: "",
      age: 0,
      sex: "unspecified",
      country: "",
      city: "",
      physicalDescription: "",
      photoUrl: "",
      disappearanceDate: new Date(),
      circumstances: "",
      latitude: undefined,
      longitude: undefined,
      clothing: "",
      belongings: "",
      contacts: [{ name: "", phone: "", email: "", relation: "" }],
      consent: false,
    },
  });

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "contacts",
  });

  const selectedCountry = form.watch("country");
  const cities = selectedCountry ? COUNTRIES_CITIES[selectedCountry] || [] : [];

  const mutation = useMutation({
    mutationFn: async (data: FormData) => {
      const { consent, ...submitData } = data;
      return apiRequest("POST", "/api/disparus", submitData);
    },
    onSuccess: async (response) => {
      const data = await response.json();
      toast({
        title: t("success"),
        description: `ID: ${data.publicId}`,
      });
      setLocation(`/disparu/${data.publicId}`);
    },
    onError: () => {
      toast({
        title: t("error"),
        variant: "destructive",
      });
    },
  });

  const handleMapClick = (lat: number, lng: number) => {
    setSelectedPosition([lat, lng]);
    form.setValue("latitude", lat);
    form.setValue("longitude", lng);
  };

  const nextStep = async () => {
    const fieldsToValidate = getStepFields(currentStep);
    const isValid = await form.trigger(fieldsToValidate as any);
    if (isValid && currentStep < STEPS.length - 1) {
      setCurrentStep((prev) => prev + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep((prev) => prev - 1);
    }
  };

  const getStepFields = (step: number): (keyof FormData)[] => {
    switch (step) {
      case 0:
        return ["personType", "firstName", "lastName", "age", "sex"];
      case 1:
        return ["country", "city", "disappearanceDate", "circumstances"];
      case 2:
        return ["physicalDescription", "clothing"];
      case 3:
        return ["contacts", "consent"];
      default:
        return [];
    }
  };

  const onSubmit = (data: FormData) => {
    // Check if online before submitting
    if (!navigator.onLine) {
      toast({
        title: t("offline.title"),
        description: t("offline.message"),
        variant: "destructive",
      });
      return;
    }
    mutation.mutate(data);
  };

  const stepIcons = [User, MapPin, FileText, Phone];
  const progress = ((currentStep + 1) / STEPS.length) * 100;

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header />

      <main className="flex-1 py-8 px-4">
        <div className="max-w-2xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2" data-testid="text-form-title">
              {t("form.title")}
            </h1>
            <p className="text-muted-foreground">
              {t("form.step")} {currentStep + 1}/{STEPS.length}: {t(`form.step.${STEPS[currentStep]}`)}
            </p>
          </div>

          <div className="mb-8">
            <Progress value={progress} className="h-2" />
            <div className="flex justify-between mt-2">
              {STEPS.map((step, index) => {
                const Icon = stepIcons[index];
                return (
                  <div
                    key={step}
                    className={`flex items-center gap-2 ${
                      index <= currentStep ? "text-primary" : "text-muted-foreground"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="text-xs hidden sm:block">{t(`form.step.${step}`)}</span>
                  </div>
                );
              })}
            </div>
          </div>

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              {currentStep === 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <User className="w-5 h-5" />
                      {t("form.step.identity")}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <FormField
                      control={form.control}
                      name="personType"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>{t("form.personType")} *</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger data-testid="select-person-type">
                                <SelectValue />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="child">{t("form.personType.child")}</SelectItem>
                              <SelectItem value="adult">{t("form.personType.adult")}</SelectItem>
                              <SelectItem value="senior">{t("form.personType.senior")}</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <FormField
                        control={form.control}
                        name="firstName"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>{t("form.firstName")} *</FormLabel>
                            <FormControl>
                              <Input {...field} data-testid="input-first-name" />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={form.control}
                        name="lastName"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>{t("form.lastName")} *</FormLabel>
                            <FormControl>
                              <Input {...field} data-testid="input-last-name" />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <FormField
                        control={form.control}
                        name="age"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>{t("form.age")} *</FormLabel>
                            <FormControl>
                              <Input
                                type="number"
                                min={0}
                                max={120}
                                {...field}
                                onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                                data-testid="input-age"
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={form.control}
                        name="sex"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>{t("form.sex")} *</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                              <FormControl>
                                <SelectTrigger data-testid="select-sex">
                                  <SelectValue />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                <SelectItem value="male">{t("form.sex.male")}</SelectItem>
                                <SelectItem value="female">{t("form.sex.female")}</SelectItem>
                                <SelectItem value="unspecified">{t("form.sex.unspecified")}</SelectItem>
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                  </CardContent>
                </Card>
              )}

              {currentStep === 1 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <MapPin className="w-5 h-5" />
                      {t("form.step.location")}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <FormField
                        control={form.control}
                        name="country"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>{t("form.country")} *</FormLabel>
                            <Select onValueChange={field.onChange} value={field.value}>
                              <FormControl>
                                <SelectTrigger data-testid="select-country">
                                  <SelectValue placeholder={t("filter.country.all")} />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                {Object.keys(COUNTRIES_CITIES).map((country) => (
                                  <SelectItem key={country} value={country}>
                                    {country}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={form.control}
                        name="city"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>{t("form.city")} *</FormLabel>
                            <Select
                              onValueChange={field.onChange}
                              value={field.value}
                              disabled={!selectedCountry}
                            >
                              <FormControl>
                                <SelectTrigger data-testid="select-city">
                                  <SelectValue placeholder={t("form.city")} />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                {cities.map((city) => (
                                  <SelectItem key={city} value={city}>
                                    {city}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>

                    <FormField
                      control={form.control}
                      name="disappearanceDate"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>{t("form.disappearanceDate")} *</FormLabel>
                          <FormControl>
                            <Input
                              type="datetime-local"
                              value={field.value instanceof Date 
                                ? field.value.toISOString().slice(0, 16)
                                : ""}
                              onChange={(e) => field.onChange(new Date(e.target.value))}
                              data-testid="input-date"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="circumstances"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>{t("form.circumstances")} *</FormLabel>
                          <FormControl>
                            <Textarea
                              {...field}
                              placeholder={t("form.circumstances.placeholder")}
                              rows={4}
                              data-testid="textarea-circumstances"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <div>
                      <FormLabel>{t("form.location")}</FormLabel>
                      <FormDescription className="mb-2">
                        {t("form.location.help")}
                      </FormDescription>
                      <LeafletMap
                        height="h-64"
                        onClick={handleMapClick}
                        selectedPosition={selectedPosition}
                        zoom={selectedCountry ? 6 : 4}
                      />
                    </div>
                  </CardContent>
                </Card>
              )}

              {currentStep === 2 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FileText className="w-5 h-5" />
                      {t("form.step.description")}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <FormField
                      control={form.control}
                      name="physicalDescription"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>{t("form.physicalDescription")} *</FormLabel>
                          <FormControl>
                            <Textarea
                              {...field}
                              placeholder={t("form.physicalDescription.placeholder")}
                              rows={4}
                              data-testid="textarea-description"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="clothing"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>{t("form.clothing")} *</FormLabel>
                          <FormControl>
                            <Textarea {...field} rows={2} data-testid="textarea-clothing" />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="belongings"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>{t("form.belongings")}</FormLabel>
                          <FormControl>
                            <Textarea
                              {...field}
                              value={field.value || ""}
                              rows={2}
                              data-testid="textarea-belongings"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="photoUrl"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>{t("form.photo")}</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              value={field.value || ""}
                              placeholder="https://..."
                              data-testid="input-photo"
                            />
                          </FormControl>
                          <FormDescription>
                            URL de la photo
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </CardContent>
                </Card>
              )}

              {currentStep === 3 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Phone className="w-5 h-5" />
                      {t("form.step.contact")}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <FormLabel>{t("form.contacts")} *</FormLabel>
                        {fields.length < 3 && (
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() =>
                              append({ name: "", phone: "", email: "", relation: "" })
                            }
                            data-testid="button-add-contact"
                          >
                            <Plus className="w-4 h-4 mr-1" />
                            {t("form.addContact")}
                          </Button>
                        )}
                      </div>

                      {fields.map((field, index) => (
                        <div
                          key={field.id}
                          className="border border-border rounded-lg p-4 space-y-4"
                        >
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">
                              Contact {index + 1}
                            </span>
                            {fields.length > 1 && (
                              <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                onClick={() => remove(index)}
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            )}
                          </div>

                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <FormField
                              control={form.control}
                              name={`contacts.${index}.name`}
                              render={({ field }) => (
                                <FormItem>
                                  <FormLabel>{t("form.contact.name")} *</FormLabel>
                                  <FormControl>
                                    <Input {...field} data-testid={`input-contact-name-${index}`} />
                                  </FormControl>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />

                            <FormField
                              control={form.control}
                              name={`contacts.${index}.phone`}
                              render={({ field }) => (
                                <FormItem>
                                  <FormLabel>{t("form.contact.phone")} *</FormLabel>
                                  <FormControl>
                                    <Input {...field} data-testid={`input-contact-phone-${index}`} />
                                  </FormControl>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />

                            <FormField
                              control={form.control}
                              name={`contacts.${index}.email`}
                              render={({ field }) => (
                                <FormItem>
                                  <FormLabel>{t("form.contact.email")}</FormLabel>
                                  <FormControl>
                                    <Input
                                      {...field}
                                      type="email"
                                      data-testid={`input-contact-email-${index}`}
                                    />
                                  </FormControl>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />

                            <FormField
                              control={form.control}
                              name={`contacts.${index}.relation`}
                              render={({ field }) => (
                                <FormItem>
                                  <FormLabel>{t("form.contact.relation")}</FormLabel>
                                  <FormControl>
                                    <Input {...field} data-testid={`input-contact-relation-${index}`} />
                                  </FormControl>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />
                          </div>
                        </div>
                      ))}
                    </div>

                    <FormField
                      control={form.control}
                      name="consent"
                      render={({ field }) => (
                        <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-lg border p-4">
                          <FormControl>
                            <Checkbox
                              checked={field.value}
                              onCheckedChange={field.onChange}
                              data-testid="checkbox-consent"
                            />
                          </FormControl>
                          <div className="space-y-1 leading-none">
                            <FormLabel className="cursor-pointer">
                              {t("form.consent")} *
                            </FormLabel>
                            <FormDescription>{t("form.gdpr")}</FormDescription>
                          </div>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </CardContent>
                </Card>
              )}

              <div className="flex items-center justify-between pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={prevStep}
                  disabled={currentStep === 0}
                  data-testid="button-prev"
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  {t("form.previous")}
                </Button>

                {currentStep < STEPS.length - 1 ? (
                  <Button type="button" onClick={nextStep} data-testid="button-next">
                    {t("form.next")}
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                ) : (
                  <Button type="submit" disabled={mutation.isPending} data-testid="button-submit">
                    {mutation.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                    {t("form.submit")}
                  </Button>
                )}
              </div>
            </form>
          </Form>
        </div>
      </main>

      <Footer />
    </div>
  );
}
