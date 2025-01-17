import pytest
from sqlalchemy.exc import SQLAlchemyError
from backend.services.cart_service import CartService
from backend.models.schemas.cart import CartItemCreate, CartItemUpdate

def test_get_or_create_cart(db_session, test_user):
    service = CartService(db_session)
    cart = service.get_or_create_cart(test_user.id)
    assert cart.user_id == test_user.id
    
    # Test getting existing cart
    same_cart = service.get_or_create_cart(test_user.id)
    assert same_cart.id == cart.id

def test_add_item_to_cart(db_session, test_user, sample_menu_item):
    service = CartService(db_session)
    item_data = CartItemCreate(
        menu_item_id=sample_menu_item.id,
        quantity=2,
        customizations={"notes": "Extra spicy"}
    )
    
    cart = service.add_item(test_user.id, item_data)
    cart_item = next(item for item in cart.items if item.menu_item_id == sample_menu_item.id)
    assert cart_item.menu_item_id == sample_menu_item.id
    assert cart_item.quantity == 2
    assert cart_item.customizations == {"notes": "Extra spicy"}

def test_add_existing_item_to_cart(db_session, test_user, sample_menu_item):
    service = CartService(db_session)
    item_data = CartItemCreate(
        menu_item_id=sample_menu_item.id,
        quantity=2,
        customizations={"notes": "Extra spicy"}
    )
    
    service.add_item(test_user.id, item_data)
    
    # Add same item again
    item_data.quantity = 3
    item_data.customizations = {"notes": "Very spicy"}
    cart = service.add_item(test_user.id, item_data)
    cart_item = next(item for item in cart.items if item.menu_item_id == sample_menu_item.id)
    
    assert cart_item.quantity == 5  # 2 + 3
    assert cart_item.customizations == {"notes": "Very spicy"}

def test_add_invalid_menu_item(db_session, test_user):
    service = CartService(db_session)
    item_data = CartItemCreate(
        menu_item_id=999,  # Non-existent menu item
        quantity=1
    )
    
    with pytest.raises(ValueError, match="Menu item .* not found"):
        service.add_item(test_user.id, item_data)

def test_add_unavailable_menu_item(db_session, test_user, sample_menu_item):
    sample_menu_item.is_available = False
    db_session.commit()
    
    service = CartService(db_session)
    item_data = CartItemCreate(
        menu_item_id=sample_menu_item.id,
        quantity=1
    )
    
    with pytest.raises(ValueError, match="Menu item .* is not available"):
        service.add_item(test_user.id, item_data)

def test_update_cart_item(db_session, test_user, sample_menu_item):
    service = CartService(db_session)
    item_data = CartItemCreate(
        menu_item_id=sample_menu_item.id,
        quantity=2
    )
    
    cart = service.add_item(test_user.id, item_data)
    cart_item = cart.items[0]
    
    update_data = CartItemUpdate(
        quantity=3,
        customizations={"notes": "Less spicy"}
    )
    
    updated_cart = service.update_item(test_user.id, cart_item.id, update_data)
    updated_item = next(item for item in updated_cart.items if item.id == cart_item.id)
    assert updated_item.quantity == 3
    assert updated_item.customizations == {"notes": "Less spicy"}

def test_update_nonexistent_cart_item(db_session, test_user):
    service = CartService(db_session)
    update_data = CartItemUpdate(quantity=1)
    
    with pytest.raises(ValueError, match="Cart item .* not found"):
        service.update_item(test_user.id, 999, update_data)

def test_update_cart_item_zero_quantity(db_session, test_user, sample_menu_item):
    service = CartService(db_session)
    item_data = CartItemCreate(
        menu_item_id=sample_menu_item.id,
        quantity=2
    )
    
    cart = service.add_item(test_user.id, item_data)
    cart_item = cart.items[0]
    
    update_data = CartItemUpdate(quantity=0)
    updated_cart = service.update_item(test_user.id, cart_item.id, update_data)
    assert len(updated_cart.items) == 0

def test_remove_item_from_cart(db_session, test_user, sample_menu_item):
    service = CartService(db_session)
    item_data = CartItemCreate(
        menu_item_id=sample_menu_item.id,
        quantity=2
    )
    
    cart = service.add_item(test_user.id, item_data)
    cart_item = cart.items[0]
    
    updated_cart = service.remove_item(test_user.id, cart_item.id)
    assert len(updated_cart.items) == 0

def test_remove_nonexistent_cart_item(db_session, test_user):
    service = CartService(db_session)
    with pytest.raises(ValueError, match="Cart item .* not found"):
        service.remove_item(test_user.id, 999)

def test_clear_cart(db_session, test_user, sample_menu_item):
    service = CartService(db_session)
    item_data1 = CartItemCreate(
        menu_item_id=sample_menu_item.id,
        quantity=2
    )
    item_data2 = CartItemCreate(
        menu_item_id=sample_menu_item.id,
        quantity=1
    )
    
    service.add_item(test_user.id, item_data1)
    service.add_item(test_user.id, item_data2)
    
    cart = service.clear_cart(test_user.id)
    assert len(cart.items) == 0

def test_calculate_total(db_session, test_user, sample_menu_item):
    service = CartService(db_session)
    item_data = CartItemCreate(
        menu_item_id=sample_menu_item.id,
        quantity=2
    )
    
    service.add_item(test_user.id, item_data)
    total = service.calculate_total(test_user.id)
    assert total == sample_menu_item.price * 2

def test_database_error_handling(db_session, test_user):
    service = CartService(db_session)
    
    # Force a database error by expiring and closing the session
    db_session.expire_all()
    db_session.bind.dispose()
    db_session.close()
    
    with pytest.raises(SQLAlchemyError):
        service.get_or_create_cart(test_user.id)
