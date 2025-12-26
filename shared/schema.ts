import { sql, relations } from "drizzle-orm";
import { pgTable, text, varchar, integer, timestamp, boolean, real, jsonb } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// Contact reference schema for repeated contacts
export const contactSchema = z.object({
  name: z.string().min(1),
  phone: z.string().min(1),
  email: z.string().email().optional().or(z.literal("")),
  relation: z.string().optional(),
});

export type Contact = z.infer<typeof contactSchema>;

// Person type enum
export const personTypeEnum = ["child", "adult", "senior"] as const;
export type PersonType = typeof personTypeEnum[number];

// Sex enum
export const sexEnum = ["male", "female", "unspecified"] as const;
export type Sex = typeof sexEnum[number];

// Status enum
export const statusEnum = ["missing", "found", "deceased"] as const;
export type Status = typeof statusEnum[number];

// Contribution type enum
export const contributionTypeEnum = ["sighting", "info", "police_report", "found", "other"] as const;
export type ContributionType = typeof contributionTypeEnum[number];

// Found state enum
export const foundStateEnum = ["safe", "injured", "deceased"] as const;
export type FoundState = typeof foundStateEnum[number];

// Moderation reason enum
export const moderationReasonEnum = ["false_info", "duplicate", "inappropriate", "spam", "other"] as const;
export type ModerationReason = typeof moderationReasonEnum[number];

// Users table (for admin/moderation)
export const users = pgTable("users", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
  role: text("role").default("user"),
});

// Missing persons table
export const disparus = pgTable("disparus", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  publicId: varchar("public_id", { length: 6 }).notNull().unique(),
  personType: text("person_type").notNull(), // child, adult, senior
  firstName: text("first_name").notNull(),
  lastName: text("last_name").notNull(),
  age: integer("age").notNull(),
  sex: text("sex").notNull(), // male, female, unspecified
  country: text("country").notNull(),
  city: text("city").notNull(),
  physicalDescription: text("physical_description").notNull(),
  photoUrl: text("photo_url"),
  disappearanceDate: timestamp("disappearance_date").notNull(),
  circumstances: text("circumstances").notNull(),
  latitude: real("latitude"),
  longitude: real("longitude"),
  clothing: text("clothing").notNull(),
  belongings: text("belongings"),
  contacts: jsonb("contacts").$type<Contact[]>().default([]),
  status: text("status").default("missing"), // missing, found, deceased
  foundState: text("found_state"), // safe, injured, deceased
  foundCircumstances: text("found_circumstances"),
  foundLatitude: real("found_latitude"),
  foundLongitude: real("found_longitude"),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
  isVerified: boolean("is_verified").default(false),
  isFlagged: boolean("is_flagged").default(false),
  viewCount: integer("view_count").default(0),
});

// Contributions table
export const contributions = pgTable("contributions", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  disparuId: varchar("disparu_id").notNull().references(() => disparus.id, { onDelete: "cascade" }),
  contributionType: text("contribution_type").notNull(), // sighting, info, police_report, found, other
  latitude: real("latitude"),
  longitude: real("longitude"),
  observationDate: timestamp("observation_date"),
  details: text("details").notNull(),
  proofUrl: text("proof_url"),
  foundState: text("found_state"), // if contribution type is 'found'
  returnCircumstances: text("return_circumstances"),
  returnLatitude: real("return_latitude"),
  returnLongitude: real("return_longitude"),
  contactName: text("contact_name"),
  contactPhone: text("contact_phone"),
  contactEmail: text("contact_email"),
  createdAt: timestamp("created_at").defaultNow(),
  isVerified: boolean("is_verified").default(false),
});

// Moderation reports table
export const moderationReports = pgTable("moderation_reports", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  targetType: text("target_type").notNull(), // disparu, contribution
  targetId: varchar("target_id").notNull(),
  reason: text("reason").notNull(), // false_info, duplicate, inappropriate, spam, other
  details: text("details"),
  reporterContact: text("reporter_contact"),
  status: text("status").default("pending"), // pending, reviewed, dismissed
  reviewedBy: varchar("reviewed_by"),
  reviewedAt: timestamp("reviewed_at"),
  createdAt: timestamp("created_at").defaultNow(),
});

// Relations
export const disparusRelations = relations(disparus, ({ many }) => ({
  contributions: many(contributions),
}));

export const contributionsRelations = relations(contributions, ({ one }) => ({
  disparu: one(disparus, {
    fields: [contributions.disparuId],
    references: [disparus.id],
  }),
}));

// Insert schemas
export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
});

export const insertDisparuSchema = createInsertSchema(disparus).omit({
  id: true,
  publicId: true,
  createdAt: true,
  updatedAt: true,
  isVerified: true,
  isFlagged: true,
  viewCount: true,
  status: true,
  foundState: true,
  foundCircumstances: true,
  foundLatitude: true,
  foundLongitude: true,
}).extend({
  contacts: z.array(contactSchema).min(1).max(3),
});

export const insertContributionSchema = createInsertSchema(contributions).omit({
  id: true,
  createdAt: true,
  isVerified: true,
});

export const insertModerationReportSchema = createInsertSchema(moderationReports).omit({
  id: true,
  status: true,
  reviewedBy: true,
  reviewedAt: true,
  createdAt: true,
});

// Types
export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;

export type InsertDisparu = z.infer<typeof insertDisparuSchema>;
export type Disparu = typeof disparus.$inferSelect;

export type InsertContribution = z.infer<typeof insertContributionSchema>;
export type Contribution = typeof contributions.$inferSelect;

export type InsertModerationReport = z.infer<typeof insertModerationReportSchema>;
export type ModerationReport = typeof moderationReports.$inferSelect;

// Search/filter types
export const searchFiltersSchema = z.object({
  query: z.string().optional(),
  status: z.enum(["all", ...statusEnum]).optional(),
  personType: z.enum(["all", ...personTypeEnum]).optional(),
  country: z.string().optional(),
  hasPhoto: z.boolean().optional(),
  dateFrom: z.string().optional(),
});

export type SearchFilters = z.infer<typeof searchFiltersSchema>;

// Countries and cities data
export const COUNTRIES_CITIES: Record<string, string[]> = {
  "Cameroun": ["Yaoundé", "Douala", "Garoua", "Bafoussam", "Bamenda", "Ngaoundéré", "Maroua", "Bertoua", "Ebolowa", "Kribi"],
  "Nigeria": ["Lagos", "Kano", "Ibadan", "Abuja", "Port Harcourt", "Benin City", "Kaduna", "Enugu", "Onitsha", "Jos"],
  "Côte d'Ivoire": ["Abidjan", "Bouaké", "Yamoussoukro", "Daloa", "Gagnoa", "Korhogo", "San Pedro", "Man", "Divo", "Séguéla"],
  "Sénégal": ["Dakar", "Thiès", "Kaolack", "Ziguinchor", "Saint-Louis", "Mbour", "Touba", "Rufisque", "Diourbel", "Tambacounda"],
  "Ghana": ["Accra", "Kumasi", "Tamale", "Sekondi-Takoradi", "Cape Coast", "Obuasi", "Tema", "Teshie", "Koforidua", "Ho"],
  "RD Congo": ["Kinshasa", "Lubumbashi", "Mbuji-Mayi", "Kisangani", "Goma", "Bukavu", "Kananga", "Likasi", "Kolwezi", "Matadi"],
  "Congo-Brazzaville": ["Brazzaville", "Pointe-Noire", "Dolisie", "Nkayi", "Ouesso", "Impfondo", "Owando", "Sibiti", "Madingou", "Kinkala"],
  "Mali": ["Bamako", "Sikasso", "Ségou", "Mopti", "Koutiala", "Kayes", "Gao", "Kidal", "Tombouctou", "San"],
  "Burkina Faso": ["Ouagadougou", "Bobo-Dioulasso", "Koudougou", "Banfora", "Ouahigouya", "Kaya", "Fada N'Gourma", "Tenkodogo", "Dédougou", "Dori"],
  "Niger": ["Niamey", "Zinder", "Maradi", "Tahoua", "Agadez", "Dosso", "Diffa", "Tillabéri", "Tessaoua", "Arlit"],
  "Guinée": ["Conakry", "Nzérékoré", "Kankan", "Kindia", "Labé", "Boké", "Mamou", "Siguiri", "Faranah", "Kissidougou"],
  "Bénin": ["Cotonou", "Porto-Novo", "Parakou", "Djougou", "Abomey", "Bohicon", "Natitingou", "Lokossa", "Ouidah", "Kandi"],
  "Togo": ["Lomé", "Sokodé", "Kara", "Kpalimé", "Atakpamé", "Bassar", "Tsévié", "Aného", "Mango", "Dapaong"],
  "Mauritanie": ["Nouakchott", "Nouadhibou", "Kiffa", "Kaédi", "Rosso", "Zouérat", "Atar", "Néma", "Aioun el Atrouss", "Sélibaby"],
  "Gabon": ["Libreville", "Port-Gentil", "Franceville", "Oyem", "Moanda", "Mouila", "Lambaréné", "Tchibanga", "Makokou", "Bitam"],
  "Centrafrique": ["Bangui", "Bimbo", "Berbérati", "Carnot", "Bambari", "Bouar", "Bria", "Bossangoa", "Nola", "Bangassou"],
  "Tchad": ["N'Djamena", "Moundou", "Sarh", "Abéché", "Kélo", "Koumra", "Bongor", "Am Timan", "Mongo", "Doba"],
  "Rwanda": ["Kigali", "Butare", "Gitarama", "Ruhengeri", "Gisenyi", "Byumba", "Cyangugu", "Kibungo", "Kibuye", "Nyanza"],
  "Burundi": ["Bujumbura", "Gitega", "Muyinga", "Ngozi", "Rumonge", "Bururi", "Makamba", "Kayanza", "Cibitoke", "Bubanza"],
  "Madagascar": ["Antananarivo", "Toamasina", "Antsirabe", "Fianarantsoa", "Mahajanga", "Toliara", "Antsiranana", "Ambovombe", "Morondava", "Manakara"],
  "Algérie": ["Alger", "Oran", "Constantine", "Annaba", "Blida", "Batna", "Sétif", "Djelfa", "Biskra", "Tébessa"],
  "Maroc": ["Casablanca", "Rabat", "Fès", "Marrakech", "Tanger", "Agadir", "Meknès", "Oujda", "Kenitra", "Tétouan"],
  "Tunisie": ["Tunis", "Sfax", "Sousse", "Kairouan", "Bizerte", "Gabès", "Ariana", "Gafsa", "Monastir", "Ben Arous"],
  "Égypte": ["Le Caire", "Alexandrie", "Gizeh", "Port-Saïd", "Suez", "Louxor", "Assouan", "Ismaïlia", "Tanta", "Zagazig"],
  "Kenya": ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret", "Thika", "Malindi", "Kitale", "Garissa", "Nyeri"],
  "Tanzanie": ["Dar es Salaam", "Dodoma", "Mwanza", "Arusha", "Zanzibar", "Mbeya", "Morogoro", "Tanga", "Kigoma", "Moshi"],
  "Ouganda": ["Kampala", "Gulu", "Lira", "Mbarara", "Jinja", "Mbale", "Masaka", "Entebbe", "Fort Portal", "Soroti"],
  "Éthiopie": ["Addis-Abeba", "Dire Dawa", "Mek'ele", "Gondar", "Bahir Dar", "Hawassa", "Jimma", "Dessie", "Harar", "Adama"],
  "Mozambique": ["Maputo", "Beira", "Nampula", "Chimoio", "Nacala", "Quelimane", "Tete", "Lichinga", "Pemba", "Xai-Xai"],
  "Angola": ["Luanda", "Huambo", "Lobito", "Benguela", "Lubango", "Malanje", "Namibe", "Cabinda", "Uíge", "Kuito"],
  "Afrique du Sud": ["Johannesburg", "Le Cap", "Durban", "Pretoria", "Port Elizabeth", "Bloemfontein", "East London", "Polokwane", "Nelspruit", "Kimberley"],
  "Zimbabwe": ["Harare", "Bulawayo", "Chitungwiza", "Mutare", "Gweru", "Kwekwe", "Kadoma", "Masvingo", "Chinhoyi", "Marondera"],
  "Zambie": ["Lusaka", "Kitwe", "Ndola", "Kabwe", "Chingola", "Mufulira", "Livingstone", "Luanshya", "Kasama", "Chipata"],
  "Malawi": ["Lilongwe", "Blantyre", "Mzuzu", "Zomba", "Kasungu", "Mangochi", "Karonga", "Salima", "Nkhotakota", "Liwonde"],
  "Liberia": ["Monrovia", "Gbarnga", "Kakata", "Buchanan", "Zwedru", "Harper", "Voinjama", "Sanniquellie", "Robertsport", "Greenville"],
  "Sierra Leone": ["Freetown", "Bo", "Kenema", "Makeni", "Koidu", "Lunsar", "Port Loko", "Kabala", "Magburaka", "Bonthe"],
};
