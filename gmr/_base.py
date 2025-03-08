from __future__ import annotations

from abc import ABC, abstractmethod

from .utils._checks import check_type


class BaseElement(ABC):
    """A base class for all elements in the game design drawing.

    Parameters
    ----------
    x : float
        The x-coordinate of the bottom-left corner of the element, in data
        coordinates.
    y : float
        The y-coordinate of the bottom-left corner of the element, in data
        coordinates.
    """

    @abstractmethod
    def __init__(self, x: float, y: float) -> None:
        check_type(x, ("numeric",), "x")
        check_type(y, ("numeric",), "y")
        self._x = x
        self._y = y

    @abstractmethod
    def draw(self) -> None:
        pass

    @property
    def x(self) -> float:
        """The x-coordinate of the element."""
        return self._x

    @property
    def y(self) -> float:
        """The y-coordinate of the element."""
        return self._y

    @property
    @abstractmethod
    def width(self) -> float:
        """The width of the element."""

    @property
    @abstractmethod
    def height(self) -> float:
        """The height of the element."""
