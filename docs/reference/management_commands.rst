====================
Management commands
====================

prune_logs
==========

.. code-block:: bash

   python manage.py prune_logs [--days DAYS]

Deletes :class:`~cookie_consent.models.LogItem` records older than the
specified number of days.

**Options**

``--days DAYS``
    Number of days to use as the cutoff. Log items created more than this
    many days ago will be deleted. Defaults to ``90``.

**Example** — delete log items older than 30 days:

.. code-block:: bash

   python manage.py prune_logs --days 30

This command is safe to run repeatedly.
