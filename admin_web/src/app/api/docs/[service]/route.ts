import { NextRequest, NextResponse } from "next/server";

const serviceUrls: Record<string, string> = {
  auth: "http://auth_service:8001/openapi.json",
  checklists: "http://checklists_service:8002/openapi.json",
  knowledge: "http://knowledge_service:8003/openapi.json",
  notification: "http://notification_service:8004/openapi.json",
  escalation: "http://escalation_service:8005/openapi.json",
  meeting: "http://meeting_service:8006/openapi.json",
  feedback: "http://feedback_service:8007/openapi.json",
};

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ service: string }> }
) {
  const { service } = await params;
  const url = serviceUrls[service];

  if (!url) {
    return NextResponse.json({ error: "Unknown service" }, { status: 404 });
  }

  try {
    const authHeader = request.headers.get("authorization");

    const response = await fetch(url, {
      headers: authHeader ? { Authorization: authHeader } : {},
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: "Failed to fetch spec" },
        { status: response.status }
      );
    }

    const spec = await response.json();

    return NextResponse.json(spec);
  } catch (error) {
    return NextResponse.json(
      { error: "Service unavailable" },
      { status: 503 }
    );
  }
}
