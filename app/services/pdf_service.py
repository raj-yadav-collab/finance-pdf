from datetime import date
from io import BytesIO
from math import sqrt

from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas

from app.common.constants.pdf_colors import *
from app.common.enums.account_type import AccountType
from app.common.types.database_schemas.account_schema import AccountSchema
from app.common.types.responses.calculation_preview import SACSCalculation, TCCCalculation
from app.common.types.responses.client_details import ClientDetails


class PDFService:
    """Fixed-layout PDF report generator for SACS and TCC reports."""

    LANDSCAPE_WIDTH = 792
    LANDSCAPE_HEIGHT = 612

    @staticmethod
    def _set_fill(c: canvas.Canvas, color: tuple[float, float, float]) -> None:
        c.setFillColorRGB(*color)

    @staticmethod
    def _set_stroke(c: canvas.Canvas, color: tuple[float, float, float]) -> None:
        c.setStrokeColorRGB(*color)

    @staticmethod
    def _format_currency(amount: float | None) -> str:
        return f"${(amount or 0):,.2f}"

    @staticmethod
    def _format_date(date_obj: date | str | None) -> str:
        if not date_obj:
            return ""
        if isinstance(date_obj, str):
            date_obj = date.fromisoformat(date_obj)
        return date_obj.strftime("%m/%d/%y")

    @staticmethod
    def _client_display_name(client: ClientDetails) -> str:
        if client.first_name_2:
            return f"{client.first_name_1} & {client.first_name_2} {client.last_name_1}"
        return f"{client.first_name_1} {client.last_name_1}"

    def _draw_page_background(self, c: canvas.Canvas) -> None:
        self._set_fill(c, WHITE)
        self._set_stroke(c, WHITE)
        c.rect(0, 0, self.LANDSCAPE_WIDTH, self.LANDSCAPE_HEIGHT, fill=1, stroke=0)

    def generate_sacs_pdf(
        self,
        client: ClientDetails,
        sacs: SACSCalculation,
        report_date: date,
    ) -> bytes:
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=landscape(letter))

        self._draw_sacs_page1(c, client, sacs, report_date)
        c.showPage()
        self._draw_sacs_page2(c, client, sacs, report_date)
        c.showPage()

        c.save()
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()

    def _draw_header(
        self,
        c: canvas.Canvas,
        title: str,
        subtitle: str | None = None,
        report_date: date | None = None,
    ) -> None:
        w = self.LANDSCAPE_WIDTH
        self._set_fill(c, BLACK)
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(w / 2, 570, title)

        if subtitle:
            c.setFont("Helvetica", 13)
            c.drawCentredString(w / 2, 548, subtitle)

        if report_date:
            c.setFont("Helvetica", 9)
            c.drawRightString(w - 32, 570, f"Report Date: {self._format_date(report_date)}")

    def _draw_sacs_page1(
        self,
        c: canvas.Canvas,
        client: ClientDetails,
        sacs: SACSCalculation,
        report_date: date,
    ) -> None:
        w = self.LANDSCAPE_WIDTH
        h = self.LANDSCAPE_HEIGHT
        self._draw_page_background(c)
        self._draw_header(
            c,
            "Simple Automated Cash Flow System (SACS)",
            self._client_display_name(client),
            report_date,
        )

        self._draw_dollar_icon(c, 34, 564)
        self._draw_money_stack_icon(c, w - 112, 548)

        self._set_fill(c, INFLOW_GREEN)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(58, 540, f"{self._format_currency(sacs.inflow)} - Monthly Inflow")
        c.drawString(58, 525, f"{self._format_currency(sacs.outflow)} - Monthly Expenses")

        left_x = 165
        right_x = 627
        top_y = 355
        reserve_x = w / 2
        reserve_y = 166
        radius = 92

        self._draw_circle(
            c,
            left_x,
            top_y,
            radius,
            INFLOW_GREEN,
            "INFLOW",
            self._format_currency(sacs.inflow),
            "$1,000 Floor",
            stroke_color=BLACK,
            stroke_width=1.25,
            sublabel_color=BLACK,
            floor_line=True,
        )
        self._draw_circle(
            c,
            right_x,
            top_y,
            radius,
            OUTFLOW_RED,
            "OUTFLOW",
            self._format_currency(sacs.outflow),
            "$1,000 Floor",
            stroke_color=BLACK,
            stroke_width=1.25,
            sublabel_color=BLACK,
            floor_line=True,
        )
        self._draw_circle(
            c,
            reserve_x,
            reserve_y,
            radius,
            PRIVATE_RESERVE_BLUE,
            "PRIVATE\nRESERVE",
            "",
            "",
            stroke_color=BLACK,
            stroke_width=1.25,
        )
        self._draw_private_reserve_icon(c, reserve_x, reserve_y - 28, 0.82)

        self._draw_inflow_deposit_arrow(c, left_x - 114, top_y + radius + 24, left_x - 78, top_y + radius - 28)
        self._draw_sacs_expense_legend(c, right_x, top_y, w - 92, 498)

        self._draw_outline_arrow_right(
            c,
            left_x + radius + 24,
            top_y,
            right_x - radius - 24,
            top_y,
            OUTFLOW_RED,
            f"X = {self._format_currency(sacs.outflow)}/month*",
            "Automated transfer on the 28th",
        )
        self._draw_outline_l_arrow(
            c,
            left_x,
            top_y - radius - 16,
            reserve_x - radius - 12,
            reserve_y,
            PRIVATE_RESERVE_BLUE,
            f"{self._format_currency(sacs.excess)}/mo*",
        )

        c.setDash(4, 4)
        self._set_stroke(c, (0.55, 0.62, 0.82))
        c.line(w / 2, reserve_y - radius - 4, w / 2, 58)
        c.setDash()

        self._set_fill(c, BLACK)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(w / 2, 45, "MONTHLY CASHFLOW")

    def _draw_sacs_page2(
        self,
        c: canvas.Canvas,
        client: ClientDetails,
        sacs: SACSCalculation,
        report_date: date,
    ) -> None:
        w = self.LANDSCAPE_WIDTH
        h = self.LANDSCAPE_HEIGHT
        self._draw_page_background(c)
        self._draw_header(c, "Simple Automated Cash Flow System (SACS)", None, report_date)

        c.setDash(5, 4)
        self._set_stroke(c, (0.72, 0.72, 0.72))
        c.line(w / 2, h - 80, w / 2, 94)
        c.setDash()

        y = 330
        left_x = 220
        right_x = w - 220
        radius = 105

        self._draw_circle(
            c,
            left_x,
            y,
            radius,
            FICA_LIGHT_BLUE,
            "FICA\nACCOUNT",
            self._format_currency(sacs.private_reserve_balance),
            "6X Monthly Expenses + Deductibles",
            stroke_color=BLACK,
            stroke_width=1.25,
            sublabel_color=TEXT_COLOR,
            sublabel_inside=False,
        )
        self._draw_circle(
            c,
            right_x,
            y,
            radius,
            INVESTMENT_NAVY,
            "INVESTMENT\nACCOUNT",
            self._format_currency(sacs.schwab_investment_balance),
            "Remainder",
            stroke_color=BLACK,
            stroke_width=1.25,
            sublabel_color=TEXT_COLOR,
            sublabel_inside=False,
        )

        self._draw_outline_double_arrow(c, left_x + radius + 18, y, right_x - radius - 18, y, ARROW_BLUE)

        self._set_fill(c, BLACK)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(w / 2, 58, "LONG TERM CASHFLOW")
        self._set_fill(c, ARROW_BLUE)
        c.setFont("Helvetica-Oblique", 10)
        c.drawCentredString(w / 2, 39, "(Magnified Private Reserve Cashflow)")

    def _draw_circle(
        self,
        c: canvas.Canvas,
        cx: float,
        cy: float,
        radius: float,
        fill_color: tuple[float, float, float],
        label: str,
        amount: str,
        sublabel: str,
        stroke_color: tuple[float, float, float] | None = None,
        stroke_width: float = 0,
        amount_text_color: tuple[float, float, float] | None = None,
        sublabel_color: tuple[float, float, float] = WHITE,
        sublabel_inside: bool = True,
        floor_line: bool = False,
    ) -> None:
        self._set_fill(c, fill_color)
        self._set_stroke(c, stroke_color or fill_color)
        c.setLineWidth(stroke_width or 1)
        c.circle(cx, cy, radius, fill=1, stroke=1 if stroke_width else 0)

        self._draw_centered_lines(
            c,
            label.split("\n"),
            cx,
            cy + radius * 0.36,
            "Helvetica-Bold",
            15,
            16,
            WHITE,
        )

        if amount:
            self._set_fill(c, WHITE)
            c.roundRect(cx - 58, cy - 19, 116, 34, 6, fill=1, stroke=0)
            self._set_fill(c, amount_text_color or fill_color)
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(cx, cy - 4, amount)

        if floor_line:
            dy = -radius * 0.58
            half_width = sqrt(max(radius * radius - dy * dy, 0))
            self._set_stroke(c, BLACK)
            c.setLineWidth(1.1)
            c.line(cx - half_width, cy + dy, cx + half_width, cy + dy)

        if sublabel:
            sublabel_y = cy - radius * 0.67 if sublabel_inside else cy - radius - 18
            self._draw_centered_lines(c, sublabel.split("\n"), cx, sublabel_y, "Helvetica", 8, 10, sublabel_color)
        c.setLineWidth(1)

    def _draw_centered_lines(
        self,
        c: canvas.Canvas,
        lines: list[str],
        cx: float,
        cy: float,
        font: str,
        size: float,
        leading: float,
        color: tuple[float, float, float],
    ) -> None:
        self._set_fill(c, color)
        c.setFont(font, size)
        start_y = cy + ((len(lines) - 1) * leading / 2)
        for index, line in enumerate(lines):
            c.drawCentredString(cx, start_y - index * leading, line)

    def _draw_arrow_right(
        self,
        c: canvas.Canvas,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        color: tuple[float, float, float],
        label: str,
        sublabel: str | None = None,
    ) -> None:
        self._set_stroke(c, color)
        self._set_fill(c, color)
        c.setLineWidth(5)
        c.line(x1, y1, x2, y2)
        c.line(x2, y2, x2 - 13, y2 + 8)
        c.line(x2, y2, x2 - 13, y2 - 8)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString((x1 + x2) / 2, y1 + 18, label)
        if sublabel:
            self._set_fill(c, TEXT_COLOR)
            c.setFont("Helvetica", 8)
            c.drawCentredString((x1 + x2) / 2, y1 - 18, sublabel)
        c.setLineWidth(1)

    def _draw_outline_arrow_right(
        self,
        c: canvas.Canvas,
        x1: float,
        y: float,
        x2: float,
        y2: float,
        color: tuple[float, float, float],
        label: str,
        sublabel: str | None = None,
    ) -> None:
        arrow_height = 28
        head = 24
        path = c.beginPath()
        path.moveTo(x1, y - arrow_height / 2)
        path.lineTo(x2 - head, y - arrow_height / 2)
        path.lineTo(x2 - head, y - arrow_height)
        path.lineTo(x2, y)
        path.lineTo(x2 - head, y + arrow_height)
        path.lineTo(x2 - head, y + arrow_height / 2)
        path.lineTo(x1, y + arrow_height / 2)
        path.close()
        self._set_fill(c, WHITE)
        self._set_stroke(c, color)
        c.setLineWidth(1.8)
        c.drawPath(path, fill=1, stroke=1)
        self._set_fill(c, color)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString((x1 + x2) / 2, y + 7, label)
        if sublabel:
            self._set_fill(c, TEXT_COLOR)
            c.setFont("Helvetica", 8)
            c.drawCentredString((x1 + x2) / 2, y - 34, sublabel)
        c.setLineWidth(1)

    def _draw_l_arrow(
        self,
        c: canvas.Canvas,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        color: tuple[float, float, float],
        label: str,
    ) -> None:
        elbow_y = y2 + 72
        self._set_stroke(c, color)
        self._set_fill(c, color)
        c.setLineWidth(4)
        c.line(x1, y1, x1, elbow_y)
        c.line(x1, elbow_y, x2, elbow_y)
        c.line(x2, elbow_y, x2, y2)
        c.line(x2, y2, x2 - 8, y2 + 12)
        c.line(x2, y2, x2 + 8, y2 + 12)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString((x1 + x2) / 2, elbow_y + 12, label)
        c.setLineWidth(1)

    def _draw_outline_l_arrow(
        self,
        c: canvas.Canvas,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        color: tuple[float, float, float],
        label: str,
    ) -> None:
        elbow_y = y2 + 72
        self._set_stroke(c, color)
        self._set_fill(c, WHITE)
        c.setLineWidth(2)
        c.line(x1, y1, x1, elbow_y)
        c.line(x1, elbow_y, x2 - 14, elbow_y)
        path = c.beginPath()
        path.moveTo(x2 - 18, y2 + 24)
        path.lineTo(x2 + 18, y2 + 24)
        path.lineTo(x2, y2)
        path.close()
        self._set_fill(c, color)
        c.drawPath(path, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString((x1 + x2) / 2, elbow_y + 12, label)
        c.setLineWidth(1)

    def _draw_double_arrow(
        self,
        c: canvas.Canvas,
        x1: float,
        y: float,
        x2: float,
        y2: float,
        color: tuple[float, float, float],
    ) -> None:
        self._set_stroke(c, color)
        self._set_fill(c, color)
        c.setLineWidth(5)
        c.line(x1, y, x2, y2)
        c.line(x1, y, x1 + 13, y + 8)
        c.line(x1, y, x1 + 13, y - 8)
        c.line(x2, y2, x2 - 13, y2 + 8)
        c.line(x2, y2, x2 - 13, y2 - 8)
        c.setLineWidth(1)

    def _draw_outline_double_arrow(
        self,
        c: canvas.Canvas,
        x1: float,
        y: float,
        x2: float,
        y2: float,
        color: tuple[float, float, float],
    ) -> None:
        height = 16
        head = 18
        path = c.beginPath()
        path.moveTo(x1, y)
        path.lineTo(x1 + head, y + height)
        path.lineTo(x1 + head, y + height / 2)
        path.lineTo(x2 - head, y + height / 2)
        path.lineTo(x2 - head, y + height)
        path.lineTo(x2, y)
        path.lineTo(x2 - head, y - height)
        path.lineTo(x2 - head, y - height / 2)
        path.lineTo(x1 + head, y - height / 2)
        path.lineTo(x1 + head, y - height)
        path.close()
        self._set_fill(c, color)
        self._set_stroke(c, BLACK)
        c.setLineWidth(1.2)
        c.drawPath(path, fill=1, stroke=1)
        c.setLineWidth(1)

    def _draw_dollar_icon(self, c: canvas.Canvas, x: float, y: float) -> None:
        self._set_fill(c, (0.0, 0.35, 0.18))
        c.setFont("Helvetica", 34)
        c.drawString(x, y - 32, "$")

    def _draw_money_stack_icon(self, c: canvas.Canvas, x: float, y: float) -> None:
        self._set_stroke(c, (0.7, 0.7, 0.7))
        self._set_fill(c, (0.92, 0.92, 0.92))
        for offset in (0, 5, 10):
            c.roundRect(x + offset, y - offset, 42, 22, 2, fill=1, stroke=1)
        self._set_fill(c, (0.45, 0.45, 0.45))
        c.setFont("Helvetica", 6)
        c.drawCentredString(x + 31, y + 2, "$")

    def _draw_inflow_deposit_arrow(self, c: canvas.Canvas, x1: float, y1: float, x2: float, y2: float) -> None:
        self._set_stroke(c, BLACK)
        self._set_fill(c, INFLOW_GREEN)
        c.setLineWidth(1.2)
        path = c.beginPath()
        path.moveTo(x1, y1)
        path.lineTo(x1 + 18, y1 + 16)
        path.lineTo(x2 - 5, y2 + 21)
        path.lineTo(x2 + 12, y2 + 28)
        path.lineTo(x2, y2)
        path.lineTo(x2 - 30, y2 + 4)
        path.lineTo(x2 - 16, y2 + 12)
        path.lineTo(x1 - 3, y1 + 9)
        path.close()
        c.drawPath(path, fill=1, stroke=1)
        c.setLineWidth(1)

    def _draw_sacs_expense_legend(self, c: canvas.Canvas, right_x: float, top_y: float, label_x: float, label_y: float) -> None:
        self._set_fill(c, TEXT_COLOR)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(label_x, label_y, "X = Monthly")
        c.drawCentredString(label_x, label_y - 13, "Expenses")
        self._set_stroke(c, BLACK)
        c.setLineWidth(1.1)
        c.line(label_x + 18, label_y - 18, label_x + 18, top_y)
        c.line(label_x + 18, top_y, right_x + 62, top_y)
        c.line(right_x + 62, top_y, right_x + 70, top_y + 4)
        c.line(right_x + 62, top_y, right_x + 70, top_y - 4)
        c.setLineWidth(1)

    def _draw_private_reserve_icon(self, c: canvas.Canvas, cx: float, cy: float, scale: float) -> None:
        gold = (0.94, 0.71, 0.24)
        dark_gold = (0.76, 0.53, 0.13)
        panel_blue = (0.9, 0.96, 1.0)
        dial_blue = (0.14, 0.36, 0.62)

        self._set_fill(c, panel_blue)
        self._set_stroke(c, WHITE)
        c.setLineWidth(1.2)
        c.roundRect(cx - 34 * scale, cy - 18 * scale, 68 * scale, 34 * scale, 6 * scale, fill=1, stroke=1)

        self._set_fill(c, gold)
        self._set_stroke(c, dark_gold)
        c.roundRect(cx - 18 * scale, cy + 5 * scale, 36 * scale, 4 * scale, 2 * scale, fill=1, stroke=1)

        self._set_fill(c, dial_blue)
        self._set_stroke(c, dial_blue)
        c.circle(cx, cy - 5 * scale, 7 * scale, fill=1, stroke=0)
        self._set_stroke(c, WHITE)
        c.setLineWidth(1)
        c.line(cx - 4 * scale, cy - 5 * scale, cx + 4 * scale, cy - 5 * scale)
        c.line(cx, cy - 9 * scale, cx, cy - 1 * scale)

        for stack_index, x_offset in enumerate((-28, 28)):
            for coin_index in range(3 + stack_index):
                coin_y = cy - 25 * scale + coin_index * 5 * scale
                self._set_fill(c, gold)
                self._set_stroke(c, dark_gold)
                c.ellipse(
                    cx + (x_offset - 9) * scale,
                    coin_y,
                    cx + (x_offset + 9) * scale,
                    coin_y + 6 * scale,
                    fill=1,
                    stroke=1,
                )
        c.setLineWidth(1)

    def generate_tcc_pdf(
        self,
        client: ClientDetails,
        tcc: TCCCalculation,
        accounts: list[AccountSchema],
        balances: dict[int, float],
        report_date: date,
        balance_meta: dict[int, dict] | None = None,
    ) -> bytes:
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=landscape(letter))

        self._draw_tcc_page(c, client, tcc, accounts, balances, report_date, balance_meta or {})

        c.save()
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()

    def _draw_tcc_page(
        self,
        c: canvas.Canvas,
        client: ClientDetails,
        tcc: TCCCalculation,
        accounts: list[AccountSchema],
        balances: dict[int, float],
        report_date: date,
        balance_meta: dict[int, dict],
    ) -> None:
        w = self.LANDSCAPE_WIDTH
        h = self.LANDSCAPE_HEIGHT
        self._draw_page_background(c)

        self._set_stroke(c, BORDER_GREEN)
        c.setLineWidth(2)
        c.rect(12, 12, w - 24, h - 24, fill=0)

        self._set_stroke(c, BORDER_GREEN)
        c.setLineWidth(1)
        c.line(w / 2, 26, w / 2, h - 26)
        c.line(26, h / 2, w - 26, h / 2)

        self._set_fill(c, TEXT_COLOR)
        c.setFont("Helvetica", 8)
        c.drawCentredString(w / 2, h - 23, f"{self._client_display_name(client)} | {self._format_date(report_date)}")

        self._draw_summary_box(c, 24, h - 64, 126, 38, "Client 1 Retirement Only", tcc.client_1_retirement_total)
        self._draw_summary_box(c, w / 2 - 60, h - 64, 120, 38, "Liabilities", tcc.liabilities_total)
        if client.first_name_2:
            self._draw_summary_box(c, w - 150, h - 64, 126, 38, "Client 2 Retirement Only", tcc.client_2_retirement_total or 0)

        self._draw_client_bubble(c, 220, h - 58, client.first_name_1, client.age_1, client.dob_1, client.ssn_last4_1)
        if client.first_name_2:
            self._draw_client_bubble(c, w - 220, h - 58, client.first_name_2, client.age_2 or 0, client.dob_2, client.ssn_last4_2 or "")

        self._draw_section_label(c, 24, h / 2 + 8, "RETIREMENT")
        if client.first_name_2:
            self._draw_section_label(c, w - 104, h / 2 + 8, "RETIREMENT")
        self._draw_section_label(c, 24, h / 2 - 27, "NON\nRETIREMENT")
        self._draw_section_label(c, w - 104, h / 2 - 27, "NON\nRETIREMENT")

        grouped = self._group_accounts(accounts)
        self._draw_account_group(c, grouped[AccountType.RETIREMENT_CLIENT_1], balances, balance_meta, [90, 300], [407, 350])
        self._draw_account_group(c, grouped[AccountType.RETIREMENT_CLIENT_2], balances, balance_meta, [492, 702], [407, 350])
        self._draw_account_group(c, grouped[AccountType.NON_RETIREMENT], balances, balance_meta, [86, 230, 544, 686], [212, 126])
        self._draw_trust_group(c, grouped[AccountType.TRUST], balances, balance_meta, w / 2, h / 2 - 70)

        self._draw_liability_table(c, w / 2 - 96, 94, 192, grouped[AccountType.LIABILITY], balances)
        self._draw_summary_box(c, w / 2 - 100, 45, 200, 38, "NON RETIREMENT TOTAL", tcc.non_retirement_total)

        if any(meta.get("is_stale") for meta in balance_meta.values()):
            self._draw_stale_note(c, w - 222, 24, 198, 22)

    @staticmethod
    def _group_accounts(accounts: list[AccountSchema]) -> dict[AccountType, list[AccountSchema]]:
        grouped = {account_type: [] for account_type in AccountType}
        for account in sorted(accounts, key=lambda item: (item.account_type.value, item.display_order, item.id)):
            grouped[account.account_type].append(account)
        return grouped

    def _draw_summary_box(
        self,
        c: canvas.Canvas,
        x: float,
        y: float,
        width: float,
        height: float,
        label: str,
        amount: float,
    ) -> None:
        self._set_fill(c, SUMMARY_BOX_GRAY)
        c.roundRect(x, y, width, height, 6, fill=1, stroke=0)
        self._set_fill(c, WHITE)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(x + width / 2, y + height - 13, label)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(x + width / 2, y + 8, self._format_currency(amount))

    def _draw_section_label(self, c: canvas.Canvas, x: float, y: float, label: str) -> None:
        self._set_fill(c, BORDER_GREEN)
        c.setFont("Helvetica-Bold", 10)
        for index, line in enumerate(label.split("\n")):
            c.drawString(x, y - index * 12, line)

    def _draw_client_bubble(
        self,
        c: canvas.Canvas,
        cx: float,
        cy: float,
        label: str,
        age: int,
        dob: date | None,
        ssn: str,
    ) -> None:
        self._set_fill(c, CLIENT_BUBBLE_GREEN)
        self._set_stroke(c, BLACK)
        c.setLineWidth(2)
        c.circle(cx, cy, 43, fill=1, stroke=1)
        self._set_fill(c, WHITE)
        self._draw_fitted_centered_string(c, label, cx, cy + 18, "Helvetica-Bold", 15, 10, 74)
        c.setFont("Helvetica", 10.5)
        c.drawCentredString(cx, cy + 1, f"Age {age}")
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(cx, cy - 15, self._format_date(dob))
        c.setFont("Helvetica", 10.5)
        c.drawCentredString(cx, cy - 31, f"SSN {ssn}")
        c.setLineWidth(1)

    def _draw_fitted_centered_string(
        self,
        c: canvas.Canvas,
        text: str,
        cx: float,
        y: float,
        font: str,
        preferred_size: float,
        min_size: float,
        max_width: float,
    ) -> None:
        size = preferred_size
        while size > min_size and c.stringWidth(text, font, size) > max_width:
            size -= 0.5
        c.setFont(font, size)
        c.drawCentredString(cx, y, text)

    def _draw_account_group(
        self,
        c: canvas.Canvas,
        accounts: list[AccountSchema],
        balances: dict[int, float],
        balance_meta: dict[int, dict],
        xs: list[float],
        ys: list[float],
    ) -> None:
        for index, account in enumerate(accounts[: len(xs) * len(ys)]):
            row = index // len(xs)
            col = index % len(xs)
            self._draw_account_bubble(c, xs[col], ys[row], 38, account, balances, balance_meta)

    def _draw_trust_group(
        self,
        c: canvas.Canvas,
        accounts: list[AccountSchema],
        balances: dict[int, float],
        balance_meta: dict[int, dict],
        cx: float,
        cy: float,
    ) -> None:
        if not accounts:
            self._draw_section_label(c, cx - 24, cy + 32, "TRUST")
            return

        trust = accounts[0]
        meta = balance_meta.get(trust.id, {})
        self._set_fill(c, ACCOUNT_BUBBLE_BG)
        self._set_stroke(c, ACCOUNT_BUBBLE_STROKE)
        c.setLineWidth(1.25)
        c.circle(cx, cy, 58, fill=1, stroke=1)

        self._set_fill(c, TEXT_COLOR)
        c.setFont("Helvetica-Bold", 8)
        self._draw_centered_lines(c, self._wrap_label(trust.label, 18), cx, cy + 18, "Helvetica-Bold", 8, 10, TEXT_COLOR)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(cx, cy - 6, self._format_currency(balances.get(trust.id, 0)))

        balance_date = meta.get("balance_date")
        if balance_date:
            c.setFont("Helvetica", 7)
            c.drawCentredString(cx, cy - 22, f"a/o {self._format_date(balance_date)}")

        if meta.get("is_stale"):
            self._set_fill(c, STALE_RED)
            c.setFont("Helvetica-Bold", 15)
            c.drawString(cx + 44, cy + 36, "*")
        c.setLineWidth(1)

    @staticmethod
    def _wrap_label(label: str, max_chars: int) -> list[str]:
        words = label.split()
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if len(candidate) <= max_chars:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word[:max_chars]
        if current:
            lines.append(current)
        return lines[:3] or [label[:max_chars]]

    def _draw_account_bubble(
        self,
        c: canvas.Canvas,
        cx: float,
        cy: float,
        radius: float,
        account: AccountSchema,
        balances: dict[int, float],
        balance_meta: dict[int, dict],
    ) -> None:
        meta = balance_meta.get(account.id, {})
        self._set_fill(c, ACCOUNT_BUBBLE_BG)
        self._set_stroke(c, ACCOUNT_BUBBLE_STROKE)
        c.setLineWidth(1.25)
        c.circle(cx, cy, radius, fill=1, stroke=1)

        self._set_fill(c, TEXT_COLOR)
        c.setFont("Helvetica-Bold", 7)
        label = account.label[:18]
        c.drawCentredString(cx, cy + 12, label)
        c.setFont("Helvetica", 7)
        if account.account_last4:
            c.drawCentredString(cx, cy + 2, f"...{account.account_last4}")
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(cx, cy - 10, self._format_currency(balances.get(account.id, 0)))

        balance_date = meta.get("balance_date")
        if balance_date:
            c.setFont("Helvetica", 6)
            c.drawCentredString(cx, cy - 21, f"a/o {self._format_date(balance_date)}")

        if meta.get("is_stale"):
            self._set_fill(c, STALE_RED)
            c.setFont("Helvetica-Bold", 15)
            c.drawString(cx + radius - 8, cy + radius - 12, "*")

        c.setLineWidth(1)

    def _draw_stale_note(self, c: canvas.Canvas, x: float, y: float, width: float, height: float) -> None:
        self._set_fill(c, WHITE)
        self._set_stroke(c, ACCOUNT_BUBBLE_STROKE)
        c.rect(x, y, width, height, fill=1, stroke=1)
        self._set_fill(c, STALE_RED)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(x + width / 2, y + 8, "* Indicates we do not have up to date information")

    def _draw_liability_table(
        self,
        c: canvas.Canvas,
        x: float,
        y: float,
        width: float,
        liabilities: list[AccountSchema],
        balances: dict[int, float],
    ) -> None:
        height = 28 + max(1, len(liabilities)) * 16
        self._set_fill(c, LIAB_TABLE_BG)
        c.roundRect(x, y, width, height, 6, fill=1, stroke=0)
        self._set_fill(c, TEXT_COLOR)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(x + width / 2, y + height - 14, "Liabilities")
        c.setFont("Helvetica", 7)
        if not liabilities:
            c.drawCentredString(x + width / 2, y + 10, "No liabilities entered")
            return

        line_y = y + height - 30
        for liability in liabilities[:5]:
            label = liability.label[:18]
            amount = self._format_currency(balances.get(liability.id, 0))
            c.drawString(x + 10, line_y, label)
            c.drawRightString(x + width - 10, line_y, amount)
            line_y -= 15
