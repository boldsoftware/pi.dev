"use client";

import { parseGithubUrl } from "../parseGithubUrl";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { gtmReportConversion } from "./gtmReportConversion";

interface Params {
  initialText?: string;
  autoSelect?: boolean;
}

export default function RequestRepoForm({ initialText, autoSelect }: Params) {
  const [githubUrl, setGithubUrl] = useState(initialText ?? "");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  useEffect(() => {
    if (autoSelect) {
      inputRef.current?.select();
    }
  }, [autoSelect]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setGithubUrl(e.target.value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage(null);

    try {
      const { owner, name } = parseGithubUrl(githubUrl);
      gtmReportConversion();
      router.push(`/github.com/${owner}/${name}/readme`);
    } catch (_error) {
      setErrorMessage(
        "Invalid URL format or repository could not be verified. Please try again.",
      );
      setLoading(false);
    }
  };

  return (
    <div>
      <form
        onSubmit={handleSubmit}
        className="flex w-full max-w-md flex-col sm:flex-row items-center gap-4 mb-7"
      >
        <input
          ref={inputRef}
          autoCapitalize="none"
          autoCorrect="off"
          autoFocus={autoSelect}
          spellCheck="false"
          value={githubUrl}
          onChange={handleInputChange}
          placeholder="Paste GitHub Repo URL here"
          className="flex-1 w-full rounded-lg border border-gray-300 p-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
        {loading ? (
          <div className="rounded-lg bg-gray-400 px-6 py-3 text-white font-medium">
            Loading...
          </div>
        ) : (
          <button
            type="submit"
            className="rounded-lg bg-blue-600 px-6 py-3 text-white font-medium hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Generate Podcast
          </button>
        )}
      </form>
      {errorMessage && (
        <p className="text-red-500 mb-4 text-center">{errorMessage}</p>
      )}
    </div>
  );
}
