"""Review engine for the Founder Operating System.

This subpackage provides durable storage and retrieval for periodic reviews,
backed by SQLite. A review captures point-in-time snapshot counts read from the
other engines (goals, projects, priorities, decisions, and memories), turning
each review into a historical record. It defines the storage interface and its
concrete implementation.
"""
