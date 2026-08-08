# Contributing

Keep WGM portable and non-authorizing.

Before opening a change:

1. Add a test for every validation or routing rule.
2. Run `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v`.
3. Do not add credentials, endpoints, user data, machine paths, execution code,
   automatic retry, fallback, or provider-specific policy.
4. Keep all routing output advisory: `authority_effect` and `execution_effect`
   must remain false.
