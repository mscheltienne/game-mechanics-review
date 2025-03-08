from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch
from matplotlib.text import Text

from .utils._checks import check_type, check_value


class TextBox:
    """A text box object.

    To draw the text box on a matplotlib axes, call the :meth:`~TextBox.draw` method.

    Parameters
    ----------
    text : str
        The text content of the textbox.
    xy : tuple[float, float]
        The (x, y) position of the textbox. The anchor point is the bottom-left corner.
    width : float
        The width of the textbox.
    height : float | str
        The height of the textbox. If ``'auto'``, the height will be automatically
        adjusted based on the text content.
    bgcolor : str
        The background color of the textbox. See the matplotlib color documentation:
        https://matplotlib.org/stable/gallery/color/named_colors.html
    edgecolor : str
        The edge color of the textbox. See the matplotlib color documentation:
        https://matplotlib.org/stable/gallery/color/named_colors.html
    boxstyle : str
        The box style, for instance ``"round,pad=0,rounding_size=0.05"`` or
        ``"square,pad=0"``.
    text_color : str
        The color of the text content. See the matplotlib color documentation:
        https://matplotlib.org/stable/gallery/color/named_colors.html
    font : str
        The font style of the text content.
    fontsize : int
        The font size of the text content.
    hpad : float
        The horizontal padding between the box and the text content, in data
        coordinates.
    text_alignment : str
        The text alignment within the box. Either ``'center'`` or ``'left'``.
    """

    def __init__(
        self,
        text: str,
        xy: tuple[float, float],
        width: float,
        height: float | str,
        bgcolor: str,
        edgecolor: str,
        boxstyle: str,
        text_color: str,
        font: str,
        fontsize=12,
        hpad: float = 0.01,
        text_alignment: str = "center",
    ) -> None:
        """Initialize a TextBox instance."""
        check_type(text, (str,), "text")
        if len(text) == 0:
            raise ValueError("The text content cannot be empty.")
        check_type(xy, (tuple,), "xy")
        if len(xy) != 2:
            raise ValueError("The xy parameter must be a tuple of two floats.")
        check_type(width, ("numeric",), "width")
        check_type(height, ("numeric", str), "height")
        if isinstance(height, str) and height != "auto":
            raise ValueError("The height parameter must be a float or 'auto'.")
        check_type(bgcolor, (str,), "bgcolor")
        check_type(edgecolor, (str,), "edgecolor")
        check_type(boxstyle, (str,), "boxstyle")
        check_type(text_color, (str,), "text_color")
        check_type(font, (str,), "font")
        check_type(fontsize, (int,), "fontsize")
        check_type(hpad, ("numeric",), "pad")
        if hpad < 0:
            raise ValueError("The hpad parameter must be a positive number.")
        check_type(text_alignment, (str,), "text_alignment")
        check_value(text_alignment, ("center", "left"), "text_alignment")
        self._text = text
        self._xy = xy
        self._width = width
        self._height = height
        self._bgcolor = bgcolor
        self._edgecolor = edgecolor
        self._boxstyle = boxstyle
        self._text_color = text_color
        self._font = font
        self._fontsize = fontsize
        self._hpad = hpad
        self._text_alignment = text_alignment

    def _compute_auto_height(self, ax: plt.Axes) -> float:
        """Estimate the textbox height based on the text."""
        fig = ax.figure
        renderer = fig.canvas.get_renderer()
        # create a temporary Text object with wrap turned on
        temp_text = Text(
            x=0,
            y=0,
            text=self._text,
            fontsize=self._fontsize,
            fontname=self._font,
            wrap=True,  # make matplotlib do line-wrapping for us
        )

        # force a "wrap width" in pixels by overriding this private method
        def _wrap_width():
            return _get_width_in_pixels(self._xy, self._width, self._hpad, ax)

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
            self._xy,  # bottom-left corner
            self._width,
            self._height,
            boxstyle=self._boxstyle,
            linewidth=1,
            facecolor=self._bgcolor,
            edgecolor=self._edgecolor,
            zorder=1,  # Keep it below the text
        )
        ax.add_patch(textbox_patch)
        # draw the text, with the same logic as the auto height
        text_x = (
            self._xy[0] + self._width / 2
            if self._text_alignment == "center"
            else self._xy[0] + self._hpad
        )
        text_y = self._xy[1] + self._height / 2
        text = ax.text(
            text_x,
            text_y,
            self._text,
            ha=self._text_alignment,
            va="center",
            fontname=self._font,
            fontsize=self._fontsize,
            color=self._text_color,
            wrap=True,
            zorder=2,  # Keep it on top of patch if desired
        )

        # force a "wrap width" in pixels by overriding this private method
        def _wrap_width():
            return _get_width_in_pixels(self._xy, self._width, self._hpad, ax)

        text._get_wrap_line_width = _wrap_width


def _get_width_in_pixels(
    xy: tuple[float, float], width: float, hpad: float, ax: plt.Axes
) -> float:
    """Convert the provided width to pixels."""
    x0_data = xy[0] + hpad
    x1_data = x0_data + (width - 2 * hpad)  # remove pad from both left & right
    x0_disp, _ = ax.transData.transform((x0_data, 0))
    x1_disp, _ = ax.transData.transform((x1_data, 0))
    return x1_disp - x0_disp
