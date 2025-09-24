import Link from "next/link";

interface Params {
  repo?: string;
  episode?: string;
}

export function Feedback({ repo, episode }: Params) {
  return (
    <p className="text-lg text-gray-700 mb-4">
      We would love{" "}
      <Link
        href={{ pathname: "/feedback", query: { repo, episode } }}
        target="_blank"
        rel="noopener noreferrer"
        className="text-blue-600 underline"
        prefetch={false}
      >
        your feedback
      </Link>
      !
    </p>
  );
}
