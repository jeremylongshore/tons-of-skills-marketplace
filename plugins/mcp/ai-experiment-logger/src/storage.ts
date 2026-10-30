/**
 * AI Experiment Logger - Storage Layer
 * Handles data persistence to JSON file
 */

import { open, mkdir, lstat, rename, unlink } from 'fs/promises';
import { constants } from 'fs';
import { randomUUID } from 'crypto';
import { join } from 'path';
import { homedir } from 'os';
import type { Experiment, ExperimentInput, ExperimentFilters, ExperimentStatistics, StorageData } from './types.js';

const DATA_DIR = join(homedir(), '.ai-experiment-logger');
const DATA_FILE = join(DATA_DIR, 'experiments.json');
const VERSION = '1.0.0';

export class ExperimentStorage {
  private data: StorageData = {
    experiments: [],
    version: VERSION
  };

  private writes: Promise<void> = Promise.resolve();

  private async ensureDirectory(): Promise<void> {
    await mkdir(DATA_DIR, { recursive: true, mode: 0o700 });
    const info = await lstat(DATA_DIR);
    if (!info.isDirectory() || info.isSymbolicLink()) {
      throw new Error('Experiment storage directory is unsafe; nothing was changed.');
    }
  }

  private async readData(): Promise<StorageData | null> {
    let file;
    try {
      // Open first: all content reads use this descriptor, never a path that
      // was checked earlier. O_NOFOLLOW also rejects final-component symlinks.
      file = await open(DATA_FILE, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0));
    } catch (error) {
      if (error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT') return null;
      throw new Error('Cannot safely read experiment data; existing files were not changed.');
    }
    try {
      const opened = await file.stat();
      const current = await lstat(DATA_FILE);
      if (!opened.isFile() || !current.isFile() || current.isSymbolicLink() ||
          opened.ino !== current.ino || opened.dev !== current.dev) {
        throw new Error('Cannot safely read experiment data; existing files were not changed.');
      }
      let parsed: unknown;
      try {
        parsed = JSON.parse(await file.readFile('utf8'));
      } catch {
        throw new Error('Stored experiment data is invalid; existing files were not changed.');
      }
      if (!parsed || typeof parsed !== 'object' || !('version' in parsed) || parsed.version !== VERSION ||
          !('experiments' in parsed) || !Array.isArray(parsed.experiments) ||
          !parsed.experiments.every((item: unknown) => {
            if (!item || typeof item !== 'object') return false;
            const row = item as Record<string, unknown>;
            return ['id', 'date', 'aiTool', 'prompt', 'result', 'createdAt', 'updatedAt']
              .every(key => typeof row[key] === 'string') &&
              typeof row.rating === 'number' && Number.isFinite(row.rating) && row.rating >= 1 && row.rating <= 5 &&
              Array.isArray(row.tags) && row.tags.every((tag: unknown) => typeof tag === 'string');
          })) {
        throw new Error('Stored experiment data has an invalid shape; existing files were not changed.');
      }
      return parsed as StorageData;
    } finally {
      await file.close();
    }
  }

  private async withWriteLock<T>(operation: () => Promise<T>): Promise<T> {
    await this.ensureDirectory();
    const lockPath = join(DATA_DIR, '.experiments.lock');
    let lock;
    try {
      lock = await open(lockPath, 'wx', 0o600);
    } catch {
      throw new Error('Experiment storage is busy or unavailable; nothing was written. Stop stale writers before recovering a lock.');
    }
    let identity;
    try {
      identity = await lock.stat();
      await lock.writeFile(JSON.stringify({ pid: process.pid }) + '\n');
      return await operation();
    } finally {
      await lock.close().catch(() => {
        console.error('Experiment storage lock descriptor cleanup failed; inspect it with all writers stopped.');
      });
      try {
        const current = await lstat(lockPath);
        if (identity && current.isFile() && current.ino === identity.ino && current.dev === identity.dev) {
          await unlink(lockPath);
        }
      } catch {
        // A completed write must not be reported as uncommitted solely because
        // cleanup failed. The remaining lock fails future writes closed.
        console.error('Experiment storage lock cleanup failed; inspect it with all writers stopped.');
      }
    }
  }

  private async writeSnapshot(data: StorageData): Promise<void> {
    const temporary = join(DATA_DIR, `.experiments-${randomUUID()}.tmp`);
    let file;
    let committed = false;
    try {
      file = await open(temporary, 'wx', 0o600);
      await file.writeFile(JSON.stringify(data, null, 2), 'utf8');
      await file.sync();
      await file.close();
      file = undefined;
      await rename(temporary, DATA_FILE);
      committed = true;
    } catch {
      throw new Error('Unable to save experiment data; previous records were preserved.');
    } finally {
      if (file) await file.close().catch(() => {});
      if (!committed) await unlink(temporary).catch(() => {});
    }
  }

  async initialize(): Promise<void> {
    await this.ensureDirectory();
    const existing = await this.readData();
    if (existing) {
      this.data = existing;
      return;
    }
    await this.withWriteLock(async () => {
      const current = await this.readData();
      if (current) this.data = current;
      else await this.writeSnapshot(this.data);
    });
  }

  private async refresh(): Promise<void> {
    await this.ensureDirectory();
    const current = await this.readData();
    if (!current) throw new Error('Experiment data disappeared; existing records were not replaced.');
    this.data = current;
  }

  private mutate<T>(change: (draft: StorageData) => { value: T; changed: boolean }): Promise<T> {
    const operation = this.writes.then(() => this.withWriteLock(async () => {
      const current = await this.readData();
      if (!current) throw new Error('Experiment data disappeared; existing records were not replaced.');
      const draft = structuredClone(current);
      const result = change(draft);
      if (result.changed) await this.writeSnapshot(draft);
      this.data = draft;
      return structuredClone(result.value);
    }));
    this.writes = operation.then(() => {}, () => {});
    return operation;
  }

  private generateId(): string {
    return `exp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  async createExperiment(input: ExperimentInput): Promise<Experiment> {
    const now = new Date().toISOString();
    const experiment: Experiment = {
      id: this.generateId(),
      date: input.date || now,
      aiTool: input.aiTool,
      prompt: input.prompt,
      result: input.result,
      rating: input.rating,
      tags: [...(input.tags || [])],
      createdAt: now,
      updatedAt: now
    };

    return this.mutate(draft => {
      draft.experiments.push(experiment);
      return { value: experiment, changed: true };
    });
  }

  async getExperiment(id: string): Promise<Experiment | null> {
    await this.refresh();
    return structuredClone(this.data.experiments.find(exp => exp.id === id) || null);
  }

  async listExperiments(filters?: ExperimentFilters): Promise<Experiment[]> {
    await this.refresh();
    let experiments = structuredClone(this.data.experiments);

    if (filters) {
      if (filters.aiTool) {
        experiments = experiments.filter(exp =>
          exp.aiTool.toLowerCase().includes(filters.aiTool!.toLowerCase())
        );
      }

      if (filters.rating !== undefined) {
        experiments = experiments.filter(exp => exp.rating === filters.rating);
      }

      if (filters.tags && filters.tags.length > 0) {
        experiments = experiments.filter(exp =>
          filters.tags!.some(tag => exp.tags.includes(tag))
        );
      }

      if (filters.dateFrom) {
        experiments = experiments.filter(exp => exp.date >= filters.dateFrom!);
      }

      if (filters.dateTo) {
        experiments = experiments.filter(exp => exp.date <= filters.dateTo!);
      }

      if (filters.searchQuery) {
        const query = filters.searchQuery.toLowerCase();
        experiments = experiments.filter(exp =>
          exp.aiTool.toLowerCase().includes(query) ||
          exp.prompt.toLowerCase().includes(query) ||
          exp.result.toLowerCase().includes(query) ||
          exp.tags.some(tag => tag.toLowerCase().includes(query))
        );
      }
    }

    // Sort by date (newest first)
    return experiments.sort((a, b) =>
      new Date(b.date).getTime() - new Date(a.date).getTime()
    );
  }

  async updateExperiment(id: string, updates: Partial<ExperimentInput>): Promise<Experiment | null> {
    return this.mutate<Experiment | null>(draft => {
      const index = draft.experiments.findIndex(exp => exp.id === id);
      if (index === -1) return { value: null, changed: false };
      const updated: Experiment = { ...draft.experiments[index], ...updates, updatedAt: new Date().toISOString() };
      draft.experiments[index] = updated;
      return { value: updated, changed: true };
    });
  }

  async deleteExperiment(id: string): Promise<boolean> {
    return this.mutate(draft => {
      const index = draft.experiments.findIndex(exp => exp.id === id);
      if (index === -1) return { value: false, changed: false };
      draft.experiments.splice(index, 1);
      return { value: true, changed: true };
    });
  }

  async getStatistics(): Promise<ExperimentStatistics> {
    await this.refresh();
    const experiments = this.data.experiments;
    const totalExperiments = experiments.length;

    if (totalExperiments === 0) {
      return {
        totalExperiments: 0,
        averageRating: 0,
        toolStats: [],
        ratingDistribution: [],
        topTags: [],
        recentActivity: []
      };
    }

    // Average rating
    const averageRating = experiments.reduce((sum, exp) => sum + exp.rating, 0) / totalExperiments;

    // Tool statistics
    const toolMap = new Map<string, { count: number; totalRating: number }>();
    experiments.forEach(exp => {
      const current = toolMap.get(exp.aiTool) || { count: 0, totalRating: 0 };
      toolMap.set(exp.aiTool, {
        count: current.count + 1,
        totalRating: current.totalRating + exp.rating
      });
    });

    const toolStats = Array.from(toolMap.entries())
      .map(([tool, stats]) => ({
        tool,
        count: stats.count,
        averageRating: stats.totalRating / stats.count
      }))
      .sort((a, b) => b.count - a.count);

    // Rating distribution
    const ratingMap = new Map<number, number>();
    experiments.forEach(exp => {
      ratingMap.set(exp.rating, (ratingMap.get(exp.rating) || 0) + 1);
    });

    const ratingDistribution = Array.from(ratingMap.entries())
      .map(([rating, count]) => ({ rating, count }))
      .sort((a, b) => a.rating - b.rating);

    // Top tags
    const tagMap = new Map<string, number>();
    experiments.forEach(exp => {
      exp.tags.forEach(tag => {
        tagMap.set(tag, (tagMap.get(tag) || 0) + 1);
      });
    });

    const topTags = Array.from(tagMap.entries())
      .map(([tag, count]) => ({ tag, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);

    // Recent activity (last 30 days)
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    const activityMap = new Map<string, number>();
    experiments
      .filter(exp => new Date(exp.date) >= thirtyDaysAgo)
      .forEach(exp => {
        const dateStr = exp.date.split('T')[0];
        activityMap.set(dateStr, (activityMap.get(dateStr) || 0) + 1);
      });

    const recentActivity = Array.from(activityMap.entries())
      .map(([date, count]) => ({ date, count }))
      .sort((a, b) => a.date.localeCompare(b.date));

    return {
      totalExperiments,
      averageRating: Math.round(averageRating * 100) / 100,
      toolStats,
      ratingDistribution,
      topTags,
      recentActivity
    };
  }

  async exportToCSV(): Promise<string> {
    const experiments = await this.listExperiments();

    // CSV header
    let csv = 'ID,Date,AI Tool,Prompt,Result,Rating,Tags,Created At,Updated At\n';

    // Quote every textual column, including dates/tags, and neutralize common
    // spreadsheet formula prefixes. This is data export, never executable input.
    const textCell = (value: string) => {
      const safe = /^\s*[=+\-@]/u.test(value) ? "'" + value : value;
      return `"${safe.replace(/"/g, '""')}"`;
    };
    experiments.forEach(exp => {
      const row = [
        textCell(exp.id), textCell(exp.date), textCell(exp.aiTool),
        textCell(exp.prompt), textCell(exp.result), exp.rating,
        textCell(exp.tags.join(', ')), textCell(exp.createdAt), textCell(exp.updatedAt)
      ].join(',');
      csv += row + '\n';
    });

    return csv;
  }

  getDataFilePath(): string {
    return DATA_FILE;
  }
}
