"use client";

import { ClipboardIcon } from "@/components/ClipboardIcon";

interface Params {
  text: string;
  name: string;
}

export function CopyButton({ text, name }: Params) {
  const handleCopy = () => {
    navigator.clipboard.writeText(text);
  };

  return (
    <button
      onClick={handleCopy}
      className="rounded p-1 text-blue-600 hover:bg-gray-300 active:bg-gray-400"
      title={`Copy ${name}`}
    >
      <ClipboardIcon />
    </button>
  );
}
