"use client";

import { useIsIos } from "@/hooks/useIsIos";
import { QRCodeCanvas } from "qrcode.react";

interface Params {
  feedUrl: string;
}

export function OpenInApplePodcasts({ feedUrl }: Params) {
  const isIOS = useIsIos();
  return isIOS ? (
    <p className="text-lg mb-4 text-gray-700">
      <a
        href={getApplePodcastsURL(feedUrl)}
        className="text-blue-600 underline"
        target="_blank"
        rel="noopener noreferrer"
      >
        Open in Apple Podcasts
      </a>
    </p>
  ) : (
    <div className="flex flex-col items-center mb-4 mt-4">
      <QRCodeCanvas value={getApplePodcastsURL(feedUrl)} size={200} />
      <p className="text-lg mt-1  text-gray-700">Open in Apple Podcasts</p>
    </div>
  );
}

function getApplePodcastsURL(url: string) {
  return url.replace(/^https?/, "podcast");
}
