from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.config import settings
from app.models import Evaluation, InterviewSession


def _radar_png(evaluations: list[Evaluation]) -> BytesIO:
    dims = ["Technical", "Problem Solving", "Communication", "Confidence"]
    vals = [
        sum(e.technical_score for e in evaluations) / max(1, len(evaluations)),
        sum(e.problem_solving_score for e in evaluations) / max(1, len(evaluations)),
        sum(e.communication_score for e in evaluations) / max(1, len(evaluations)),
        sum(e.confidence_score for e in evaluations) / max(1, len(evaluations)),
    ]
    angles = [i / len(dims) * 2 * 3.1415926535 for i in range(len(dims))]
    angles += angles[:1]
    values = vals + vals[:1]
    fig = plt.figure(figsize=(5, 4))
    ax = fig.add_subplot(111, polar=True)
    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.15)
    ax.set_ylim(0, 100)
    ax.set_thetagrids([a * 180 / 3.1415926535 for a in angles[:-1]], dims)
    ax.set_title("HireIQ Skill Radar", pad=18)
    out = BytesIO()
    fig.savefig(out, format="png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    out.seek(0)
    return out


def generate_report(session: InterviewSession, db) -> str:
    report_path = Path(settings.report_dir) / f"hireiq_{session.id}.pdf"
    doc = SimpleDocTemplate(
        str(report_path), pagesize=A4, leftMargin=1.4 * cm, rightMargin=1.4 * cm,
        topMargin=1.2 * cm, bottomMargin=1.2 * cm,
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle("title", parent=styles["Title"], alignment=TA_CENTER, fontSize=23, leading=28)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=14, leading=18, spaceAfter=7)
    body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=9.5, leading=13)
    small = ParagraphStyle("small", parent=body, fontSize=8.5, leading=11)

    candidate = session.candidate
    question_order = {q.id: q.order_index for q in session.interview.questions}
    responses = sorted(session.responses, key=lambda r: question_order.get(r.question_id, 9999))
    evaluations = [r.evaluation for r in responses if r.evaluation is not None]
    overall = sum(e.overall_score for e in evaluations) / max(1, len(evaluations))
    if overall >= 75:
        recommendation = "Proceed"
    elif overall >= 55:
        recommendation = "Hold"
    else:
        recommendation = "Reject"

    story = [
        Paragraph("HireIQ", title),
        Paragraph("Multimodal AI Interview Evaluation Report", ParagraphStyle("sub", parent=body, alignment=TA_CENTER, fontSize=12)),
        Spacer(1, 0.35 * cm),
        Table([
            ["Candidate", candidate.name, "Interview", session.interview.title],
            ["Email", candidate.email, "Rubric", session.interview.rubric_name],
            ["Overall", f"{overall:.1f}/100", "Recommendation", recommendation],
        ], colWidths=[2.2*cm, 5.5*cm, 2.2*cm, 6.1*cm], style=TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e9eef7")),
            ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#9aa7bd")),
            ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
            ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
            ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 8.5),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("TOPPADDING", (0,0), (-1,-1), 5),
        ])),
        Spacer(1, 0.4 * cm),
        Image(_radar_png(evaluations), width=12.5*cm, height=10*cm),
        Spacer(1, 0.25 * cm),
        Paragraph("Score Interpretation", h2),
        Paragraph("Scores are evidence-based outputs of the configured rubric and LLM evaluation. Confidence and sentiment are supplementary signals and should not be used as proxies for protected traits.", body),
        PageBreak(),
        Paragraph("Per-question Evaluation", h2),
    ]

    for idx, response in enumerate(responses, start=1):
        question = next((q for q in session.interview.questions if q.id == response.question_id), None)
        eval_ = response.evaluation
        story.append(Paragraph(f"Q{idx}. {question.prompt if question else 'Question'}", h2))
        if eval_:
            story.append(Table([
                ["Technical", f"{eval_.technical_score:.0f}", "Problem Solving", f"{eval_.problem_solving_score:.0f}"],
                ["Communication", f"{eval_.communication_score:.0f}", "Confidence", f"{eval_.confidence_score:.0f}"],
                ["Overall", f"{eval_.overall_score:.0f}", "Recommendation", eval_.recommendation],
            ], colWidths=[3*cm, 2*cm, 3.5*cm, 2*cm], style=TableStyle([
                ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#b1b8c6")),
                ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
                ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
                ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
                ("FONTSIZE", (0,0), (-1,-1), 8),
            ])))
            story.append(Spacer(1, 0.15*cm))
            story.append(Paragraph("Transcript", ParagraphStyle("label", parent=body, fontName="Helvetica-Bold")))
            story.append(Paragraph(response.transcript.replace("&", "&amp;").replace("<", "&lt;"), small))
            story.append(Spacer(1, 0.12*cm))
            story.append(Paragraph("Strengths: " + "; ".join(eval_.strengths), small))
            story.append(Paragraph("Improvements: " + "; ".join(eval_.improvements), small))
            story.append(Paragraph("Rationale: " + eval_.rationale, small))
            story.append(Paragraph(f"NLP: sentiment={response.nlp_json.get('sentiment', 'neutral')}; keywords={', '.join(response.nlp_json.get('keywords', []))}", small))
        else:
            story.append(Paragraph("No completed evaluation.", body))
        story.append(Spacer(1, 0.3*cm))

    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("AI Ethics & Bias Note", h2))
    story.append(Paragraph("HireIQ is a decision-support system, not an autonomous hiring authority. Reviewers should validate evidence, monitor for disparate effects, and avoid treating accent, sentiment, or confidence heuristics as measures of candidate worth.", body))
    doc.build(story)
    return str(report_path)
