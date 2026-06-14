import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

// Point at the request config so next-intl can find locale + messages.
const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

const nextConfig: NextConfig = {
  reactStrictMode: true,
};

export default withNextIntl(nextConfig);
