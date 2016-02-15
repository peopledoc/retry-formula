=======================================
 Transparent network outage resilience
=======================================

This formula hijack salt states to enable retry on failure.

.. code-block:: yaml

    my_resiliant_state:
      pkg.installed:
        - name: nano


Available states
================

- ``pkg.installed``
