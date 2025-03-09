from __future__ import annotations

import numpy as np
from matplotlib import pyplot as plt

from ._constants import (
    COLUMN_WIDTHS,
    COLUMNS_HEIGHTS,
    ENGAGEMENT_TYPE_COLORS,
    HPAD,
    INTERVENTION_TYPE_COLORS,
    INTERVENTION_TYPE_ORDER,
    VPAD,
)
from .link import link
from .text import TextBox
from .utils._checks import check_type, check_value


class FigureGame:
    """A figure object for a given game.

    A figure object has 4 columns and is organized as:

      Game Name
    +-----------------------------------------------------------------+
    | header            |                    |      |                 |
    +-----------------------------------------------------------------+
    | intervention type | type of engagement | what |design principle |
    |                   |                    |      |                 |
    |                   |                    |      |                 |
    +-----------------------------------------------------------------+
    """

    def __init__(self, name: str, *, figsize: tuple[int, int] = (15, 10)) -> None:
        check_type(name, (str,), "name")
        check_type(figsize, (tuple,), "figsize")
        if len(figsize) != 2:
            raise ValueError("figsize must be a tuple of 2 integers.")
        check_type(figsize[0], ("int-like",), "figsize[0]")
        check_type(figsize[1], ("int-like",), "figsize[1]")
        self._name = name
        self._figsize = figsize
        self._y_pos_engagement_init = None

    def draw(
        self,
        intervention_types: list[str] | tuple[str],
        engagements: dict[str, dict[str, tuple[str, ...] | list[str]]],
    ) -> None:
        """Draw the figure on a matplotlib axes."""
        self._fig, self._ax = plt.subplots(
            1, 1, figsize=self._figsize, layout="constrained", facecolor="white"
        )
        self._ax.invert_yaxis()
        self._ax.axis("off")

        self._draw_title()
        self._draw_header()
        self._draw_intervention_type(intervention_types)
        for name, whats in engagements.items():
            self._draw_engagement(name, whats)
        # now resize based on the update `self._y_pos_engagement_init` value
        self._ax.set_ylim(self._y_pos_engagement_init, 0)
        self._ax.set_xlim(0, np.sum(COLUMN_WIDTHS) + 3 * HPAD)

    def _draw_title(self) -> None:
        """Draw the title at the top of the first column."""
        self._bbox_title = TextBox(
            text=self._name,
            x=0,
            y=0,
            width=COLUMN_WIDTHS[0],
            height=0.05,
            hpad=0.5,
            text_alignment="center",
            bbox_kwargs=dict(
                facecolor="#eeeeee", edgecolor="black", boxstyle="square,pad=0"
            ),
            text_kwargs=dict(color="black", font="Consolas", fontsize=24),
        )
        self._bbox_title.draw(self._ax)

    def _draw_header(self) -> None:
        """Draw the headers."""
        if not hasattr(self, "_bbox_title"):
            raise RuntimeError("The title must be drawn first.")
        # properties
        headers = (
            "Primary type of intervention",
            "Type of engagement",
            "What game design features support this engagement?",
            "Which design principles support this features?",
        )
        # draw the headers
        x_pos = 0
        self._bbox_headers = []
        for k, header in enumerate(headers):
            text = TextBox(
                text=header,
                x=x_pos,
                y=self._bbox_title._height + VPAD,
                width=COLUMN_WIDTHS[k],
                height=0.07,
                hpad=0.01,
                text_alignment="center",
                bbox_kwargs=dict(
                    facecolor="#eeeeee",
                    edgecolor="black",
                    boxstyle="square,pad=0"
                    if k == 2
                    else "round,pad=0,rounding_size=0.01",
                ),
                text_kwargs=dict(
                    color="black",
                    font="Corbel",
                    fontsize=18,
                ),
            )
            text.draw(self._ax)
            x_pos += COLUMN_WIDTHS[k] + HPAD
            self._bbox_headers.append(text)

    def _draw_intervention_type(
        self,
        intervention_types: list[str] | tuple[str],
    ) -> None:
        """Draw the intervention type."""
        check_type(intervention_types, (list, tuple), "intervention_types")
        for inter in intervention_types:
            check_type(inter, (str,), "intervention_type")
            check_value(inter.strip(), INTERVENTION_TYPE_COLORS, "intervention_type")
        if not hasattr(self, "_bbox_title") or not hasattr(self, "_bbox_headers"):
            raise RuntimeError("The title and headers must be drawn first.")
        header_heights = [header._height for header in self._bbox_headers]
        assert all(elt == header_heights[0] for elt in header_heights)  # sanity-check
        # sanitize
        intervention_types = [inter.strip() for inter in intervention_types]
        # properties
        # draw the boxes
        y_pos = self._bbox_title._height + self._bbox_headers[0]._height + 2 * VPAD
        for inter in INTERVENTION_TYPE_ORDER:
            if inter not in intervention_types:
                facecolor = INTERVENTION_TYPE_COLORS[inter] + "10"
                edgecolor = "lightgray"
                textcolor = "lightgray"
            else:
                facecolor = INTERVENTION_TYPE_COLORS[inter] + "ff"
                edgecolor = "black"
                textcolor = "black"
            TextBox(
                text=inter,
                x=0,
                y=y_pos,
                width=COLUMN_WIDTHS[0],
                height=COLUMNS_HEIGHTS[0],
                hpad=0.01,
                text_alignment="center",
                bbox_kwargs=dict(
                    facecolor=facecolor,
                    boxstyle="round,pad=0,rounding_size=0.005",
                    edgecolor=edgecolor,
                ),
                text_kwargs=dict(
                    color=textcolor,
                    font="DejaVu Sans",
                    fontsize=14,
                ),
            ).draw(self._ax)
            y_pos += COLUMNS_HEIGHTS[0] + VPAD

    def _draw_engagement(
        self, name: str, whats: dict[str, tuple[str, ...] | list[str]]
    ) -> None:
        """Draw the engagement type."""
        check_type(name, (str,), "name")
        check_value(name.strip(), ENGAGEMENT_TYPE_COLORS, "name")
        if self._y_pos_engagement_init is None:
            if not hasattr(self, "_bbox_title") or not hasattr(self, "_bbox_headers"):
                raise RuntimeError("The title and headers must be drawn first.")
            self._y_pos_engagement_init = (
                self._bbox_title._height + self._bbox_headers[0]._height + 2 * VPAD
            )
        # first, we can draw the engagement name in the second column
        text_engagement = TextBox(
            text=name,
            x=COLUMN_WIDTHS[0] + HPAD,
            y=self._y_pos_engagement_init,
            width=COLUMN_WIDTHS[1],
            height=COLUMNS_HEIGHTS[1],
            hpad=0.01,
            text_alignment="center",
            bbox_kwargs=dict(
                facecolor=ENGAGEMENT_TYPE_COLORS[name],
                boxstyle="round,pad=0,rounding_size=0.005",
            ),
            text_kwargs=dict(
                color="black",
                font="DejaVu Sans",
                fontsize=14,
            ),
        )
        text_engagement.draw(self._ax)
        # then we iterate on the whats and hows
        y_pos_what = self._y_pos_engagement_init
        for what, hows in whats.items():
            # draw the what
            text_what = TextBox(
                text=what,
                x=np.sum(COLUMN_WIDTHS[:2]) + 2 * HPAD,
                y=y_pos_what,
                width=COLUMN_WIDTHS[2],
                height="auto",
                hpad=0.01,
                text_alignment="left",
                bbox_kwargs=dict(
                    facecolor="#ffffff",
                    boxstyle="square,pad=0",
                    edgecolor=ENGAGEMENT_TYPE_COLORS[name],
                    linewidth=1.5,
                ),
                text_kwargs=dict(
                    color="black",
                    font="DejaVu Sans",
                    fontsize=12,
                ),
            )
            text_what.draw(self._ax)
            link(
                self._ax,
                text_engagement,
                text_what,
                kwargs=dict(
                    facecolor="none",
                    edgecolor=ENGAGEMENT_TYPE_COLORS[name],
                    linewidth=1.5,
                ),
            )
            # draw the hows
            y_pos_how = y_pos_what
            for how in hows:
                text_how = TextBox(
                    text=how,
                    x=np.sum(COLUMN_WIDTHS[:3]) + 3 * HPAD,
                    y=y_pos_how,
                    width=COLUMN_WIDTHS[3],
                    height="auto",
                    hpad=0.01,
                    text_alignment="left",
                    bbox_kwargs=dict(
                        facecolor="#ffffff",
                        boxstyle="round,pad=0,rounding_size=0.005",
                        edgecolor=ENGAGEMENT_TYPE_COLORS[name],
                        linewidth=1.5,
                    ),
                    text_kwargs=dict(
                        color="black",
                        font="DejaVu Sans",
                        fontsize=12,
                    ),
                )
                text_how.draw(self._ax)
                link(
                    self._ax,
                    text_what,
                    text_how,
                    kwargs=dict(
                        facecolor="none",
                        edgecolor=ENGAGEMENT_TYPE_COLORS[name],
                        linewidth=1.5,
                    ),
                )
                y_pos_how += text_how._height + VPAD
                y_pos_what += text_how._height + VPAD
        self._y_pos_engagement_init = max(
            self._y_pos_engagement_init + text_engagement._height + VPAD, y_pos_what
        )

    @property
    def name(self) -> str:
        """The name of the game."""
        return self._name
