from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from matplotlib.patches import ConnectionPatch, PathPatch
from matplotlib.path import Path

if TYPE_CHECKING:
    from ._text import TextBox


def link_textbox(
    ax, boxA: TextBox, boxB: TextBox, color: str = "black", linewidth: int = 1
) -> None:
    """Draw a link between the right side of box A and the left side of box B."""
    xA = boxA._xy[0] + boxA._width
    yA = boxA._xy[1] + boxA._height / 2

    xB = boxB._xy[0]
    yB = boxB._xy[1] + boxB._height / 2

    # Straight line if yA ~= yB
    if np.isclose(yA, yB, atol=1e-7):
        conn = ConnectionPatch(
            xyA=(xA, yA),
            xyB=(xB, yB),
            coordsA="data",
            coordsB="data",
            arrowstyle="-",
            color=color,
            linewidth=linewidth,
        )
        ax.add_patch(conn)
        return

    # Otherwise, draw a cubic Bézier (C-shaped) from (xA, yA) to (xB, yB).
    # We'll pick two control points so that the curve
    # leaves boxA horizontally and arrives at boxB horizontally:
    # - first control near (xA, yA)
    # - second control near (xB, yB)
    ctrlx1 = xA + 0.5 * (xB - xA)  # 1/2 of the distance
    ctrly1 = yA
    ctrlx2 = xA + 0.5 * (xB - xA)  # 3/2 of the distance
    ctrly2 = yB

    verts = [
        (xA, yA),  # start
        (ctrlx1, ctrly1),  # control point 1
        (ctrlx2, ctrly2),  # control point 2
        (xB, yB),  # end
    ]
    codes = [
        Path.MOVETO,
        Path.LINETO,
        Path.LINETO,
        Path.LINETO,
    ]

    path = Path(verts, codes)
    patch = PathPatch(
        path,
        facecolor="none",
        edgecolor="black",
        linewidth=2,
    )
    ax.add_patch(patch)
