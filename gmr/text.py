from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch
from matplotlib.text import Text

from ._base import BaseElement
from .utils._checks import check_type, check_value


class TextBox(BaseElement):
    """A text box object.

    To draw the text box on a matplotlib axes, call the :meth:`~TextBox.draw` method.

    Parameters
    ----------
    x : float
        The x-coordinate of the bottom-left corner of the element, in data
        coordinates.
    y : float
        The y-coordinate of the bottom-left corner of the element, in data
        coordinates.
    text : str
        The text content of the textbox.
    width : float
        The width of the textbox.
    height : float | str
        The height of the textbox. If ``'auto'``, the height will be automatically
        adjusted based on the text content.
    hpad : float
        The horizontal padding between the box and the text content, in data
        coordinates.
    text_alignment : str
        The text alignment within the box. Either ``'center'`` or ``'left'``.
    bbox_kwargs : dict
        Additional keyword arguments to pass to the FancyBboxPatch constructor.
    text_kwargs : dict
        Additional keyword arguments to pass to the Text constructor.
    """

    def __init__(
        self,
        text: str,
        x: float,
        y: float,
        width: float,
        height: float | str,
        hpad: float = 0.01,
        text_alignment: str = "center",
        bbox_kwargs: dict | None = None,
        text_kwargs: dict | None = None,
    ) -> None:
        """Initialize a TextBox instance."""
        super().__init__(x, y)
        check_type(text, (str,), "text")
        if len(text) == 0:
            raise ValueError("The text content cannot be empty.")
        check_type(width, ("numeric",), "width")
        check_type(height, ("numeric", str), "height")
        if isinstance(height, str) and height != "auto":
            raise ValueError("The height parameter must be a float or 'auto'.")
        check_type(hpad, ("numeric",), "pad")
        if hpad < 0:
            raise ValueError("The hpad parameter must be a positive number.")
        check_type(text_alignment, (str,), "text_alignment")
        check_value(text_alignment, ("center", "left"), "text_alignment")
        check_type(bbox_kwargs, (dict, None), "bbox_kwargs")
        check_type(text_kwargs, (dict, None), "text_kwargs")
        self._text = text
        self._width = width
        self._height = height
        self._hpad = hpad
        self._text_alignment = text_alignment
        self._bbox_kwargs = bbox_kwargs if bbox_kwargs is not None else {}
        self._text_kwargs = text_kwargs if text_kwargs is not None else {}

    def _compute_auto_height(self, ax: plt.Axes) -> float:
        """Estimate the textbox height based on the text."""
        fig = ax.figure
        renderer = fig.canvas.get_renderer()
        # create a temporary Text object with wrap turned on
        temp_text = Text(
            x=0,
            y=0,
            text=self._text,
            wrap=True,  # make matplotlib do line-wrapping for us
            **self._text_kwargs,
        )

        # force a "wrap width" in pixels by overriding this private method
        def _wrap_width() -> float:
            return _get_width_in_pixels(self.x, self._width, self._hpad, ax)

        temp_text._get_wrap_line_width = _wrap_width
        # associate the text with a figure and an axes, force a draw to get the size and
        # remove the temporary text
        ax.add_artist(temp_text)
        fig.canvas.draw()
        # measure in display coordinate and transform to data coordinate
        bbox_disp = temp_text.get_window_extent(renderer=renderer)
        bbox_data = bbox_disp.transformed(ax.transData.inverted())
        auto_height = np.abs(bbox_data.height)
        temp_text.remove()
        return auto_height

    def draw(self, ax: plt.Axes) -> None:
        """Draw the textbox on the provided matplotlib axes.

        Parameters
        ----------
        ax : Axes
            The matplotlib axes on which to draw the textbox.
        """
        self._height = (
            self._compute_auto_height(ax) if self._height == "auto" else self._height
        )
        # draw the FancyBboxPatch, with round or square corners
        textbox_patch = FancyBboxPatch(
            (self.x, self.y),  # bottom-left corner
            self._width,
            self._height,
            zorder=1,  # Keep it below the text
            **self._bbox_kwargs,
        )
        ax.add_patch(textbox_patch)
        # draw the text, with the same logic as the auto height
        text_x = (
            self.x + self._width / 2
            if self._text_alignment == "center"
            else self.x + self._hpad
        )
        text_y = self.y + self._height / 2
        text = ax.text(
            text_x,
            text_y,
            self._text,
            ha=self._text_alignment,
            va="center",
            wrap=True,
            zorder=2,  # Keep it on top of patch if desired
            **self._text_kwargs,
        )

        # force a "wrap width" in pixels by overriding this private method
        def _wrap_width() -> float:
            return _get_width_in_pixels(self.x, self._width, self._hpad, ax)

        text._get_wrap_line_width = _wrap_width

    @property
    def height(self) -> float:
        """The height of the textbox."""
        if self._height == "auto":
            raise RuntimeError("The height will be available after drawing.")
        return self._height

    @property
    def width(self) -> float:
        """The width of the textbox."""
        return self._width


def _get_width_in_pixels(x: float, width: float, hpad: float, ax: plt.Axes) -> float:
    """Convert the provided width to pixels."""
    x0_data = x + hpad
    x1_data = x0_data + (width - 2 * hpad)  # remove pad from both left & right
    x0_disp, _ = ax.transData.transform((x0_data, 0))
    x1_disp, _ = ax.transData.transform((x1_data, 0))
    return x1_disp - x0_disp
