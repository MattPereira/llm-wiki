// Frontmatter dates are date-only, so format in UTC or they render a day early
// west of Greenwich.
export const formatDate = (date: Date): string =>
  date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    timeZone: "UTC",
  });

export const permalink = (id: string): string => `/${id}/`;

export const sourceLabel = (url: string): string =>
  url.includes("youtube.com") || url.includes("youtu.be")
    ? "Watch the original"
    : "Read the original";
