"use client";
import { sendGTMEvent } from "@next/third-parties/google";

const GOOGLE_ADS_CONVERSION_TARGET =
  process.env.NEXT_PUBLIC_GOOGLE_ADS_CONVERSION_TARGET ??
  "GOOGLE_ADS_CONVERSION_TARGET_PLACEHOLDER";

export function gtmReportConversion() {
  sendGTMEvent([
    "event",
    "conversion",
    {
      send_to: GOOGLE_ADS_CONVERSION_TARGET,
      value: 1.0,
      currency: "USD",
    },
  ]);
}
