"""Shared CLI types."""

from __future__ import annotations


class CliError(RuntimeError):
    """User-facing CLI error; main() prints the message and exits non-zero."""
