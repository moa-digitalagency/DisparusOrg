import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
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
import { Flag, Loader2 } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";

const moderationSchema = z.object({
  reason: z.enum(["false_info", "duplicate", "inappropriate", "spam", "other"]),
  details: z.string().optional(),
  reporterContact: z.string().optional(),
});

type ModerationFormData = z.infer<typeof moderationSchema>;

interface ModerationDialogProps {
  targetType: "disparu" | "contribution";
  targetId: string;
  children?: React.ReactNode;
}

export function ModerationDialog({ targetType, targetId, children }: ModerationDialogProps) {
  const { t } = useI18n();
  const { toast } = useToast();
  const [open, setOpen] = useState(false);

  const form = useForm<ModerationFormData>({
    resolver: zodResolver(moderationSchema),
    defaultValues: {
      reason: "false_info",
      details: "",
      reporterContact: "",
    },
  });

  const mutation = useMutation({
    mutationFn: async (data: ModerationFormData) => {
      return apiRequest("POST", "/api/moderation", {
        ...data,
        targetType,
        targetId,
      });
    },
    onSuccess: () => {
      toast({
        title: t("success"),
        description: t("moderation.success"),
      });
      setOpen(false);
      form.reset();
    },
    onError: () => {
      toast({
        title: t("error"),
        variant: "destructive",
      });
    },
  });

  const onSubmit = (data: ModerationFormData) => {
    mutation.mutate(data);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {children || (
          <Button variant="outline" size="sm" data-testid="button-flag">
            <Flag className="w-4 h-4 mr-2" />
            {t("detail.flag")}
          </Button>
        )}
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{t("moderation.title")}</DialogTitle>
          <DialogDescription>
            {t("moderation.success")}
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="reason"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("moderation.reason")} *</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger data-testid="select-moderation-reason">
                        <SelectValue />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="false_info">{t("moderation.reason.false_info")}</SelectItem>
                      <SelectItem value="duplicate">{t("moderation.reason.duplicate")}</SelectItem>
                      <SelectItem value="inappropriate">{t("moderation.reason.inappropriate")}</SelectItem>
                      <SelectItem value="spam">{t("moderation.reason.spam")}</SelectItem>
                      <SelectItem value="other">{t("moderation.reason.other")}</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="details"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("moderation.details")}</FormLabel>
                  <FormControl>
                    <Textarea
                      {...field}
                      rows={3}
                      data-testid="textarea-moderation-details"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="reporterContact"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("moderation.contact")}</FormLabel>
                  <FormControl>
                    <Input {...field} data-testid="input-moderation-contact" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={() => setOpen(false)}>
                {t("cancel")}
              </Button>
              <Button type="submit" disabled={mutation.isPending} data-testid="button-moderation-submit">
                {mutation.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                {t("moderation.submit")}
              </Button>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
