import { Metadata } from "next";

const WEB_HOST = process.env.NEXT_PUBLIC_WEB_HOST ?? "PI_DEV_WEB_HOST";

const SOCIAL_LOGO = {
  url: `https://${WEB_HOST}/logo.webp`,
  width: 1024,
  height: 1024,
  alt: WEB_HOST,
};

export function getMetadata(title: string, description: string): Metadata {
  return {
    title,
    description,
    openGraph: {
      title,
      description,
      images: SOCIAL_LOGO,
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: SOCIAL_LOGO,
    },
  };
}
