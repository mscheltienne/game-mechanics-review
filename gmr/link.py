from __future__ import annotations

from typing import TYPE_CHECKING

from matplotlib.patches import PathPatch
from matplotlib.path import Path

if TYPE_CHECKING:
    from ._base import BaseElement


def link(ax, eltA: BaseElement, eltB: BaseElement, kwargs: dict | None = None) -> None:
    """Draw a link between the right side of box A and the left side of box B.

    Parameters
    ----------
    ax : Axes
        The matplotlib axes to draw the link on.
    eltA : BaseElement
        The first element to link. The center of the right edge of this element will be
        used as anchor.
    eltB : BaseElement
        The second element to link. The center of the left edge of this element will be
        used as anchor.
    kwargs : dict | None
        The keyword arguments to pass to the PathPatch constructor.
    """
    xA = eltA.x + eltA.width
    yA = eltA.y + eltA.height / 2
    xB = eltB.x
    yB = eltB.y + eltB.height / 2
    # get the line out of the element horizontally up to a control point at half the
    # horizontal distance between the 2 elements.
    verts = [
        (xA, yA),  # start
        (xA + 0.5 * (xB - xA), yA),  # control point 1
        (xA + 0.5 * (xB - xA), yB),  # control point 2
        (xB, yB),  # end
    ]
    codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO]
    path = Path(verts, codes)
    patch = PathPatch(path, **kwargs)
    ax.add_patch(patch)
