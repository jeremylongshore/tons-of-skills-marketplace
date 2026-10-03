import express, { type Express, type Request, type Response, type NextFunction } from 'express';
import cors from 'cors';
import { createServer, type Server } from 'http';
import type { ConversationWatcher } from './watcher.js';
import type { AnalyticsServer } from './server.js';
import type { AttributionEngine } from './attribution.js';

/**
 * Strip CR/LF and other control characters before a request-derived value is
 * written to the console. `req.method` / `req.path` are client-controlled,
 * so logging them raw risks forged/injected log lines (CodeQL
 * js/log-injection).
 */
function sanitizeForLog(value: unknown): string {
  return String(value).replace(/[\r\n\x00-\x1f\x7f]/g, '');
}

/**
 * HTTP API for analytics data access
 */
export class AnalyticsAPI {
  private app: Express;
  private server: Server | null = null;
  private port: number;
  private host: string;

  constructor(
    private watcher: ConversationWatcher,
    private wsServer: AnalyticsServer,
    private attribution: AttributionEngine,
    config: { port?: number; host?: string } = {}
  ) {
    this.port = config.port ?? 3333;
    this.host = config.host ?? 'localhost';
    this.app = express();

    this.setupMiddleware();
    this.setupRoutes();
  }

  /**
   * Configure Express middleware
   */
  private setupMiddleware(): void {
    // CORS for local access only
    this.app.use(
      cors({
        origin: ['http://localhost:*', 'http://127.0.0.1:*'],
        credentials: true,
      })
    );

    // JSON body parsing
    this.app.use(express.json());

    // Request logging
    this.app.use((req, res, next) => {
      console.log(`[API] ${sanitizeForLog(req.method)} ${sanitizeForLog(req.path)}`);
      next();
    });
  }

  /**
   * Setup API routes
   */
  private setupRoutes(): void {
    // Health check
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        timestamp: Date.now(),
        uptime: process.uptime(),
      });
    });

    // List all sessions
    this.app.get('/api/sessions', (req, res) => {
      this.handleGetSessions(req, res);
    });

    // Get session details
    this.app.get('/api/session/:id', (req, res) => {
      this.handleGetSession(req, res);
    });

    // Server status
    this.app.get('/api/status', (req, res) => {
      this.handleGetStatus(req, res);
    });

    // WebSocket info endpoint
    this.app.get('/api/realtime', (req, res) => {
      const wsStatus = this.wsServer.getStatus();
      res.json({
        websocket: {
          url: `ws://${wsStatus.host}:${wsStatus.port}`,
          running: wsStatus.running,
          clients: wsStatus.clients,
        },
        instructions: {
          connect: `const ws = new WebSocket('ws://${wsStatus.host}:${wsStatus.port}');`,
          events: [
            'plugin.activation',
            'skill.trigger',
            'llm.call',
            'cost.update',
            'rate_limit.warning',
            'conversation.created',
            'conversation.updated',
            'mcp.tool_call',
          ],
        },
      });
    });

    // Attribution endpoints
    this.app.get('/api/attribution/stats', (req, res) => {
      this.handleGetAttributionStats(req, res);
    });

    this.app.get('/api/attribution/plugins', (req, res) => {
      this.handleGetPluginAttribution(req, res);
    });

    this.app.get('/api/attribution/skills', (req, res) => {
      this.handleGetSkillAttribution(req, res);
    });

    this.app.get('/api/attribution/mcp', (req, res) => {
      this.handleGetMCPAttribution(req, res);
    });

    this.app.get('/api/attribution/top/:type', (req, res) => {
      this.handleGetTopUsed(req, res);
    });

    this.app.get('/api/attribution/recent/:type', (req, res) => {
      this.handleGetRecentlyUsed(req, res);
    });

    // 404 handler
    this.app.use((req, res) => {
      res.status(404).json({
        error: 'Not Found',
        message: `Route ${req.method} ${req.path} does not exist`,
      });
    });

    // Error handler
    this.app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
      console.error('API error:', err);
      res.status(500).json({
        error: 'Internal Server Error',
        message: err.message,
      });
    });
  }

  /**
   * Handle GET /api/sessions
   */
  private handleGetSessions(req: Request, res: Response): void {
    try {
      const conversations = this.watcher.getConversations();

      const sessions = conversations.map((conv) => ({
        id: conv.id,
        title: conv.title ?? 'Untitled',
        messageCount: conv.messages.length,
        plugins: conv.metadata?.plugins ?? [],
        skills: conv.metadata?.skills ?? [],
        model: conv.metadata?.model,
        lastMessage: conv.messages[conv.messages.length - 1]?.timestamp,
      }));

      res.json({
        sessions,
        total: sessions.length,
        timestamp: Date.now(),
      });
    } catch (error) {
      console.error('Error fetching sessions:', error);
      res.status(500).json({
        error: 'Failed to fetch sessions',
        message: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  }

  /**
   * Handle GET /api/session/:id
   */
  private handleGetSession(req: Request, res: Response): void {
    try {
      const { id } = req.params;
      const conversation = this.watcher.getConversation(String(id));

      if (!conversation) {
        res.status(404).json({
          error: 'Not Found',
          message: `Session ${id} not found`,
        });
        return;
      }

      // Return full conversation details
      res.json({
        id: conversation.id,
        title: conversation.title ?? 'Untitled',
        messageCount: conversation.messages.length,
        metadata: conversation.metadata,
        messages: conversation.messages.map((msg) => ({
          role: msg.role,
          timestamp: msg.timestamp,
          plugin: msg.metadata?.plugin,
          skill: msg.metadata?.skill,
          tokens: msg.metadata?.tokens,
          // Don't include full content for privacy
          hasContent: !!msg.content,
          contentLength: msg.content?.length ?? 0,
        })),
        timestamp: Date.now(),
      });
    } catch (error) {
      console.error('Error fetching session:', error);
      res.status(500).json({
        error: 'Failed to fetch session',
        message: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  }

  /**
   * Handle GET /api/status
   */
  private handleGetStatus(req: Request, res: Response): void {
    const wsStatus = this.wsServer.getStatus();
    const conversations = this.watcher.getConversations();
    const attributionStats = this.attribution.getStats();

    res.json({
      api: {
        running: this.server !== null,
        host: this.host,
        port: this.port,
      },
      websocket: wsStatus,
      watcher: {
        conversationCount: conversations.length,
        totalMessages: conversations.reduce((sum, c) => sum + c.messages.length, 0),
      },
      attribution: {
        pluginCount: attributionStats.plugins.size,
        skillCount: attributionStats.skills.size,
        mcpToolCount: attributionStats.mcpTools.size,
        lastUpdated: attributionStats.lastUpdated,
      },
      system: {
        uptime: process.uptime(),
        nodeVersion: process.version,
        platform: process.platform,
      },
      timestamp: Date.now(),
    });
  }

  /**
   * Handle GET /api/attribution/stats
   */
  private handleGetAttributionStats(req: Request, res: Response): void {
    try {
      const stats = this.attribution.getStats();

      res.json({
        summary: {
          totalPlugins: stats.plugins.size,
          totalSkills: stats.skills.size,
          totalMCPTools: stats.mcpTools.size,
          lastUpdated: stats.lastUpdated,
        },
        topPlugins: Array.from(stats.plugins.values())
          .sort((a, b) => b.activationCount - a.activationCount)
          .slice(0, 10)
          .map(p => ({
            name: p.name,
            activationCount: p.activationCount,
            lastActivated: p.lastActivated,
            conversationCount: p.conversationIds.size,
          })),
        topSkills: Array.from(stats.skills.values())
          .sort((a, b) => b.activationCount - a.activationCount)
          .slice(0, 10)
          .map(s => ({
            name: s.name,
            activationCount: s.activationCount,
            lastActivated: s.lastActivated,
            conversationCount: s.conversationIds.size,
            pluginName: s.metadata?.pluginName,
          })),
        topMCPTools: Array.from(stats.mcpTools.values())
          .sort((a, b) => b.activationCount - a.activationCount)
          .slice(0, 10)
          .map(m => ({
            name: m.name,
            activationCount: m.activationCount,
            lastActivated: m.lastActivated,
            conversationCount: m.conversationIds.size,
            mcpServer: m.metadata?.mcpServer,
          })),
        timestamp: Date.now(),
      });
    } catch (error) {
      console.error('Error fetching attribution stats:', error);
      res.status(500).json({
        error: 'Failed to fetch attribution stats',
        message: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  }

  /**
   * Handle GET /api/attribution/plugins
   */
  private handleGetPluginAttribution(req: Request, res: Response): void {
    try {
      const stats = this.attribution.getStats();
      const plugins = Array.from(stats.plugins.values()).map(p => ({
        name: p.name,
        type: p.type,
        activationCount: p.activationCount,
        lastActivated: p.lastActivated,
        conversationCount: p.conversationIds.size,
        marketplace: p.metadata?.marketplace,
      }));

      res.json({
        plugins,
        total: plugins.length,
        timestamp: Date.now(),
      });
    } catch (error) {
      console.error('Error fetching plugin attribution:', error);
      res.status(500).json({
        error: 'Failed to fetch plugin attribution',
        message: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  }

  /**
   * Handle GET /api/attribution/skills
   */
  private handleGetSkillAttribution(req: Request, res: Response): void {
    try {
      const stats = this.attribution.getStats();
      const skills = Array.from(stats.skills.values()).map(s => ({
        name: s.name,
        type: s.type,
        activationCount: s.activationCount,
        lastActivated: s.lastActivated,
        conversationCount: s.conversationIds.size,
        pluginName: s.metadata?.pluginName,
      }));

      res.json({
        skills,
        total: skills.length,
        timestamp: Date.now(),
      });
    } catch (error) {
      console.error('Error fetching skill attribution:', error);
      res.status(500).json({
        error: 'Failed to fetch skill attribution',
        message: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  }

  /**
   * Handle GET /api/attribution/mcp
   */
  private handleGetMCPAttribution(req: Request, res: Response): void {
    try {
      const stats = this.attribution.getStats();
      const mcpTools = Array.from(stats.mcpTools.values()).map(m => ({
        name: m.name,
        type: m.type,
        activationCount: m.activationCount,
        lastActivated: m.lastActivated,
        conversationCount: m.conversationIds.size,
        mcpServer: m.metadata?.mcpServer,
      }));

      res.json({
        mcpTools,
        total: mcpTools.length,
        timestamp: Date.now(),
      });
    } catch (error) {
      console.error('Error fetching MCP attribution:', error);
      res.status(500).json({
        error: 'Failed to fetch MCP attribution',
        message: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  }

  /**
   * Validate and sanitize limit parameter
   * Returns a safe limit value between 1 and MAX_LIMIT
   */
  private validateLimit(limitParam: unknown): number {
    const MAX_LIMIT = 1000;
    const DEFAULT_LIMIT = 10;

    if (limitParam === undefined || limitParam === null || limitParam === '') {
      return DEFAULT_LIMIT;
    }

    const parsed = parseInt(String(limitParam), 10);

    // Handle NaN, negative, zero, or non-integer values
    if (!Number.isInteger(parsed) || parsed < 1) {
      return DEFAULT_LIMIT;
    }

    // Cap at maximum to prevent DoS
    return Math.min(parsed, MAX_LIMIT);
  }

  /**
   * Handle GET /api/attribution/top/:type
   */
  private handleGetTopUsed(req: Request, res: Response): void {
    try {
      const { type } = req.params;
      const limit = this.validateLimit(req.query.limit);

      if (!['plugin', 'skill', 'mcp'].includes(String(type))) {
        res.status(400).json({
          error: 'Bad Request',
          message: 'Type must be one of: plugin, skill, mcp',
        });
        return;
      }

      const topUsed = this.attribution.getTopUsed(type as 'plugin' | 'skill' | 'mcp', limit);

      res.json({
        type,
        items: topUsed.map(item => ({
          name: item.name,
          activationCount: item.activationCount,
          lastActivated: item.lastActivated,
          conversationCount: item.conversationIds.size,
          metadata: item.metadata,
        })),
        total: topUsed.length,
        timestamp: Date.now(),
      });
    } catch (error) {
      console.error('Error fetching top used:', error);
      res.status(500).json({
        error: 'Failed to fetch top used',
        message: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  }

  /**
   * Handle GET /api/attribution/recent/:type
   */
  private handleGetRecentlyUsed(req: Request, res: Response): void {
    try {
      const { type } = req.params;
      const limit = this.validateLimit(req.query.limit);

      if (!['plugin', 'skill', 'mcp'].includes(String(type))) {
        res.status(400).json({
          error: 'Bad Request',
          message: 'Type must be one of: plugin, skill, mcp',
        });
        return;
      }

      const recentlyUsed = this.attribution.getRecentlyUsed(type as 'plugin' | 'skill' | 'mcp', limit);

      res.json({
        type,
        items: recentlyUsed.map(item => ({
          name: item.name,
          activationCount: item.activationCount,
          lastActivated: item.lastActivated,
          conversationCount: item.conversationIds.size,
          metadata: item.metadata,
        })),
        total: recentlyUsed.length,
        timestamp: Date.now(),
      });
    } catch (error) {
      console.error('Error fetching recently used:', error);
      res.status(500).json({
        error: 'Failed to fetch recently used',
        message: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  }

  /**
   * Start the HTTP API server
   */
  start(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.server) {
        console.warn('API server already started');
        resolve();
        return;
      }

      this.server = createServer(this.app);

      this.server.on('error', (error) => {
        console.error('HTTP API error:', error);
        reject(error);
      });

      this.server.listen(this.port, this.host, () => {
        console.log(`Analytics API listening on http://${this.host}:${this.port}`);
        console.log(`  Health check: http://${this.host}:${this.port}/health`);
        console.log(`  Sessions: http://${this.host}:${this.port}/api/sessions`);
        console.log(`  Status: http://${this.host}:${this.port}/api/status`);
        resolve();
      });
    });
  }

  /**
   * Stop the HTTP API server
   */
  async stop(): Promise<void> {
    return new Promise((resolve) => {
      if (!this.server) {
        resolve();
        return;
      }

      this.server.close(() => {
        this.server = null;
        console.log('Analytics API stopped');
        resolve();
      });
    });
  }

  /**
   * Get Express app instance (for testing)
   */
  getApp(): Express {
    return this.app;
  }
}
