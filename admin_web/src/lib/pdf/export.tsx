"use client";

import { pdf } from "@react-pdf/renderer";
import type { ChecklistStats } from "@/types";
import type { User } from "@/types";
import type { Checklist } from "@/types";

interface ReportData {
  stats: ChecklistStats | null;
  userCount: number;
  monthlyData: Array<{ month: string; newUsers: number; completed: number }>;
  completionTimeData: Array<{ range: string; count: number }>;
  departmentData: Array<{ name: string; value: number; color: string }>;
}

interface ReportTranslations {
  title: string;
  overview: string;
  generatedAt: string;
  summary: string;
  totalNewbies: string;
  completed: string;
  inProgress: string;
  overdue: string;
  averageTime: string;
  completionRate: string;
  byDepartments: string;
  monthlyDynamics: string;
  completionTimeDistribution: string;
  department: string;
  count: string;
  month: string;
  newUsers: string;
  range: string;
  appName: string;
  page: string;
  of: string;
}

interface CertificateTranslations {
  title: string;
  subtitle: string;
  presentedTo: string;
  achievement: string;
  completedOn: string;
  hrSignature: string;
  mentorSignature: string;
  date: string;
  certificateId: string;
  appName: string;
}

// Dynamic imports to avoid SSR issues with @react-pdf/renderer
async function getReportDocument() {
  const { ReportDocument } = await import("@/components/pdf/report-document");
  return ReportDocument;
}

async function getCertificateDocument() {
  const { CertificateDocument } = await import("@/components/pdf/certificate-document");
  return CertificateDocument;
}

export async function generateOnboardingReportPDF(
  data: ReportData,
  translations: ReportTranslations,
  locale: string
): Promise<Blob> {
  const ReportDocument = await getReportDocument();

  const doc = (
    <ReportDocument
      data={data}
      translations={translations}
      locale={locale}
    />
  );

  const blob = await pdf(doc).toBlob();
  return blob;
}

export async function generateCertificatePDF(
  user: User,
  checklist: Checklist & { template_name?: string },
  translations: CertificateTranslations,
  locale: string
): Promise<Blob> {
  const CertificateDocument = await getCertificateDocument();

  const doc = (
    <CertificateDocument
      user={user}
      checklist={checklist}
      translations={translations}
      locale={locale}
    />
  );

  const blob = await pdf(doc).toBlob();
  return blob;
}

export function downloadPDF(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export function generatePDFReportFilename(locale: string): string {
  const date = new Date().toISOString().split("T")[0];
  return locale === "ru" ? `отчет-онбординг-${date}.pdf` : `onboarding-report-${date}.pdf`;
}

export function generateCertificateFilename(user: User, locale: string): string {
  const fullName = `${user.first_name}_${user.last_name || ""}`.trim().replace(/\s+/g, "_");
  const date = new Date().toISOString().split("T")[0];
  return locale === "ru" ? `сертификат_${fullName}_${date}.pdf` : `certificate_${fullName}_${date}.pdf`;
}
