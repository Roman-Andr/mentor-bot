import { NextRequest, NextResponse } from "next/server";

const SERVICE_MAP: Record<string, string> = {
  auth: process.env.AUTH_SERVICE_URL || "http://localhost:8001",
  users: process.env.AUTH_SERVICE_URL || "http://localhost:8001",
  invitations: process.env.AUTH_SERVICE_URL || "http://localhost:8001",
  departments: process.env.AUTH_SERVICE_URL || "http://localhost:8001",
  "user-mentors": process.env.AUTH_SERVICE_URL || "http://localhost:8001",
  checklists: process.env.CHECKLISTS_SERVICE_URL || "http://localhost:8002",
  templates: process.env.CHECKLISTS_SERVICE_URL || "http://localhost:8002",
  tasks: process.env.CHECKLISTS_SERVICE_URL || "http://localhost:8002",
  "dialogue-scenarios": process.env.KNOWLEDGE_SERVICE_URL || "http://localhost:8003",
  "dialogue-scenarios/active": process.env.KNOWLEDGE_SERVICE_URL || "http://localhost:8003",
  articles: process.env.KNOWLEDGE_SERVICE_URL || "http://localhost:8003",
  categories: process.env.KNOWLEDGE_SERVICE_URL || "http://localhost:8003",
  tags: process.env.KNOWLEDGE_SERVICE_URL || "http://localhost:8003",
  search: process.env.KNOWLEDGE_SERVICE_URL || "http://localhost:8003",
  attachments: process.env.KNOWLEDGE_SERVICE_URL || "http://localhost:8003",
  notifications: process.env.NOTIFICATION_SERVICE_URL || "http://localhost:8004",
  escalations: process.env.ESCALATION_SERVICE_URL || "http://localhost:8005",
  meetings: process.env.MEETING_SERVICE_URL || "http://localhost:8006",
  "user-meetings": process.env.MEETING_SERVICE_URL || "http://localhost:8006",
  calendar: process.env.MEETING_SERVICE_URL || "http://localhost:8006",
  feedback: process.env.FEEDBACK_SERVICE_URL || "http://localhost:8007",
};

const HOP_BY_HOP_HEADERS = new Set([
  "connection",
  "keep-alive",
  "transfer-encoding",
  "host",
  "content-length",
  "te",
  "trailer",
  "upgrade",
]);

function buildTargetUrl(
  pathSegments: string[],
  search: string,
): { url: URL; error?: undefined } | { url?: undefined; error: NextResponse } {
  if (pathSegments.length < 2 || pathSegments[0] !== "v1") {
    return { error: NextResponse.json({ error: "Not found" }, { status: 404 }) };
  }

  const serviceKey = pathSegments[1];
  const serviceUrl = SERVICE_MAP[serviceKey];

  if (!serviceUrl) {
    return { error: NextResponse.json({ error: "Unknown service" }, { status: 404 }) };
  }

  const targetPath = "/api/" + pathSegments.join("/");
  const url = new URL(targetPath, serviceUrl);
  url.search = search;

  return { url };
}

function rewriteLocation(location: string, targetUrl: URL, requestUrl: string): string {
  const redirectUrl = new URL(location, targetUrl);

  const isInternalHost = Object.values(SERVICE_MAP).some(
    (svcUrl) => redirectUrl.origin === new URL(svcUrl).origin,
  );

  if (isInternalHost) {
    return redirectUrl.pathname + redirectUrl.search;
  }

  if (redirectUrl.origin === new URL(requestUrl).origin) {
    return redirectUrl.pathname + redirectUrl.search;
  }

  return redirectUrl.toString();
}

async function proxyRequest(request: NextRequest, pathSegments: string[]): Promise<NextResponse> {
  const result = buildTargetUrl(pathSegments, request.nextUrl.search);
  if (result.error) return result.error;

  const targetUrl = result.url;

  const headers = new Headers();
  request.headers.forEach((value, key) => {
    if (!HOP_BY_HOP_HEADERS.has(key.toLowerCase())) {
      headers.set(key, value);
    }
  });

  const hasBody = request.method !== "GET" && request.method !== "HEAD";
  const body = hasBody ? await request.arrayBuffer() : undefined;

  let fetchResponse: Response;
  try {
    fetchResponse = await fetch(targetUrl.toString(), {
      method: request.method,
      headers,
      body,
      redirect: "manual",
    });
  } catch {
    return NextResponse.json({ error: "Service unavailable" }, { status: 502 });
  }

  if (fetchResponse.status >= 300 && fetchResponse.status < 400) {
    const location = fetchResponse.headers.get("location");
    if (location) {
      const rewritten = rewriteLocation(location, targetUrl, request.url);
      return NextResponse.redirect(new URL(rewritten, request.url), fetchResponse.status);
    }
  }

  const responseHeaders = new Headers();
  fetchResponse.headers.forEach((value, key) => {
    const lowerKey = key.toLowerCase();
    if (!HOP_BY_HOP_HEADERS.has(lowerKey) && lowerKey !== "content-encoding") {
      responseHeaders.set(key, value);
    }
  });

  return new NextResponse(fetchResponse.body, {
    status: fetchResponse.status,
    headers: responseHeaders,
  });
}

type RouteParams = { params: Promise<{ path: string[] }> };

export async function GET(request: NextRequest, { params }: RouteParams) {
  const { path } = await params;
  return proxyRequest(request, path);
}

export async function POST(request: NextRequest, { params }: RouteParams) {
  const { path } = await params;
  return proxyRequest(request, path);
}

export async function PUT(request: NextRequest, { params }: RouteParams) {
  const { path } = await params;
  return proxyRequest(request, path);
}

export async function DELETE(request: NextRequest, { params }: RouteParams) {
  const { path } = await params;
  return proxyRequest(request, path);
}

export async function PATCH(request: NextRequest, { params }: RouteParams) {
  const { path } = await params;
  return proxyRequest(request, path);
}
