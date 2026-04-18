"use client";

import { useState, useEffect } from "react";
import {
  SwaggerViewer,
  ServiceSelector,
  services,
} from "@/components/features/api-docs";
import { useAuth } from "@/hooks/use-auth";
import { Loader2, AlertCircle } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";

export default function ApiDocsPage() {
  const [selectedService, setSelectedService] = useState(services[0]);
  const [spec, setSpec] = useState<object | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuth();

  useEffect(() => {
    async function loadSpec() {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`/api/docs/${selectedService.id}`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });

        if (response.ok) {
          const data = await response.json();
          setSpec(data);
        } else {
          setSpec(null);
          setError(`Failed to load spec: ${response.statusText}`);
        }
      } catch (err) {
        setSpec(null);
        setError("Service unavailable");
      } finally {
        setLoading(false);
      }
    }

    loadSpec();
  }, [selectedService, token]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="API Documentation"
        subtitle="Explore and test all service APIs"
      />

      <ServiceSelector
        selected={selectedService.id}
        onSelect={setSelectedService}
      />

      {loading ? (
        <div className="flex h-64 items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
        </div>
      ) : error ? (
        <div className="flex h-64 flex-col items-center justify-center gap-2 text-slate-500">
          <AlertCircle className="h-8 w-8" />
          <p>{error}</p>
          <p className="text-sm">
            Failed to load API specification for {selectedService.name}
          </p>
        </div>
      ) : spec ? (
        <div className="overflow-hidden rounded-lg border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-900">
          <SwaggerViewer spec={spec} authToken={token || undefined} />
        </div>
      ) : null}
    </div>
  );
}
