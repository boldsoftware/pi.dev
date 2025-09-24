import { redirect } from "next/navigation";
import { type NextRequest } from "next/server";

const REPO_KEY = "entry.700542346";
const EPISODE_KEY = "entry.1815165153";

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const repo = searchParams.get("repo");
  const episode = searchParams.get("episode");

  if (repo == null && episode == null) {
    return redirect("https://forms.gle/PbvmintKfSSU2Vsw6");
  }

  const query = new URLSearchParams();

  if (repo != null) {
    query.set(REPO_KEY, repo);
  }
  if (episode != null) {
    query.set(EPISODE_KEY, episode);
  }

  redirect(
    `https://docs.google.com/forms/d/e/1FAIpQLSdY2PP7NAbD4v-1EOX0qKWlSJ1kk0aRS9bUv6B9Jj9cfYeirA/viewform?usp=pp_url&${query}`,
  );
}
