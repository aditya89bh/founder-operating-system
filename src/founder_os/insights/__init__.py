"""Historical insights for the Founder Operating System.

This subpackage reads the review snapshots recorded by the review engine and
derives deterministic historical insights -- how many reviews exist, their date
range, and the simple growth (latest snapshot minus earliest snapshot) of goals,
projects, priorities, decisions, and memories. It only reads stored snapshots; it
never recomputes historical state, and it performs no scoring, forecasting, or
AI reasoning.
"""
