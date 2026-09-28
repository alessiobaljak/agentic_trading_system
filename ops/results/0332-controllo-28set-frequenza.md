# 0332-controllo-28set-frequenza.req

_eseguito: 2026-09-28 06:18 UTC_

**richiesta:** `frequenza`
**eseguito:** `.venv/bin/python -m scripts.signal_frequency`
**esito:** codice 1 in 1.9s

```
[firebase] connesso (Firestore + RTDB)

--- stderr ---
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
  File "/root/agentic_trading_system/scripts/signal_frequency.py", line 201, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/root/agentic_trading_system/scripts/signal_frequency.py", line 90, in main
    adaptation = AdaptationEngine()
                 ^^^^^^^^^^^^^^^^^^
  File "/root/agentic_trading_system/bot/learning/adaptation.py", line 61, in __init__
    self.load_weights()
  File "/root/agentic_trading_system/bot/learning/adaptation.py", line 67, in load_weights
    doc = self.fb.get_doc("strategy_weights", "current") or {}
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/agentic_trading_system/bot/core/firebase_client.py", line 282, in get_doc
    snap = self._fs.collection(collection).document(doc_id).get()
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/document.py", line 413, in get
    response_iter = self._client._firestore_api.batch_get_documents(
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/services/firestore/client.py", line 1227, in batch_get_documents
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
