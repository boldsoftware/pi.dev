import { getMetadata } from "@/app/getMetadata";
import { CopyButton } from "@/components/CopyButton";
import { Feedback } from "@/components/Feedback";
import { OpenInApplePodcasts } from "@/components/OpenInApplePodcasts";
import RequestRepoForm from "@/components/RequestRepoForm";
import { requestRepo } from "@/requestRepo";
import Image from "next/image";
import { redirect } from "next/navigation";
import { RepositoryError } from "./RepositoryError";

const WEB_HOST = process.env.NEXT_PUBLIC_WEB_HOST ?? "PI_DEV_WEB_HOST";

interface Params {
  owner: string;
  name: string;
}

export async function generateMetadata({
  params,
}: {
  params: Promise<Params>;
}) {
  const { owner, name } = await params;
  const title = `${owner}/${name} by ${WEB_HOST}`;
  return getMetadata(
    title,
    `An AI-generated podcast keeping you up-to-date on the latest changes in the ${owner}/${name} repository.`,
  );
}

export default async function RepositoryPage({
  params,
}: {
  params: Promise<Params>;
}) {
  const { owner, name } = await params;
  const repo = `${owner}/${name}`;

  const response = await requestRepo(owner, name);

  if (!response.ok) {
    return <RepositoryError repo={repo} />;
  }

  const payload = await response.json();

  if (payload.status == "REDIRECT") {
    const { owner, name } = payload;
    return redirect(`/github.com/${owner}/${name}/readme`);
  }

  const feedUrl = `https://${WEB_HOST}/github.com/${owner}/${name}/feed.rss`;

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-100 p-4">
      <div className="mb-8">
        <Image
          className="rounded-md"
          src="/logo.webp"
          alt="Logo"
          width={200}
          height={200}
        />
      </div>

      <h1 className="text-3xl font-bold text-center text-gray-800 mb-6">
        {repo} by {WEB_HOST}
      </h1>

      <div className="flex flex-col items-center text-center">
        <p className="text-lg mb-4 text-gray-700 max-w-prose">
          An AI-generated podcast keeping you up-to-date on the latest changes
          in the{" "}
          <a
            href={`https://github.com/${owner}/${name}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 underline"
          >
            {repo}
          </a>{" "}
          repository.
        </p>
        <div className="flex items-center justify-center mb-4 text-gray-700 break-all flex-wrap">
          <span className="text-2xl">{feedUrl}</span>
          <CopyButton text={feedUrl} name="RSS feed URL" />
        </div>
        <OpenInApplePodcasts feedUrl={feedUrl} />
        <p className=" text-gray-600 mb-4">
          Or for instructions on adding to your favorite podcast app, visit{" "}
          <a
            href="https://transistor.fm/add-podcast/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 underline"
          >
            Transistor.fm
          </a>
        </p>
      </div>

      <div className="flex flex-col items-center">
        <Feedback repo={repo} />
      </div>

      <p className="text-lg text-center text-gray-600 mb-2 max-w-lg">
        Want to generate podcasts for more repositories?
      </p>
      <RequestRepoForm />
    </main>
  );
}
