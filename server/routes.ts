import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import {
  insertDisparuSchema,
  insertContributionSchema,
  insertModerationReportSchema,
  searchFiltersSchema,
} from "@shared/schema";
import { z } from "zod";

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  // ============ DISPARUS ROUTES ============

  // Get all disparus with optional filters
  app.get("/api/disparus", async (req, res) => {
    try {
      const filters = searchFiltersSchema.parse({
        query: req.query.query as string | undefined,
        status: req.query.status as string | undefined,
        personType: req.query.personType as string | undefined,
        country: req.query.country as string | undefined,
        hasPhoto: req.query.hasPhoto === "true",
        dateFrom: req.query.dateFrom as string | undefined,
      });

      const disparus = await storage.getDisparus(filters);
      res.json(disparus);
    } catch (error) {
      console.error("Error fetching disparus:", error);
      res.status(500).json({ error: "Failed to fetch disparus" });
    }
  });

  // Get single disparu by publicId
  app.get("/api/disparus/:id", async (req, res) => {
    try {
      const { id } = req.params;
      const disparu = await storage.getDisparuByPublicId(id);
      
      if (!disparu) {
        return res.status(404).json({ error: "Not found" });
      }

      // Increment view count
      await storage.incrementViewCount(disparu.id);
      
      res.json(disparu);
    } catch (error) {
      console.error("Error fetching disparu:", error);
      res.status(500).json({ error: "Failed to fetch disparu" });
    }
  });

  // Create new disparu
  app.post("/api/disparus", async (req, res) => {
    try {
      const data = insertDisparuSchema.parse(req.body);
      const disparu = await storage.createDisparu(data);
      res.status(201).json(disparu);
    } catch (error) {
      console.error("Error creating disparu:", error);
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: "Validation failed", details: error.errors });
      }
      res.status(500).json({ error: "Failed to create disparu" });
    }
  });

  // Update disparu - only allow specific fields to be updated
  app.patch("/api/disparus/:id", async (req, res) => {
    try {
      const { id } = req.params;
      const disparu = await storage.getDisparuByPublicId(id);
      
      if (!disparu) {
        return res.status(404).json({ error: "Not found" });
      }

      // Only allow updating specific safe fields
      const allowedFields = [
        "status", "foundState", "foundCircumstances",
        "foundLatitude", "foundLongitude", "photoUrl"
      ] as const;
      
      const updates: Record<string, unknown> = {};
      for (const field of allowedFields) {
        if (field in req.body && req.body[field] !== undefined) {
          updates[field] = req.body[field];
        }
      }

      if (Object.keys(updates).length === 0) {
        return res.status(400).json({ error: "No valid fields to update" });
      }

      const updated = await storage.updateDisparu(disparu.id, updates);
      res.json(updated);
    } catch (error) {
      console.error("Error updating disparu:", error);
      res.status(500).json({ error: "Failed to update disparu" });
    }
  });

  // ============ CONTRIBUTIONS ROUTES ============

  // Get contributions for a disparu
  app.get("/api/contributions/:disparuPublicId", async (req, res) => {
    try {
      const { disparuPublicId } = req.params;
      const disparu = await storage.getDisparuByPublicId(disparuPublicId);
      
      if (!disparu) {
        return res.status(404).json({ error: "Disparu not found" });
      }

      const contributionsList = await storage.getContributionsByDisparuId(disparu.id);
      res.json(contributionsList);
    } catch (error) {
      console.error("Error fetching contributions:", error);
      res.status(500).json({ error: "Failed to fetch contributions" });
    }
  });

  // Create new contribution
  app.post("/api/contributions", async (req, res) => {
    try {
      const data = insertContributionSchema.parse(req.body);
      const contribution = await storage.createContribution(data);
      res.status(201).json(contribution);
    } catch (error) {
      console.error("Error creating contribution:", error);
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: "Validation failed", details: error.errors });
      }
      res.status(500).json({ error: "Failed to create contribution" });
    }
  });

  // ============ MODERATION ROUTES ============

  // Create moderation report
  app.post("/api/moderation", async (req, res) => {
    try {
      const data = insertModerationReportSchema.parse(req.body);
      const report = await storage.createModerationReport(data);
      res.status(201).json(report);
    } catch (error) {
      console.error("Error creating moderation report:", error);
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: "Validation failed", details: error.errors });
      }
      res.status(500).json({ error: "Failed to create report" });
    }
  });

  // Get moderation reports (admin only - no auth for MVP)
  app.get("/api/moderation", async (req, res) => {
    try {
      const reports = await storage.getModerationReports();
      res.json(reports);
    } catch (error) {
      console.error("Error fetching moderation reports:", error);
      res.status(500).json({ error: "Failed to fetch reports" });
    }
  });

  // ============ STATS ROUTE ============

  app.get("/api/stats", async (req, res) => {
    try {
      const stats = await storage.getStats();
      res.json(stats);
    } catch (error) {
      console.error("Error fetching stats:", error);
      res.status(500).json({ error: "Failed to fetch stats" });
    }
  });

  return httpServer;
}
