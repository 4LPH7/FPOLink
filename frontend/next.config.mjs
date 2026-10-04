/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Netlify's Next.js adapter manages its own runtime output. Standalone is
  // enabled only for the Docker image, which copies .next/standalone.
  ...(process.env.NEXT_OUTPUT_STANDALONE === "true" ? { output: "standalone" } : {}),
  async rewrites() {
    const isNetlifyBuild = process.env.NETLIFY === "true";
    const apiInternalUrl = process.env.API_INTERNAL_URL?.trim();
    if (isNetlifyBuild) {
      if (!apiInternalUrl) {
        throw new Error("Set API_INTERNAL_URL to the HTTPS origin of the FPOLink API in Netlify.");
      }
      if (process.env.NEXT_PUBLIC_API_URL?.trim()) {
        throw new Error("Unset NEXT_PUBLIC_API_URL on Netlify; use the same-origin API proxy via API_INTERNAL_URL.");
      }
      let parsedApiUrl;
      try {
        parsedApiUrl = new URL(apiInternalUrl);
      } catch {
        throw new Error("API_INTERNAL_URL must be an absolute HTTPS origin for Netlify builds.");
      }
      if (parsedApiUrl.protocol !== "https:") {
        throw new Error("API_INTERNAL_URL must use HTTPS for Netlify builds.");
      }
    }

    return [
      {
        source: "/api/:path*",
        destination: `${(apiInternalUrl || "http://localhost:8000").replace(/\/+$/, "")}/api/:path*`,
      },
    ];
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
