"use client";

import {
  Document,
  Page,
  Text,
  View,
  StyleSheet,
  PDFDownloadLink,
} from "@react-pdf/renderer";
import type { ChecklistStats } from "@/types";

interface ReportDocumentProps {
  data: {
    stats: ChecklistStats | null;
    userCount: number;
    monthlyData: Array<{ month: string; newUsers: number; completed: number }>;
    completionTimeData: Array<{ range: string; count: number }>;
    departmentData: Array<{ name: string; value: number; color: string }>;
  };
  translations: {
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
  };
  locale: string;
}

const styles = StyleSheet.create({
  page: {
    padding: 30,
    fontFamily: "Helvetica",
    fontSize: 11,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 20,
    borderBottomWidth: 1,
    borderBottomColor: "#ccc",
    paddingBottom: 10,
  },
  headerLeft: {
    flex: 1,
  },
  headerRight: {
    flex: 1,
    alignItems: "flex-end",
  },
  logo: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#3B82F6",
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    marginBottom: 6,
  },
  subtitle: {
    fontSize: 12,
    color: "#666",
    marginBottom: 20,
  },
  section: {
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: "bold",
    marginBottom: 8,
    backgroundColor: "#f5f5f5",
    padding: 8,
    borderRadius: 4,
  },
  row: {
    flexDirection: "row",
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
    paddingVertical: 6,
  },
  label: {
    width: "50%",
    fontWeight: "bold",
  },
  value: {
    width: "50%",
  },
  table: {
    width: "100%",
    borderWidth: 1,
    borderColor: "#ccc",
  },
  tableHeader: {
    flexDirection: "row",
    backgroundColor: "#f5f5f5",
    borderBottomWidth: 1,
    borderBottomColor: "#ccc",
    padding: 8,
  },
  tableRow: {
    flexDirection: "row",
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
    padding: 6,
  },
  tableCell: {
    flex: 1,
    fontSize: 10,
  },
  tableCellHeader: {
    flex: 1,
    fontSize: 10,
    fontWeight: "bold",
  },
  footer: {
    position: "absolute",
    bottom: 30,
    left: 30,
    right: 30,
    flexDirection: "row",
    justifyContent: "space-between",
    fontSize: 9,
    color: "#666",
  },
  twoColumn: {
    flexDirection: "row",
    gap: 15,
  },
  column: {
    flex: 1,
  },
});

export function ReportDocument({ data, translations, locale }: ReportDocumentProps) {
  const { stats, userCount, monthlyData, completionTimeData, departmentData } = data;

  const formatDate = (date: Date) => {
    return date.toLocaleDateString(locale === "ru" ? "ru-RU" : "en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  return (
    <Document>
      <Page size="A4" style={styles.page}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.headerLeft}>
            <Text style={styles.logo}>{translations.appName}</Text>
          </View>
          <View style={styles.headerRight}>
            <Text style={{ fontSize: 10, color: "#666" }}>
              {translations.generatedAt}: {formatDate(new Date())}
            </Text>
          </View>
        </View>

        {/* Title */}
        <Text style={styles.title}>{translations.title}</Text>
        <Text style={styles.subtitle}>{translations.overview}</Text>

        {/* Summary Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{translations.summary}</Text>
          <View style={styles.row}>
            <Text style={styles.label}>{translations.totalNewbies}:</Text>
            <Text style={styles.value}>{stats?.total || userCount || 0}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>{translations.completed}:</Text>
            <Text style={styles.value}>{stats?.completed || 0}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>{translations.inProgress}:</Text>
            <Text style={styles.value}>{stats?.in_progress || 0}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>{translations.overdue}:</Text>
            <Text style={styles.value}>{stats?.overdue || 0}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>{translations.averageTime}:</Text>
            <Text style={styles.value}>
              {Math.round(stats?.avg_completion_days || 0)} {translations.completed.toLowerCase()}
            </Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>{translations.completionRate}:</Text>
            <Text style={styles.value}>{Math.round(stats?.completion_rate || 0)}%</Text>
          </View>
        </View>

        {/* Two Column Layout for Department and Monthly Data */}
        <View style={[styles.section, styles.twoColumn]}>
          {/* Department Breakdown */}
          <View style={styles.column}>
            <Text style={styles.sectionTitle}>{translations.byDepartments}</Text>
            <View style={styles.table}>
              <View style={styles.tableHeader}>
                <Text style={styles.tableCellHeader}>{translations.department}</Text>
                <Text style={styles.tableCellHeader}>{translations.count}</Text>
              </View>
              {departmentData.map((dept, index) => (
                <View key={index} style={styles.tableRow}>
                  <Text style={styles.tableCell}>{dept.name}</Text>
                  <Text style={styles.tableCell}>{dept.value}</Text>
                </View>
              ))}
            </View>
          </View>

          {/* Monthly Dynamics */}
          <View style={styles.column}>
            <Text style={styles.sectionTitle}>{translations.monthlyDynamics}</Text>
            <View style={styles.table}>
              <View style={styles.tableHeader}>
                <Text style={styles.tableCellHeader}>{translations.month}</Text>
                <Text style={styles.tableCellHeader}>{translations.newUsers}</Text>
                <Text style={styles.tableCellHeader}>{translations.completed}</Text>
              </View>
              {monthlyData.slice(0, 6).map((month, index) => (
                <View key={index} style={styles.tableRow}>
                  <Text style={styles.tableCell}>{month.month}</Text>
                  <Text style={styles.tableCell}>{month.newUsers}</Text>
                  <Text style={styles.tableCell}>{month.completed}</Text>
                </View>
              ))}
            </View>
          </View>
        </View>

        {/* Completion Time Distribution */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{translations.completionTimeDistribution}</Text>
          <View style={styles.table}>
            <View style={styles.tableHeader}>
              <Text style={styles.tableCellHeader}>{translations.range}</Text>
              <Text style={styles.tableCellHeader}>{translations.count}</Text>
            </View>
            {completionTimeData.map((item, index) => (
              <View key={index} style={styles.tableRow}>
                <Text style={styles.tableCell}>{item.range}</Text>
                <Text style={styles.tableCell}>{item.count}</Text>
              </View>
            ))}
          </View>
        </View>

        {/* Footer */}
        <View style={styles.footer} fixed>
          <Text>
            {translations.appName} - {translations.title}
          </Text>
          <Text>
            {translations.page} 1 {translations.of} 1
          </Text>
        </View>
      </Page>
    </Document>
  );
}

export { PDFDownloadLink };
