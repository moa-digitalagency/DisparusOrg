import {
  type User,
  type InsertUser,
  type Disparu,
  type InsertDisparu,
  type Contribution,
  type InsertContribution,
  type ModerationReport,
  type InsertModerationReport,
  type SearchFilters,
  users,
  disparus,
  contributions,
  moderationReports,
} from "@shared/schema";
import { db } from "./db";
import { eq, desc, ilike, and, or, sql } from "drizzle-orm";
import { randomBytes } from "crypto";

// Generate 6-character alphanumeric ID
function generatePublicId(): string {
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  let result = "";
  const bytes = randomBytes(6);
  for (let i = 0; i < 6; i++) {
    result += chars[bytes[i] % chars.length];
  }
  return result;
}

export interface IStorage {
  // Users
  getUser(id: string): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;

  // Disparus
  getDisparus(filters?: SearchFilters): Promise<Disparu[]>;
  getDisparuById(id: string): Promise<Disparu | undefined>;
  getDisparuByPublicId(publicId: string): Promise<Disparu | undefined>;
  createDisparu(disparu: InsertDisparu): Promise<Disparu>;
  updateDisparu(id: string, updates: Partial<Disparu>): Promise<Disparu | undefined>;
  incrementViewCount(id: string): Promise<void>;

  // Contributions
  getContributionsByDisparuId(disparuId: string): Promise<Contribution[]>;
  createContribution(contribution: InsertContribution): Promise<Contribution>;

  // Moderation
  createModerationReport(report: InsertModerationReport): Promise<ModerationReport>;
  getModerationReports(): Promise<ModerationReport[]>;

  // Stats
  getStats(): Promise<{
    total: number;
    found: number;
    countries: number;
    contributions: number;
  }>;
}

export class DatabaseStorage implements IStorage {
  // Users
  async getUser(id: string): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.id, id));
    return user || undefined;
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.username, username));
    return user || undefined;
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const [user] = await db.insert(users).values(insertUser).returning();
    return user;
  }

  // Disparus
  async getDisparus(filters?: SearchFilters): Promise<Disparu[]> {
    let query = db.select().from(disparus);
    
    const conditions = [];
    
    if (filters?.query) {
      const searchTerm = `%${filters.query}%`;
      conditions.push(
        or(
          ilike(disparus.firstName, searchTerm),
          ilike(disparus.lastName, searchTerm),
          ilike(disparus.publicId, searchTerm),
          ilike(disparus.city, searchTerm),
          ilike(disparus.country, searchTerm)
        )
      );
    }
    
    if (filters?.status && filters.status !== "all") {
      conditions.push(eq(disparus.status, filters.status));
    }
    
    if (filters?.personType && filters.personType !== "all") {
      conditions.push(eq(disparus.personType, filters.personType));
    }
    
    if (filters?.country) {
      conditions.push(eq(disparus.country, filters.country));
    }
    
    if (filters?.hasPhoto) {
      conditions.push(sql`${disparus.photoUrl} IS NOT NULL AND ${disparus.photoUrl} != ''`);
    }

    if (conditions.length > 0) {
      query = query.where(and(...conditions)) as typeof query;
    }
    
    return query.orderBy(desc(disparus.createdAt)).limit(100);
  }

  async getDisparuById(id: string): Promise<Disparu | undefined> {
    const [disparu] = await db.select().from(disparus).where(eq(disparus.id, id));
    return disparu || undefined;
  }

  async getDisparuByPublicId(publicId: string): Promise<Disparu | undefined> {
    const [disparu] = await db.select().from(disparus).where(eq(disparus.publicId, publicId));
    return disparu || undefined;
  }

  async createDisparu(insertDisparu: InsertDisparu): Promise<Disparu> {
    const publicId = generatePublicId();
    const [disparu] = await db
      .insert(disparus)
      .values({
        ...insertDisparu,
        publicId,
        status: "missing",
      })
      .returning();
    return disparu;
  }

  async updateDisparu(id: string, updates: Partial<Disparu>): Promise<Disparu | undefined> {
    const [disparu] = await db
      .update(disparus)
      .set({ ...updates, updatedAt: new Date() })
      .where(eq(disparus.id, id))
      .returning();
    return disparu || undefined;
  }

  async incrementViewCount(id: string): Promise<void> {
    await db
      .update(disparus)
      .set({ viewCount: sql`${disparus.viewCount} + 1` })
      .where(eq(disparus.id, id));
  }

  // Contributions
  async getContributionsByDisparuId(disparuId: string): Promise<Contribution[]> {
    return db
      .select()
      .from(contributions)
      .where(eq(contributions.disparuId, disparuId))
      .orderBy(desc(contributions.createdAt));
  }

  async createContribution(insertContribution: InsertContribution): Promise<Contribution> {
    const [contribution] = await db
      .insert(contributions)
      .values(insertContribution)
      .returning();
    
    // If the contribution marks the person as found, update their status
    if (insertContribution.contributionType === "found" && insertContribution.foundState) {
      const status = insertContribution.foundState === "deceased" ? "deceased" : "found";
      await db
        .update(disparus)
        .set({
          status,
          foundState: insertContribution.foundState,
          foundCircumstances: insertContribution.returnCircumstances,
          foundLatitude: insertContribution.returnLatitude,
          foundLongitude: insertContribution.returnLongitude,
          updatedAt: new Date(),
        })
        .where(eq(disparus.id, insertContribution.disparuId));
    }
    
    return contribution;
  }

  // Moderation
  async createModerationReport(insertReport: InsertModerationReport): Promise<ModerationReport> {
    const [report] = await db
      .insert(moderationReports)
      .values(insertReport)
      .returning();
    
    // Flag the target if it's a disparu
    if (insertReport.targetType === "disparu") {
      await db
        .update(disparus)
        .set({ isFlagged: true })
        .where(eq(disparus.id, insertReport.targetId));
    }
    
    return report;
  }

  async getModerationReports(): Promise<ModerationReport[]> {
    return db
      .select()
      .from(moderationReports)
      .orderBy(desc(moderationReports.createdAt));
  }

  // Stats
  async getStats(): Promise<{
    total: number;
    found: number;
    countries: number;
    contributions: number;
  }> {
    const [totalResult] = await db
      .select({ count: sql<number>`count(*)::int` })
      .from(disparus);
    
    const [foundResult] = await db
      .select({ count: sql<number>`count(*)::int` })
      .from(disparus)
      .where(eq(disparus.status, "found"));
    
    const [countriesResult] = await db
      .select({ count: sql<number>`count(distinct ${disparus.country})::int` })
      .from(disparus);
    
    const [contributionsResult] = await db
      .select({ count: sql<number>`count(*)::int` })
      .from(contributions);

    return {
      total: totalResult?.count || 0,
      found: foundResult?.count || 0,
      countries: countriesResult?.count || 0,
      contributions: contributionsResult?.count || 0,
    };
  }
}

export const storage = new DatabaseStorage();
