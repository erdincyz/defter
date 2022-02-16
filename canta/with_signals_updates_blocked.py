# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '07/Sep/2017'
__author__ = 'Erdinç Yılmaz'

from contextlib import contextmanager


# ---------------------------------------------------------------------
@contextmanager
def signals_blocked_and_updates_disabled(widget):
    """
    """

    widget.setUpdatesEnabled(False)
    widget.blockSignals(True)
    yield
    widget.blockSignals(False)
    widget.setUpdatesEnabled(True)


# ---------------------------------------------------------------------
@contextmanager
def signals_blocked(widget):
    """
    """

    widget.blockSignals(True)
    yield
    widget.blockSignals(False)


# ---------------------------------------------------------------------
@contextmanager
def slot_disconnected(signal, slot):
    """
    """

    signal.disconnect(slot)
    yield
    signal.connect(slot)


# ---------------------------------------------------------------------
@contextmanager
def slot_disconnected_and_updates_disabled(signal, slot, widget):
    """
    """

    signal.disconnect(slot)
    widget.setUpdatesEnabled(False)
    yield
    signal.connect(slot)
    widget.setUpdatesEnabled(True)
