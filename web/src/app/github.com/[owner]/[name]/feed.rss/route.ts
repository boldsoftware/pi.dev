import { requestRepo } from "../../../../../requestRepo";

const PUBLIC_BUCKET_NAME = "PI_DEV_PUBLIC_BUCKET";
const STORAGE_BASE_URL = `https://storage.googleapis.com/${PUBLIC_BUCKET_NAME}`;

interface Params {
  owner: string;
  name: string;
}

export async function GET(
  _request: Request,
  { params }: { params: Promise<Params> },
) {
  const { owner, name } = await params;

  // First just try to send them the podcast feed
  const url = `${STORAGE_BASE_URL}/shows/github.com%252F${owner}%252F${name}/podcast.rss`;
  let response = await fetch(url);

  if (response.ok) {
    return response;
  }

  // If the podcast feed doesn't exist, then try to create it
  response = await requestRepo(owner, name);

  // If it was a bad repo, then return the error
  if (!response.ok) {
    return response;
  }

  // If the feed was created, then forward the podcast feed
  response = await fetch(url);

  return response;
}
