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
from ._link import link_textbox
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
            1, 1, figsize=self._figsize, layout="constrained"
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
            xy=(0, 0),
            width=COLUMN_WIDTHS[0],
            height=0.05,
            bgcolor="#eeeeee",
            edgecolor="black",
            boxstyle="square,pad=0",
            text_color="black",
            font="Consolas",
            fontsize=20,
            hpad=0.5,
            text_alignment="center",
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
                xy=(x_pos, self._bbox_title._height + VPAD),
                width=COLUMN_WIDTHS[k],
                height=0.07,
                bgcolor="#eeeeee",
                edge_color="black",
                boxstyle="square,pad=0" if k == 2 else "round,pad=0,rounding_size=0.01",
                text_color="black",
                font="Corbel",
                fontsize=18,
                hpad=0.01,
                text_alignment="center",
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
                y_pos += COLUMNS_HEIGHTS[0] + VPAD
                continue
            TextBox(
                text=inter,
                xy=(0, y_pos),
                width=COLUMN_WIDTHS[0],
                height=COLUMNS_HEIGHTS[0],
                bgcolor=INTERVENTION_TYPE_COLORS[inter],
                boxstyle="round,pad=0,rounding_size=0.005",
                text_color="black",
                font="DejaVu Sans",
                fontsize=14,
                hpad=0.01,
                text_alignment="center",
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
            xy=(COLUMN_WIDTHS[0] + HPAD, self._y_pos_engagement_init),
            width=COLUMN_WIDTHS[1],
            height=COLUMNS_HEIGHTS[1],
            bgcolor=ENGAGEMENT_TYPE_COLORS[name],
            boxstyle="round,pad=0,rounding_size=0.005",
            text_color="black",
            font="DejaVu Sans",
            fontsize=14,
            hpad=0.01,
            text_alignment="center",
        )
        text_engagement.draw(self._ax)
        # then we iterate on the whats and hows
        y_pos_what = self._y_pos_engagement_init
        for what, hows in whats.items():
            # draw the what
            text_what = TextBox(
                text=what,
                xy=(np.sum(COLUMN_WIDTHS[:2]) + 2 * HPAD, y_pos_what),
                width=COLUMN_WIDTHS[2],
                height="auto",
                bgcolor="#ffffff",
                boxstyle="square,pad=0",
                text_color="black",
                font="DejaVu Sans",
                fontsize=12,
                hpad=0.01,
                text_alignment="left",
            )
            text_what.draw(self._ax)
            link_textbox(self._ax, text_engagement, text_what)
            # draw the hows
            y_pos_how = y_pos_what
            for how in hows:
                text_how = TextBox(
                    text=how,
                    xy=(np.sum(COLUMN_WIDTHS[:3]) + 3 * HPAD, y_pos_how),
                    width=COLUMN_WIDTHS[3],
                    height="auto",
                    bgcolor="#ffffff",
                    boxstyle="round,pad=0,rounding_size=0.005",
                    text_color="black",
                    font="DejaVu Sans",
                    fontsize=12,
                    hpad=0.01,
                    text_alignment="left",
                )
                text_how.draw(self._ax)
                link_textbox(self._ax, text_what, text_how)
                y_pos_how += text_how._height + VPAD
                y_pos_what += text_how._height + VPAD
        self._y_pos_engagement_init = max(
            self._y_pos_engagement_init + text_engagement._height + VPAD, y_pos_what
        )

    @property
    def name(self) -> str:
        """The name of the game."""
        return self._name
