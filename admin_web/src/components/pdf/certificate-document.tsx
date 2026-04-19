"use client";

import { Document, Page, Text, View, StyleSheet } from "@react-pdf/renderer";
import type { User } from "@/types";
import type { Checklist } from "@/types";
import "@/lib/pdf/fonts";

interface CertificateDocumentProps {
  user: User;
  checklist: Checklist & { template_name?: string };
  translations: {
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
  };
  locale: string;
}

const styles = StyleSheet.create({
  page: {
    padding: 40,
    fontFamily: "Roboto",
    backgroundColor: "#fafafa",
  },
  border: {
    borderWidth: 3,
    borderColor: "#3B82F6",
    borderRadius: 8,
    padding: 30,
    height: "100%",
    position: "relative",
  },
  innerBorder: {
    borderWidth: 1,
    borderColor: "#93C5FD",
    borderRadius: 4,
    padding: 20,
    height: "100%",
    alignItems: "center",
    justifyContent: "center",
  },
  logo: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#3B82F6",
    marginBottom: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: "bold",
    color: "#1F2937",
    marginBottom: 8,
    textAlign: "center",
  },
  subtitle: {
    fontSize: 14,
    color: "#6B7280",
    marginBottom: 40,
    textAlign: "center",
  },
  presentedTo: {
    fontSize: 12,
    color: "#6B7280",
    marginBottom: 10,
    textTransform: "uppercase",
    letterSpacing: 2,
  },
  recipientName: {
    fontSize: 28,
    fontWeight: "bold",
    color: "#1F2937",
    marginBottom: 8,
    textAlign: "center",
  },
  recipientRole: {
    fontSize: 14,
    color: "#4B5563",
    marginBottom: 40,
    textAlign: "center",
  },
  achievement: {
    fontSize: 13,
    color: "#374151",
    textAlign: "center",
    marginBottom: 40,
    lineHeight: 1.6,
    maxWidth: "80%",
  },
  dateSection: {
    marginBottom: 50,
  },
  dateLabel: {
    fontSize: 11,
    color: "#6B7280",
    marginBottom: 4,
  },
  dateValue: {
    fontSize: 14,
    color: "#1F2937",
    fontWeight: "bold",
  },
  signatureArea: {
    flexDirection: "row",
    justifyContent: "space-between",
    width: "80%",
    marginBottom: 40,
  },
  signatureBlock: {
    alignItems: "center",
    width: "45%",
  },
  signatureLine: {
    borderTopWidth: 1,
    borderTopColor: "#9CA3AF",
    width: "100%",
    paddingTop: 8,
    marginTop: 20,
  },
  signatureLabel: {
    fontSize: 10,
    color: "#6B7280",
    textAlign: "center",
  },
  certId: {
    position: "absolute",
    bottom: 20,
    right: 20,
    fontSize: 9,
    color: "#9CA3AF",
  },
  footer: {
    position: "absolute",
    bottom: 20,
    left: 20,
    fontSize: 9,
    color: "#9CA3AF",
  },
});

export function CertificateDocument({
  user,
  checklist,
  translations,
  locale,
}: CertificateDocumentProps) {
  const formatDate = (dateString: string | null) => {
    if (!dateString) return "-";
    const date = new Date(dateString);
    return date.toLocaleDateString(locale === "ru" ? "ru-RU" : "en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  const fullName = `${user.first_name} ${user.last_name || ""}`.trim();
  const department = user.department?.name || "";
  const position = user.position || "";

  return (
    <Document>
      <Page size="A4" orientation="landscape" style={styles.page}>
        <View style={styles.border}>
          <View style={styles.innerBorder}>
            {/* Logo */}
            <Text style={styles.logo}>{translations.appName}</Text>

            {/* Title */}
            <Text style={styles.title}>{translations.title}</Text>
            <Text style={styles.subtitle}>{translations.subtitle}</Text>

            {/* Recipient */}
            <Text style={styles.presentedTo}>{translations.presentedTo}</Text>
            <Text style={styles.recipientName}>{fullName}</Text>
            <Text style={styles.recipientRole}>
              {position}
              {position && department ? ", " : ""}
              {department}
            </Text>

            {/* Achievement */}
            <Text style={styles.achievement}>
              {translations.achievement.replace(
                "{templateName}",
                checklist.template_name || "Onboarding"
              )}
            </Text>

            {/* Date */}
            <View style={styles.dateSection}>
              <Text style={styles.dateLabel}>{translations.completedOn}</Text>
              <Text style={styles.dateValue}>{formatDate(checklist.completed_at)}</Text>
            </View>

            {/* Signatures */}
            <View style={styles.signatureArea}>
              <View style={styles.signatureBlock}>
                <View style={styles.signatureLine} />
                <Text style={styles.signatureLabel}>{translations.hrSignature}</Text>
              </View>
              <View style={styles.signatureBlock}>
                <View style={styles.signatureLine} />
                <Text style={styles.signatureLabel}>{translations.mentorSignature}</Text>
              </View>
            </View>

            {/* Certificate ID */}
            <Text style={styles.certId}>
              {translations.certificateId}: {checklist.id.toString().padStart(8, "0")}
            </Text>
          </View>
        </View>

        {/* Footer */}
        <Text style={styles.footer} fixed>
          {translations.appName}
        </Text>
      </Page>
    </Document>
  );
}
