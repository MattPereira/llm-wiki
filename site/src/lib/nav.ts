/**
 * Which nav item the current URL belongs under, as its href, or undefined for a
 * page that sits in no section. Permalinks mirror the file tree, so a Creator
 * page is the only single-segment path that is not one of the site's own indexes.
 */
export function activeNav(pathname: string): string | undefined {
  const segments = pathname.split("/").filter(Boolean);
  if (segments.length === 0) return "/";

  switch (segments[0]) {
    case "creators":
      return "/creators/";
    case "topics":
      return "/topics/";
    case "search":
      return "/search/";
    default:
      // /<creator>/ is a Creator; /<creator>/<slug>/ is a Summary, which is a leaf.
      return segments.length === 1 ? "/creators/" : undefined;
  }
}
