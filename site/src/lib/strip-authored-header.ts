import { defineMdastPlugin } from "satteri";
import type { RootContent } from "mdast";

/**
 * Summaries repeat their title and a `Creator · date · duration · link` byline in
 * the body so they read standalone in Obsidian. The Site renders both from
 * validated frontmatter instead, so drop the authored copies rather than show
 * every summary's header twice.
 */
const isByline = (node: RootContent): boolean =>
  node.type === "paragraph" &&
  node.children.some((child) => child.type === "strong") &&
  node.children.some(
    (child) => child.type === "text" && child.value.includes("·"),
  );

export const stripAuthoredHeader = defineMdastPlugin({
  name: "strip-authored-header",
  before(root, ctx) {
    const [first, second] = root.children;
    if (first?.type !== "heading" || first.depth !== 1) return;

    ctx.removeNode(first);
    if (second && isByline(second)) ctx.removeNode(second);
  },
});
