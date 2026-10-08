import { describe, it, expect, vi, beforeEach } from 'vitest';
import { GitHubClient } from '../src/github-client.js';

// Mock Octokit
vi.mock('@octokit/rest', () => {
  return {
    // Vitest 4: a mock invoked with `new` needs a constructible implementation.
    Octokit: vi.fn().mockImplementation(function () {
      return {
        issues: {
          create: vi.fn(),
        },
        repos: {
          get: vi.fn(),
        },
      };
    }),
  };
});

describe('GitHubClient', () => {
  let client;
  let mockOctokit;

  beforeEach(async () => {
    vi.clearAllMocks();
    const { Octokit } = await import('@octokit/rest');
    client = new GitHubClient('test-token');
    mockOctokit = client.octokit;
  });

  describe('constructor', () => {
    it('should throw error when token is missing', () => {
      expect(() => new GitHubClient()).toThrow(
        'GitHub token required. Set GITHUB_TOKEN environment variable.'
      );
    });

    it('should throw error when token is empty string', () => {
      expect(() => new GitHubClient('')).toThrow(
        'GitHub token required. Set GITHUB_TOKEN environment variable.'
      );
    });

    it('should throw error when token is null', () => {
      expect(() => new GitHubClient(null)).toThrow(
        'GitHub token required. Set GITHUB_TOKEN environment variable.'
      );
    });

    it('should create instance with valid token', () => {
      const validClient = new GitHubClient('valid-token');
      expect(validClient).toBeInstanceOf(GitHubClient);
      expect(validClient.octokit).toBeDefined();
    });
  });

  describe('createIssue', () => {
    const validIssueData = {
      title: 'Test Issue',
      body: 'Issue body content',
      labels: ['research', 'enhancement'],
      assignees: ['testuser'],
    };

    it('should create issue with valid repo format', async () => {
      const mockResponse = {
        data: {
          id: 1,
          number: 42,
          title: 'Test Issue',
          html_url: 'https://github.com/owner/repo/issues/42',
        },
      };

      mockOctokit.issues.create.mockResolvedValue(mockResponse);

      const result = await client.createIssue('owner/repo', validIssueData);

      expect(mockOctokit.issues.create).toHaveBeenCalledWith({
        owner: 'owner',
        repo: 'repo',
        title: validIssueData.title,
        body: validIssueData.body,
        labels: validIssueData.labels,
        assignees: validIssueData.assignees,
      });

      expect(result).toEqual(mockResponse.data);
    });

    it('should throw error for invalid repo format (no slash)', async () => {
      await expect(
        client.createIssue('invalidrepo', validIssueData)
      ).rejects.toThrow('Invalid repo format: invalidrepo. Must be owner/repo with valid GitHub characters');
    });

    it('should throw error for invalid repo format (missing owner)', async () => {
      await expect(
        client.createIssue('/repo', validIssueData)
      ).rejects.toThrow('Invalid repo format: /repo. Must be owner/repo with valid GitHub characters');
    });

    it('should throw error for invalid repo format (missing repo)', async () => {
      await expect(
        client.createIssue('owner/', validIssueData)
      ).rejects.toThrow('Invalid repo format: owner/. Must be owner/repo with valid GitHub characters');
    });

    it('should throw error for empty repo string', async () => {
      await expect(
        client.createIssue('', validIssueData)
      ).rejects.toThrow('Invalid repo format: . Must be owner/repo with valid GitHub characters');
    });

    it('should handle API errors gracefully', async () => {
      mockOctokit.issues.create.mockRejectedValue(
        new Error('API rate limit exceeded')
      );

      await expect(
        client.createIssue('owner/repo', validIssueData)
      ).rejects.toThrow('Failed to create issue: API rate limit exceeded');
    });

    it('should handle network errors', async () => {
      mockOctokit.issues.create.mockRejectedValue(
        new Error('Network error: ECONNREFUSED')
      );

      await expect(
        client.createIssue('owner/repo', validIssueData)
      ).rejects.toThrow('Failed to create issue: Network error: ECONNREFUSED');
    });

    it('should create issue with empty labels array when not provided', async () => {
      const mockResponse = { data: { id: 1, number: 42 } };
      mockOctokit.issues.create.mockResolvedValue(mockResponse);

      const dataWithoutLabels = {
        title: 'Test',
        body: 'Body',
      };

      await client.createIssue('owner/repo', dataWithoutLabels);

      expect(mockOctokit.issues.create).toHaveBeenCalledWith({
        owner: 'owner',
        repo: 'repo',
        title: dataWithoutLabels.title,
        body: dataWithoutLabels.body,
        labels: [],
        assignees: [],
      });
    });

    it('should handle authentication errors', async () => {
      mockOctokit.issues.create.mockRejectedValue(
        new Error('Bad credentials')
      );

      await expect(
        client.createIssue('owner/repo', validIssueData)
      ).rejects.toThrow('Failed to create issue: Bad credentials');
    });

    it('should handle permission errors', async () => {
      mockOctokit.issues.create.mockRejectedValue(
        new Error('Resource not accessible by integration')
      );

      await expect(
        client.createIssue('owner/repo', validIssueData)
      ).rejects.toThrow(
        'Failed to create issue: Resource not accessible by integration'
      );
    });

    it('should handle repo not found errors', async () => {
      mockOctokit.issues.create.mockRejectedValue(new Error('Not Found'));

      await expect(
        client.createIssue('owner/nonexistent', validIssueData)
      ).rejects.toThrow('Failed to create issue: Not Found');
    });
  });

  describe('verifyRepo', () => {
    it('should return success for valid repo', async () => {
      const mockResponse = {
        data: {
          full_name: 'owner/repo',
          has_issues: true,
        },
      };

      mockOctokit.repos.get.mockResolvedValue(mockResponse);

      const result = await client.verifyRepo('owner/repo');

      expect(mockOctokit.repos.get).toHaveBeenCalledWith({
        owner: 'owner',
        repo: 'repo',
      });

      expect(result).toEqual({
        exists: true,
        fullName: 'owner/repo',
        hasIssues: true,
      });
    });

    it('should return false for non-existent repo', async () => {
      mockOctokit.repos.get.mockRejectedValue(new Error('Not Found'));

      const result = await client.verifyRepo('owner/nonexistent');

      expect(result).toEqual({
        exists: false,
        error: 'Not Found',
      });
    });

    it('should return false for repo without issues enabled', async () => {
      const mockResponse = {
        data: {
          full_name: 'owner/repo',
          has_issues: false,
        },
      };

      mockOctokit.repos.get.mockResolvedValue(mockResponse);

      const result = await client.verifyRepo('owner/repo');

      expect(result).toEqual({
        exists: true,
        fullName: 'owner/repo',
        hasIssues: false,
      });
    });

    it('should handle authentication errors gracefully', async () => {
      mockOctokit.repos.get.mockRejectedValue(new Error('Bad credentials'));

      const result = await client.verifyRepo('owner/repo');

      expect(result).toEqual({
        exists: false,
        error: 'Bad credentials',
      });
    });

    it('should handle network errors gracefully', async () => {
      mockOctokit.repos.get.mockRejectedValue(
        new Error('Network error: timeout')
      );

      const result = await client.verifyRepo('owner/repo');

      expect(result).toEqual({
        exists: false,
        error: 'Network error: timeout',
      });
    });

    it('should handle private repo access denied', async () => {
      mockOctokit.repos.get.mockRejectedValue(
        new Error('Resource not accessible')
      );

      const result = await client.verifyRepo('owner/private-repo');

      expect(result).toEqual({
        exists: false,
        error: 'Resource not accessible',
      });
    });

    it('should split repo name correctly with hyphens', async () => {
      const mockResponse = {
        data: {
          full_name: 'my-org/my-repo-name',
          has_issues: true,
        },
      };

      mockOctokit.repos.get.mockResolvedValue(mockResponse);

      await client.verifyRepo('my-org/my-repo-name');

      expect(mockOctokit.repos.get).toHaveBeenCalledWith({
        owner: 'my-org',
        repo: 'my-repo-name',
      });
    });

    it('should split repo name correctly with underscores', async () => {
      const mockResponse = {
        data: {
          full_name: 'my_org/my_repo',
          has_issues: true,
        },
      };

      mockOctokit.repos.get.mockResolvedValue(mockResponse);

      await client.verifyRepo('my_org/my_repo');

      expect(mockOctokit.repos.get).toHaveBeenCalledWith({
        owner: 'my_org',
        repo: 'my_repo',
      });
    });
  });
});
