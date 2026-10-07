/**
 * Resolve relative links in repository markdown (SKILL.md bodies, plugin
 * README sections) to targets that exist once the markdown is rendered on a
 * tonsofskills.com page.
 *
 * Why: a SKILL.md link such as `references/foo.md` is relative to the
 * SKILL.md file in the repository. Rendered verbatim into /skills/<slug>/ it
 * resolves against the page URL instead, producing /skills/<slug>/references/
 * foo.md (or /skills/references/foo.md when the page is requested without its
 * trailing slash). Neither was ever a page, so every such link was a 404.
 *
 * Reference files have no rendered page on the site, so a relative link is
 * rewritten to the file's source on GitHub — the same pattern the site
 * already uses for repository documents (learning guides, grading page,
 * contributing guide all link `github.com/.../blob/main/<path>`).
 *
 * The resolver fails closed: a target that escapes the repository or does
 * not exist in the tracked tree yields null, and the renderer emits the
 * link label as plain text instead of a dead link.
 */

import * as posix from 'node:path/posix';

export const SOURCE_REPOSITORY_URL = 'https://github.com/jeremylongshore/tons-of-skills-marketplace';
export const SOURCE_BRANCH = 'main';

const ABSOLUTE_URI = /^[a-z][a-z\d+.-]*:/i;

// Claude Code expands these placeholders at runtime; on the page they mean
// "this skill's directory" / "this plugin's root".
const SKILL_DIR_PLACEHOLDER = /^\$\{CLAUDE_SKILL_DIR\}\/?/;
const PLUGIN_ROOT_PLACEHOLDER = /^\$\{CLAUDE_PLUGIN_ROOT\}\/?/;

/** True when the target is not a repository-relative path. */
export function isNonRelativeTarget(target) {
  return (
    target.startsWith('/') ||
    target.startsWith('#') ||
    target.startsWith('?') ||
    ABSOLUTE_URI.test(target)
  );
}

function encodePath(path) {
  return path
    .split('/')
    .map((segment) => encodeURIComponent(segment))
    .join('/');
}

/**
 * Build a set-backed `kindOf` lookup from a list of tracked repository paths
 * (e.g. `git ls-files`). Directories are derived from file prefixes.
 */
export function createTrackedTreeLookup(trackedPaths) {
  const files = new Set();
  const directories = new Set();
  for (const entry of trackedPaths) {
    files.add(entry);
    let slash = entry.lastIndexOf('/');
    while (slash > 0) {
      const directory = entry.slice(0, slash);
      if (directories.has(directory)) break;
      directories.add(directory);
      slash = directory.lastIndexOf('/');
    }
  }
  return (path) => (files.has(path) ? 'file' : directories.has(path) ? 'directory' : null);
}

/**
 * Create a resolver for links written in one repository markdown file.
 *
 * @param {object} options
 * @param {string} options.sourcePath  repository-relative path of the markdown
 *   file (POSIX separators), e.g. `plugins/x/y/skills/z/SKILL.md`.
 * @param {(path: string) => 'file' | 'directory' | null} options.kindOf
 *   reports whether a repository-relative path exists in the tracked tree.
 * @param {string} [options.pluginRoot]  repository-relative plugin directory,
 *   used for `${CLAUDE_PLUGIN_ROOT}` targets.
 * @returns {(target: string) => string | null}  the rewritten href, the
 *   original target when it is not relative, or null when it cannot resolve.
 */
export function createRelativeLinkResolver({ sourcePath, kindOf, pluginRoot }) {
  if (typeof sourcePath !== 'string' || sourcePath.length === 0) {
    throw new TypeError('createRelativeLinkResolver: sourcePath is required');
  }
  if (typeof kindOf !== 'function') {
    throw new TypeError('createRelativeLinkResolver: kindOf is required');
  }
  const sourceDirectory = posix.dirname(sourcePath);

  return (target) => {
    let base = sourceDirectory;
    let relativeTarget = target;
    if (SKILL_DIR_PLACEHOLDER.test(relativeTarget)) {
      relativeTarget = relativeTarget.replace(SKILL_DIR_PLACEHOLDER, '');
    } else if (PLUGIN_ROOT_PLACEHOLDER.test(relativeTarget)) {
      if (!pluginRoot) return null;
      base = pluginRoot;
      relativeTarget = relativeTarget.replace(PLUGIN_ROOT_PLACEHOLDER, '');
    } else if (isNonRelativeTarget(relativeTarget)) {
      return target;
    }

    const fragmentIndex = relativeTarget.indexOf('#');
    const fragment = fragmentIndex === -1 ? '' : relativeTarget.slice(fragmentIndex);
    const beforeFragment =
      fragmentIndex === -1 ? relativeTarget : relativeTarget.slice(0, fragmentIndex);
    const queryIndex = beforeFragment.indexOf('?');
    const pathPart = queryIndex === -1 ? beforeFragment : beforeFragment.slice(0, queryIndex);
    if (!pathPart) return null;

    let decoded;
    try {
      decoded = decodeURIComponent(pathPart);
    } catch {
      return null;
    }
    if (decoded.includes('\\') || /[\u0000-\u001f\u007f]/.test(decoded)) return null;

    const resolved = posix.normalize(posix.join(base, decoded)).replace(/\/+$/, '');
    if (!resolved || resolved === '.' || resolved === '..' || resolved.startsWith('../')) {
      return null;
    }

    const kind = kindOf(resolved);
    if (kind === null) return null;
    const view = kind === 'directory' ? 'tree' : 'blob';
    // Query strings mean nothing to a GitHub source view; anchors still work.
    return `${SOURCE_REPOSITORY_URL}/${view}/${SOURCE_BRANCH}/${encodePath(resolved)}${fragment}`;
  };
}
