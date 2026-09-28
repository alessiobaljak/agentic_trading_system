# 0331-controllo-28set-mfe.req

_eseguito: 2026-09-28 06:18 UTC_

**richiesta:** `mfe`
**eseguito:** `.venv/bin/python -m scripts.mfe_report`
**esito:** codice 1 in 1.2s

```
[firebase] connesso (Firestore + RTDB)

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
Traceback (most recent call last):
  File "/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/api_core/grpc_helpers.py", line 149, in error_remapped_callable
    return _StreamingResponseIterator(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/api_core/grpc_helpers.py", line 71, in __init__
    self._stored_first_result = next(self._wrapped)
                                ^^^^^^^^^^^^^^^^^^^
  File "/root/agentic_trading_system/.venv/lib/python3.12/site-packages/grpc/_channel.py", line 538, in __next__
    return self._next()
           ^^^^^^^^^^^^
  File "/root/agentic_trading_system/.venv/lib/python3.12/site-packages/grpc/_channel.py", line 956, in _next
    raise self
grpc._channel._MultiThreadedRendezvous: <_MultiThreadedRendezvous of RPC that terminated with:
	status = StatusCode.RESOURCE_EXHAUSTED
	details = "Quota exceeded."
	debug_error_string = "RESOURCE_EXHAUSTED:Quota exceeded."
>

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/root/agentic_trading_system/scripts/mfe_report.py", line 457, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/root/agentic_trading_system/scripts/mfe_report.py", line 231, in main
    trades = TradeLogger(fb).all_since(0.0)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/agentic_trading_system/bot/learning/trade_logger.py", line 38, in all_since
    return self.fb.query_collection(self.COLLECTION, order_by="exit_ts",
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/agentic_trading_system/bot/core/firebase_client.py", line 301, in query_collection
    return [d.to_dict() for d in q.stream()]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/stream_generator.py", line 58, in __next__
    return self._generator.__next__()
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/query.py", line 423, in _make_stream
    response_iterator, expected_prefix = self._get_stream_iterator(
                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/query.py", line 268, in _get_stream_iterator
    response_iterator = self._client._firestore_api.run_query(
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/services/firestore/client.py", line 1648, in run_query
    response = rpc(
               ^^^^
  File "/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/api_core/gapic_v1/method.py", line 128, in __call__
    return wrapped_func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/api_core/retry/retry_unary.py", line 294, in retry_wrapped_func
    return retry_target(
           ^^^^^^^^^^^^^
  File "/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/api_core/retry/retry_unary.py", line 156, in retry_target
    next_sleep = _retry_error_helper(
                 ^^^^^^^^^^^^^^^^^^^^
  File "/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/api_core/retry/retry_base.py", line 216, in _retry_error_helper
    raise final_exc from source_exc
  File "/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/api_core/retry/retry_unary.py", line 147, in retry_target
    result = target()
             ^^^^^^^^
  File "/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/api_core/timeout.py", line 130, in func_with_timeout
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/api_core/grpc_helpers.py", line 153, in error_remapped_callable
    raise exceptions.from_grpc_error(exc) from exc
google.api_core.exceptions.ResourceExhausted: 429 Quota exceeded.
```
