export type SkillFrontmatterValue =
  | string
  | null
  | SkillFrontmatterValue[]
  | { [key: string]: SkillFrontmatterValue };

export function parseSkillFrontmatter(
  content: string,
): Record<string, SkillFrontmatterValue> | null;
