"use client";

import dynamic from "next/dynamic";
import "swagger-ui-react/swagger-ui.css";

const SwaggerUI = dynamic(import("swagger-ui-react"), { ssr: false });

interface SwaggerViewerProps {
  spec: object;
  authToken?: string;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function SwaggerViewer({ spec, authToken }: SwaggerViewerProps) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const requestInterceptor = (req: any) => {
    if (authToken) {
      req.headers["Authorization"] = `Bearer ${authToken}`;
    }
    return req;
  };

  return (
    <div className="swagger-ui-wrapper">
      <SwaggerUI
        spec={spec}
        requestInterceptor={requestInterceptor}
        docExpansion="list"
        defaultModelsExpandDepth={-1}
        tryItOutEnabled={true}
      />
    </div>
  );
}
