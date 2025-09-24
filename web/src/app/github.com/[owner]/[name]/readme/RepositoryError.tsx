import RequestRepoForm from "@/components/RequestRepoForm";

interface Props {
  repo: string;
}

export function RepositoryError({ repo }: Props) {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-100 p-4">
      <h1 className="text-3xl font-bold text-center text-red-500 mb-6">
        Error
      </h1>
      <p className="text-lg text-center text-gray-700 mb-8">
        There was an error generating the podcast feed for {repo}.
      </p>
      <p className="text-lg text-center text-gray-600 mb-2 max-w-lg">
        Try again?
      </p>
      <RequestRepoForm initialText={repo} autoSelect={true} />
    </main>
  );
}
