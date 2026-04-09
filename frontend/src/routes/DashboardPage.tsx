import type { LucideIcon } from "lucide-react";
import {
  AlertTriangle,
  Briefcase,
  Building2,
  CheckCircle2,
  Globe2,
  Link2,
  Search,
  TrendingUp,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/StatusBadge";
import { SkeletonCard } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { listApplications, type ApplicationSummary } from "@/lib/api";
import { visibleStatusLabels } from "@/lib/application-options";

type StatusKey = keyof typeof visibleStatusLabels;

const STATUS_ACCENTS: Record<StatusKey, { fill: string; track: string }> = {
  draft: { fill: "var(--color-ink-25)", track: "var(--color-ink-10)" },
  needs_action: { fill: "var(--color-ember)", track: "var(--color-ember-10)" },
  in_progress: { fill: "var(--color-spruce)", track: "var(--color-spruce-10)" },
  complete: { fill: "var(--color-ink)", track: "var(--color-ink-10)" },
};

const SOURCE_META: Record<string, { label: string; icon: LucideIcon; accent: string; tint: string }> = {
  linkedin: { label: "LinkedIn", icon: Link2, accent: "#0a66c2", tint: "rgba(10,102,194,0.10)" },
  indeed: { label: "Indeed", icon: Search, accent: "#2557a7", tint: "rgba(37,87,167,0.10)" },
  google_jobs: { label: "Google Jobs", icon: Search, accent: "#1a73e8", tint: "rgba(26,115,232,0.10)" },
  glassdoor: { label: "Glassdoor", icon: Building2, accent: "#0caa41", tint: "rgba(12,170,65,0.10)" },
  ziprecruiter: { label: "ZipRecruiter", icon: TrendingUp, accent: "#1565ff", tint: "rgba(21,101,255,0.10)" },
  monster: { label: "Monster", icon: Globe2, accent: "#6d28d9", tint: "rgba(109,40,217,0.10)" },
  dice: { label: "Dice", icon: Briefcase, accent: "#7c3aed", tint: "rgba(124,58,237,0.10)" },
  company_website: { label: "Company Website", icon: Globe2, accent: "var(--color-spruce)", tint: "var(--color-spruce-10)" },
  unknown: { label: "Unknown", icon: Globe2, accent: "var(--color-ink-50)", tint: "var(--color-ink-05)" },
};

function getSourceMeta(origin: string) {
  return SOURCE_META[origin] ?? {
    label: origin.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase()),
    icon: Globe2,
    accent: "var(--color-spruce)",
    tint: "var(--color-spruce-10)",
  };
}

export function DashboardPage() {
  const navigate = useNavigate();
  const [applications, setApplications] = useState<ApplicationSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadApplications() {
    setError(null);
    try {
      const response = await listApplications();
      setApplications(response);
    } catch (err) {
      setApplications(null);
      setError(err instanceof Error ? err.message : "Unable to load dashboard.");
    }
  }

  useEffect(() => {
    void loadApplications();
  }, []);

  if (applications === null) {
    if (error) {
      return (
        <div className="page-enter space-y-5">
          <PageHeader title="Dashboard" subtitle="Application analytics and activity overview" />
          <Card variant="danger" density="compact">
            <p className="text-sm font-semibold" style={{ color: "var(--color-ember)" }}>
              Dashboard unavailable
            </p>
            <p className="mt-1 text-sm" style={{ color: "var(--color-ink-65)" }}>
              {error}
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              <Button onClick={() => void loadApplications()}>Retry</Button>
              <Button variant="secondary" onClick={() => navigate("/app/applications")}>
                Go to Applications
              </Button>
            </div>
          </Card>
        </div>
      );
    }

    return (
      <div className="page-enter space-y-5">
        <PageHeader title="Dashboard" subtitle="Application analytics and activity overview" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} density="compact" />)}
        </div>
        <div className="grid gap-4 lg:grid-cols-2">
          <SkeletonCard density="compact" />
          <SkeletonCard density="compact" />
        </div>
      </div>
    );
  }

  if (applications.length === 0) {
    return (
      <div className="page-enter space-y-5">
        <PageHeader title="Dashboard" subtitle="Application analytics and activity overview" />
        <EmptyState
          title="No applications yet"
          description="Create your first application to start tracking your job search progress and see analytics here."
          action={<Button onClick={() => navigate("/app/applications")}>Go to Applications</Button>}
        />
      </div>
    );
  }

  const total = applications.length;
  const appliedCount = applications.filter((a) => a.applied).length;
  const needsActionCount = applications.filter((a) => a.visible_status === "needs_action").length;
  const failedExtractions = applications.filter(
    (a) => a.failure_reason === "extraction_failed" || a.internal_state === "manual_entry_required",
  ).length;

  const statusCounts: Record<StatusKey, number> = {
    draft: 0,
    needs_action: 0,
    in_progress: 0,
    complete: 0,
  };
  for (const app of applications) {
    if (app.visible_status in statusCounts) {
      statusCounts[app.visible_status as StatusKey]++;
    }
  }

  const companyCounts: Record<string, number> = {};
  for (const app of applications) {
    const company = app.company?.trim() || "Unknown";
    companyCounts[company] = (companyCounts[company] ?? 0) + 1;
  }
  const topCompanies = Object.entries(companyCounts).sort((a, b) => b[1] - a[1]).slice(0, 6);
  const maxCompanyCount = topCompanies[0]?.[1] ?? 1;

  const monthlyCounts: Record<string, { created: number; applied: number }> = {};
  for (const app of applications) {
    const d = new Date(app.created_at);
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
    if (!monthlyCounts[key]) monthlyCounts[key] = { created: 0, applied: 0 };
    monthlyCounts[key].created++;
    if (app.applied) monthlyCounts[key].applied++;
  }
  const monthlyEntries = Object.entries(monthlyCounts).sort((a, b) => a[0].localeCompare(b[0])).slice(-6);
  const maxMonthly = Math.max(...monthlyEntries.map(([, value]) => value.created), 1);

  const originCounts: Record<string, number> = {};
  for (const app of applications) {
    const origin = app.job_posting_origin ?? "unknown";
    originCounts[origin] = (originCounts[origin] ?? 0) + 1;
  }
  const topOrigins = Object.entries(originCounts).sort((a, b) => b[1] - a[1]).slice(0, 4);
  const maxOriginCount = topOrigins[0]?.[1] ?? 1;

  const recentApps = [...applications]
    .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
    .slice(0, 5);

  return (
    <div className="page-enter space-y-5">
      <PageHeader
        title="Dashboard"
        subtitle="Application analytics and activity overview"
        actions={<Button onClick={() => navigate("/app/applications")}>View All Applications</Button>}
      />

      <div className="stagger-children grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Applications" value={total} accent="var(--color-ink)" tint="var(--color-ink-05)" icon={Briefcase} />
        <StatCard label="Applied" value={appliedCount} accent="var(--color-spruce)" tint="var(--color-spruce-10)" icon={CheckCircle2} />
        <StatCard label="Needs Action" value={needsActionCount} accent="var(--color-ember)" tint="var(--color-ember-10)" icon={AlertTriangle} />
        <StatCard label="Extraction Failures" value={failedExtractions} accent="var(--color-amber)" tint="var(--color-amber-10)" icon={Building2} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card density="compact">
          <h3 className="text-xs font-semibold uppercase tracking-[0.18em]" style={{ color: "var(--color-ink-40)" }}>
            Status Breakdown
          </h3>
          <div className="mt-4 space-y-2.5">
            {(Object.keys(statusCounts) as StatusKey[]).map((status) => (
              <div key={status} className="flex items-center gap-3">
                <StatusBadge status={status} size="sm" layout="rail" />
                <div className="flex-1 overflow-hidden rounded-full" style={{ background: STATUS_ACCENTS[status].track }}>
                  <div
                    className="h-2.5 rounded-full transition-all"
                    style={{
                      width: `${(statusCounts[status] / total) * 100}%`,
                      minWidth: statusCounts[status] > 0 ? "10px" : "0",
                      background: STATUS_ACCENTS[status].fill,
                    }}
                  />
                </div>
                <span className="w-7 text-right text-sm font-semibold tabular-nums" style={{ color: "var(--color-ink)" }}>
                  {statusCounts[status]}
                </span>
              </div>
            ))}
          </div>
        </Card>

        <Card density="compact">
          <h3 className="text-xs font-semibold uppercase tracking-[0.18em]" style={{ color: "var(--color-ink-40)" }}>
            Monthly Activity
          </h3>
          <div className="mt-4 flex items-end gap-2" style={{ height: "118px" }}>
            {monthlyEntries.map(([month, counts]) => (
              <div key={month} className="flex flex-1 flex-col items-center gap-1.5">
                <div className="flex w-full max-w-10 flex-col items-stretch justify-end gap-1" style={{ height: "94px" }}>
                  <div
                    className="rounded-t-md transition-all"
                    style={{
                      height: `${(counts.created / maxMonthly) * 100}%`,
                      minHeight: counts.created > 0 ? "6px" : "0",
                      background: "var(--color-ink-10)",
                    }}
                    title={`${counts.created} created`}
                  />
                  <div
                    className="rounded-b-md transition-all"
                    style={{
                      height: `${(counts.applied / maxMonthly) * 100}%`,
                      minHeight: counts.applied > 0 ? "6px" : "0",
                      background: "var(--color-spruce)",
                    }}
                    title={`${counts.applied} applied`}
                  />
                </div>
                <span className="text-[10px] font-semibold tracking-[0.14em]" style={{ color: "var(--color-ink-40)" }}>
                  {month.split("-")[1]}
                </span>
              </div>
            ))}
          </div>
          <div className="mt-3 flex items-center gap-4 text-[10px] uppercase tracking-[0.14em]" style={{ color: "var(--color-ink-40)" }}>
            <span className="flex items-center gap-1.5">
              <span className="inline-block h-2.5 w-2.5 rounded-sm" style={{ background: "var(--color-ink-10)" }} />
              Created
            </span>
            <span className="flex items-center gap-1.5">
              <span className="inline-block h-2.5 w-2.5 rounded-sm" style={{ background: "var(--color-spruce)" }} />
              Applied
            </span>
          </div>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card density="compact">
          <div className="flex items-center justify-between gap-3">
            <h3 className="text-xs font-semibold uppercase tracking-[0.18em]" style={{ color: "var(--color-ink-40)" }}>
              Top Companies
            </h3>
            <span className="text-[10px] font-semibold uppercase tracking-[0.16em]" style={{ color: "var(--color-ink-40)" }}>
              by volume
            </span>
          </div>
          <div className="mt-4 space-y-3">
            {topCompanies.map(([company, count]) => (
              <div key={company} className="space-y-1.5">
                <div className="flex items-center justify-between gap-3">
                  <span className="min-w-0 truncate text-sm font-medium" style={{ color: "var(--color-ink)" }}>
                    {company}
                  </span>
                  <span className="text-xs font-semibold tabular-nums" style={{ color: "var(--color-ink-50)" }}>
                    {count}
                  </span>
                </div>
                <div className="overflow-hidden rounded-full" style={{ background: "var(--color-spruce-10)" }}>
                  <div
                    className="h-2.5 rounded-full"
                    style={{
                      width: `${(count / maxCompanyCount) * 100}%`,
                      minWidth: count > 0 ? "10px" : "0",
                      background: "linear-gradient(90deg, var(--color-spruce) 0%, var(--color-spruce-light) 100%)",
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card density="compact">
          <div className="flex items-center justify-between gap-3">
            <h3 className="text-xs font-semibold uppercase tracking-[0.18em]" style={{ color: "var(--color-ink-40)" }}>
              Job Sources
            </h3>
            <span className="text-[10px] font-semibold uppercase tracking-[0.16em]" style={{ color: "var(--color-ink-40)" }}>
              capture mix
            </span>
          </div>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {topOrigins.map(([origin, count]) => {
              const meta = getSourceMeta(origin);
              const Icon = meta.icon;
              const share = Math.round((count / total) * 100);

              return (
                <div
                  key={origin}
                  className="rounded-xl border p-3"
                  style={{ borderColor: "var(--color-border)", background: "linear-gradient(180deg, rgba(255,255,255,0.96) 0%, rgba(255,255,255,0.88) 100%)" }}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2.5 min-w-0">
                      <span className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg" style={{ background: meta.tint, color: meta.accent }}>
                        <Icon size={16} />
                      </span>
                      <div className="min-w-0">
                        <div className="truncate text-sm font-medium" style={{ color: "var(--color-ink)" }}>
                          {meta.label}
                        </div>
                        <div className="text-[10px] font-semibold uppercase tracking-[0.16em]" style={{ color: "var(--color-ink-40)" }}>
                          {share}% share
                        </div>
                      </div>
                    </div>
                    <span className="text-lg font-semibold tabular-nums" style={{ color: meta.accent }}>
                      {count}
                    </span>
                  </div>
                  <div className="mt-3 overflow-hidden rounded-full" style={{ background: meta.tint }}>
                    <div
                      className="h-2.5 rounded-full"
                      style={{
                        width: `${(count / maxOriginCount) * 100}%`,
                        minWidth: count > 0 ? "10px" : "0",
                        background: meta.accent,
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      </div>

      <Card density="compact">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-semibold uppercase tracking-[0.18em]" style={{ color: "var(--color-ink-40)" }}>
            Recent Activity
          </h3>
          <Button size="sm" variant="secondary" onClick={() => navigate("/app/applications")}>
            View all
          </Button>
        </div>
        <div className="mt-3 divide-y" style={{ borderColor: "var(--color-border)" }}>
          {recentApps.map((app) => (
            <div
              key={app.id}
              className="flex cursor-pointer items-center gap-3 py-2.5 transition-colors first:pt-0 last:pb-0"
              onClick={() => navigate(`/app/applications/${app.id}`)}
              onMouseEnter={(e) => { e.currentTarget.style.background = "var(--color-ink-05)"; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}
            >
              <StatusBadge status={app.visible_status} size="sm" />
              <div className="min-w-0 flex-1">
                <div className="truncate text-sm font-medium" style={{ color: "var(--color-ink)" }}>
                  {app.job_title ?? "Untitled"}
                </div>
                <div className="truncate text-xs" style={{ color: "var(--color-ink-40)" }}>
                  {app.company ?? "Unknown"} · {new Date(app.updated_at).toLocaleDateString()}
                </div>
              </div>
              {app.applied && (
                <span className="rounded-full px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em]" style={{ color: "var(--color-spruce)", background: "var(--color-spruce-05)" }}>
                  Applied
                </span>
              )}
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

function StatCard({
  label,
  value,
  accent,
  tint,
  icon: Icon,
}: {
  label: string;
  value: number;
  accent: string;
  tint: string;
  icon: LucideIcon;
}) {
  return (
    <Card density="compact" className="relative overflow-hidden">
      <span
        className="absolute right-4 top-4 inline-flex h-10 w-10 items-center justify-center rounded-xl"
        style={{ background: tint, color: accent }}
      >
        <Icon size={18} />
      </span>
      <div className="text-[11px] font-semibold uppercase tracking-[0.18em]" style={{ color: "var(--color-ink-40)" }}>
        {label}
      </div>
      <div className="mt-2 font-display text-3xl font-semibold tabular-nums" style={{ color: accent }}>
        {value}
      </div>
      <div className="mt-3 h-1.5 w-20 rounded-full" style={{ background: tint }}>
        <div className="h-full w-8 rounded-full" style={{ background: accent }} />
      </div>
    </Card>
  );
}
