import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)

#
# --- TODO: add test functions below this line ---
#

def test_add_order_successfully(order_tracker, mock_storage):
    """Tests adding a new order with default 'pending' status."""
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")
    
    # We expect save_order to be called once
    mock_storage.save_order.assert_called_once()


def test_add_order_raises_error_if_exists(order_tracker,mock_storage):
    """Tests that adding an order with a duplicate ID raises a ValueError."""
    # Simulate that the storage finds an existing order
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}
    with pytest.raises(ValueError,match="Order with ID 'ORD_EXISTING' already exists."):
        order_tracker.add_order("ORD_EXISTING","New item",1,"CUST001")


def test_get_order_by_id_found(order_tracker, mock_storage):
    """Returns the order dict when the order exists."""
    expected = {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    }
    mock_storage.get_order.return_value = expected

    result = order_tracker.get_order_by_id("ORD001")

    assert result == expected
    mock_storage.get_order.assert_called_once_with("ORD001")

def test_get_order_by_id_not_found(order_tracker, mock_storage):
    """Returns None when the order does not exist."""
    mock_storage.get_order.return_value = None  # (this is the fixture default)

    result = order_tracker.get_order_by_id("NONEXISTENT")

    assert result is None
    mock_storage.get_order.assert_called_once_with("NONEXISTENT")


# --- update_order_status ---

def test_update_order_status_changes_status(order_tracker, mock_storage):
    """Changes an existing order's status (e.g. 'pending' -> 'shipped')."""
    existing = {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    }
    mock_storage.get_order.return_value = existing

    result = order_tracker.update_order_status("ORD001", "shipped")

    # The returned order reflects the new status
    assert result["status"] == "shipped"
    # The updated order is persisted back to storage
    mock_storage.save_order.assert_called_once_with("ORD001", existing)
    assert mock_storage.save_order.call_args[0][1]["status"] == "shipped"


def test_update_order_status_raises_error_if_not_found(order_tracker, mock_storage):
    """Raises ValueError when updating an order that does not exist."""
    mock_storage.get_order.return_value = None  # (fixture default)

    with pytest.raises(ValueError, match="Order with ID 'NONEXISTENT' not found."):
        order_tracker.update_order_status("NONEXISTENT", "shipped")

    # Nothing should be saved when the order is missing
    mock_storage.save_order.assert_not_called()


# --- list_all_orders ---

def test_list_all_orders_returns_all(order_tracker, mock_storage):
    """Returns a list of all current orders."""
    orders = {
        "ORD001": {"order_id": "ORD001", "item_name": "Laptop", "quantity": 1,
                   "customer_id": "C1", "status": "pending"},
        "ORD002": {"order_id": "ORD002", "item_name": "Mouse", "quantity": 2,
                   "customer_id": "C2", "status": "shipped"},
    }
    mock_storage.get_all_orders.return_value = orders

    result = order_tracker.list_all_orders()

    assert isinstance(result, list)
    assert len(result) == 2
    assert orders["ORD001"] in result
    assert orders["ORD002"] in result


def test_list_all_orders_empty(order_tracker, mock_storage):
    """Returns an empty list when there are no orders."""
    mock_storage.get_all_orders.return_value = {}  # (fixture default)

    result = order_tracker.list_all_orders()

    assert result == []


# --- list_orders_by_status ---

def test_list_orders_by_status_filters_matching(order_tracker, mock_storage):
    """Returns only the orders whose status matches the requested one."""
    orders = {
        "ORD001": {"order_id": "ORD001", "status": "pending"},
        "ORD002": {"order_id": "ORD002", "status": "shipped"},
        "ORD003": {"order_id": "ORD003", "status": "shipped"},
    }
    mock_storage.get_all_orders.return_value = orders

    result = order_tracker.list_orders_by_status("shipped")

    assert len(result) == 2
    returned_ids = {order["order_id"] for order in result}
    assert returned_ids == {"ORD002", "ORD003"}
    assert all(order["status"] == "shipped" for order in result)


def test_list_orders_by_status_no_match(order_tracker, mock_storage):
    """Returns an empty list when no order has the requested status."""
    orders = {
        "ORD001": {"order_id": "ORD001", "status": "pending"},
    }
    mock_storage.get_all_orders.return_value = orders

    result = order_tracker.list_orders_by_status("delivered")

    assert result == []
