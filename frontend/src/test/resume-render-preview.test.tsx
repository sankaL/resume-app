import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ResumeRenderPreview } from "@/components/ResumeRenderPreview";
import type { ResumeRenderModel } from "@/lib/api";

describe("resume render preview", () => {
  it("renders structured experience and education rows with right-side metadata", () => {
    const model: ResumeRenderModel = {
      render_contract_version: "2026-04-19.v1",
      header: {
        name: "Alex Example",
        contact_line: "alex@example.com | 555-0100 | Toronto, ON",
        extra_lines: [],
      },
      normalized_markdown: "",
      sections: [
        {
          heading: "Professional Experience",
          kind: "professional_experience",
          entries: [
            {
              row1_left: "**Google**",
              row1_right: "Los Angeles, CA",
              row2_left: "*VP Engineering*",
              row2_right: "Dec 2019 - Present",
              bullets: ["Led **platform** work with [`kubectl`](https://example.com/kubectl)."],
            },
          ],
        },
        {
          heading: "Education",
          kind: "education",
          entries: [
            {
              row1_left: "Masters University",
              row1_right: "Los Angeles, CA",
              row2_left: "Master of Science in Mechanical Engineering with Honors",
              row2_right: "Apr 2021",
              bullets: ["Honors thesis."],
            },
          ],
        },
      ],
    };

    render(<ResumeRenderPreview model={model} />);

    expect(screen.getByText("Google")).toBeInTheDocument();
    expect(screen.queryByText("**Google**")).not.toBeInTheDocument();
    expect(screen.getAllByText("Los Angeles, CA")).toHaveLength(2);
    expect(screen.getByText("VP Engineering")).toBeInTheDocument();
    expect(screen.getByText("Dec 2019 - Present")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "kubectl" })).toBeInTheDocument();
    expect(screen.getByText("Masters University")).toBeInTheDocument();
    expect(screen.getByText("Apr 2021")).toBeInTheDocument();
    expect(screen.getByText("Honors thesis.")).toBeInTheDocument();
  });

  it("renders markdown sections at the same body size as structured bullets", () => {
    const model: ResumeRenderModel = {
      render_contract_version: "2026-04-19.v1",
      header: null,
      normalized_markdown: "",
      sections: [
        {
          heading: "Summary",
          kind: "markdown",
          markdown_body: "Candidate summary paragraph.",
          entries: [],
        },
        {
          heading: "Skills",
          kind: "markdown",
          markdown_body: "- Skill A\n- Skill B",
          entries: [],
        },
      ],
    };

    render(<ResumeRenderPreview model={model} />);

    expect(screen.getByText("Candidate summary paragraph.").closest("div")).toHaveClass("text-sm");
    expect(screen.getByText("Skill A").closest("div")).toHaveClass("text-sm");
  });
});
