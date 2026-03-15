import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  async rewrites() {
    return [
      {
        source: "/api/v1/auth/:path*",
        destination: "http://localhost:8001/api/v1/auth/:path*",
      },
      {
        source: "/api/v1/users/:path*",
        destination: "http://localhost:8001/api/v1/users/:path*",
      },
      {
        source: "/api/v1/invitations/:path*",
        destination: "http://localhost:8001/api/v1/invitations/:path*",
      },
      {
        source: "/api/v1/checklists/:path*",
        destination: "http://localhost:8002/api/v1/checklists/:path*",
      },
      {
        source: "/api/v1/knowledge/:path*",
        destination: "http://localhost:8003/api/v1/knowledge/:path*",
      },
      {
        source: "/api/v1/notification/:path*",
        destination: "http://localhost:8004/api/v1/notification/:path*",
      },
      {
        source: "/api/v1/escalation/:path*",
        destination: "http://localhost:8005/api/v1/escalation/:path*",
      },
      {
        source: "/api/v1/meeting/:path*",
        destination: "http://localhost:8006/api/v1/meeting/:path*",
      },
      {
        source: "/api/v1/feedback/:path*",
        destination: "http://localhost:8007/api/v1/feedback/:path*",
      },
    ];
  },
};

export default nextConfig;
