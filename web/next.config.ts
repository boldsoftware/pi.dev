import type { NextConfig } from "next";
import { withPlausibleProxy } from "next-plausible";

const nextConfig: NextConfig = withPlausibleProxy()({
  output: "standalone",

  async redirects() {
    return [
      {
        source: "/github.com/:owner/:name",
        destination: "/github.com/:owner/:name/feed.rss",
        permanent: true,
      },
    ];
  },
});

export default nextConfig;
