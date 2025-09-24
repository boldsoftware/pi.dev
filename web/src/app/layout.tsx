import { GoogleTagManager } from "@next/third-parties/google";
import type { Metadata } from "next";
import PlausibleProvider from "next-plausible";
import { Geist, Geist_Mono } from "next/font/google";
import { getMetadata } from "./getMetadata";
import "./globals.css";
import { DESCRIPTION, SHARE_TITLE } from "./stringAssets";

const GOOGLE_TAG_MANAGER_ID =
  process.env.NEXT_PUBLIC_GOOGLE_TAG_MANAGER_ID ??
  "GOOGLE_TAG_MANAGER_ID_PLACEHOLDER";

const PLAUSIBLE_DOMAIN =
  process.env.NEXT_PUBLIC_PLAUSIBLE_DOMAIN ?? "PI_DEV_WEB_HOST";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = getMetadata(SHARE_TITLE, DESCRIPTION);

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <meta
          name="format-detection"
          content="telephone=no, date=no, email=no, address=no"
        />
      </head>
      <GoogleTagManager gtmId={GOOGLE_TAG_MANAGER_ID} />
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <PlausibleProvider domain={PLAUSIBLE_DOMAIN}>
          {children}
        </PlausibleProvider>
      </body>
    </html>
  );
}
