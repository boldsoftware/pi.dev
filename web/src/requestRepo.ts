import { isProd } from "@/env";
import { env } from "process";

export async function requestRepo(owner: string, name: string) {
  const url = `${PODCAST_GENERATOR_SERVICE_URL}/request/github.com/${owner}/${name}`;

  return await fetch(url, {
    method: "POST",
  });
}

const PODCAST_GENERATOR_SERVICE_URL = isProd()
  ? env.PODCAST_GENERATOR_SERVICE_URL
  : "http://127.0.0.1:5000";
