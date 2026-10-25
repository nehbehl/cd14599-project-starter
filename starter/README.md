# Udatracker Starter Code

This directory contains the starter code for the Udatracker project. The initial structure of directories and files is described below.

```
.
├── backend
│   ├── __init__.py
│   ├── app.py
│   ├── in_memory_storage.py
│   ├── order_tracker.py
│   ├── requirements.txt
│   └── tests
│       ├── __init__.py
│       ├── test_api.py
│       └── test_order_tracker.py
├── frontend
│   ├── css
│   │   └── style.css
│   ├── index.html
│   └── js
│       └── script.js
├── pytest.ini
└── README.md
```

## Reflection

- **Design trade-off (return shapes):** Storage keeps orders in a dict keyed by `order_id`, but `list_all_orders` and `list_orders_by_status` return plain lists. I chose this so the API layer stays thin and can serialize results directly, since the API tests assert on `len(response.json)` and `response.json[0]`. The cost is a small conversion in `OrderTracker`, but it keeps JSON ordering concerns out of the route handlers.
- **Testing insight:** Writing the unit tests first clarified the contract between layers. `update_order_status` had to *return* the updated order (not just mutate storage) because the API responds with `json['status']`, and the "not found" tests pushed me to raise `ValueError` consistently so routes could map it cleanly to a 404.
- **Tooling insight:** Running `pycodestyle --max-line-length=79` surfaced PEP 8 issues I'd missed by eye (long lines, missing blank lines, import grouping). Keeping the checker in the loop let me fix style without changing behavior, verified by re-running the tests after each edit.
- **Next step:** Add a `DELETE /api/orders/<id>` endpoint and swap the in-memory store for persistent storage (e.g., SQLite) behind the same interface, plus stricter input validation on quantity and status values.
