export function parseGithubUrl(githubUrl: string) {
  try {
    const url = new URL(githubUrl);
    const pathSegments = url.pathname.split("/").filter(Boolean);
    if (
      pathSegments.length < 2 ||
      url.hostname !== "github.com" ||
      (url.protocol !== "https:" && url.protocol !== "http:")
    ) {
      throw new Error("Invalid GitHub URL format");
    }
    return { owner: pathSegments[0], name: pathSegments[1] };
  } catch (_err) {
    // Try to handle case where input is just "owner/repo"
    const pathSegments = githubUrl.split("/").filter(Boolean);
    if (pathSegments.length !== 2) {
      throw new Error("Invalid GitHub URL format");
    }
    return { owner: pathSegments[0], name: pathSegments[1] };
  }
}
