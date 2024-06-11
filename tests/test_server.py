import os
import shutil
import tempfile
from fastapi.testclient import TestClient
from server import app, verify_token, PHOTO_PATH  # Assuming your FastAPI app is in `main.py`

client = TestClient(app)

# Create a temporary directory for storing test photos
temp_dir = tempfile.mkdtemp()
app.dependency_overrides[PHOTO_PATH] = lambda: temp_dir


# Mock token verification
def mock_verify_token(request):
    pass  # Mock function does nothing, just to bypass actual token check

app.dependency_overrides[verify_token] = mock_verify_token


def test_get_all_users():
    response = client.get('/api/users/')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_user():
    user_id = 1  # Replace with an actual user ID present in your test database
    response = client.get(f'/api/users/{user_id}')
    assert response.status_code == 200
    assert response.json()['id'] == user_id


def test_get_users_by_name():
    pattern = "John"  # Replace with an actual name pattern present in your test database
    response = client.get(f'/api/users/name/{pattern}')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_add_user():
    new_user = {
        "id": 2,  # Ensure this ID is not already in the test database
        "name": "Test User",
        "email": "test@example.com"
    }
    response = client.post('/api/users/', json=new_user)
    assert response.status_code == 200
    assert response.json()['id'] == new_user['id']


def test_update_user():
    update_user = {
        "id": 2,  # Ensure this ID is already in the test database
        "name": "Updated Test User",
        "email": "updated@example.com"
    }
    response = client.put('/api/users/', json=update_user)
    assert response.status_code == 200
    assert response.json()['name'] == update_user['name']


def test_delete_user():
    user_id = 2  # Ensure this ID is already in the test database
    response = client.delete(f'/api/users/{user_id}')
    assert response.status_code == 200
    assert response.json()['id'] == user_id


def test_get_all_employers():
    response = client.get('/api/employers/')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_employer():
    employer_id = 1  # Replace with an actual employer ID present in your test database
    response = client.get(f'/api/employers/{employer_id}')
    assert response.status_code == 200
    assert response.json()['id'] == employer_id


def test_get_employers_by_name():
    pattern = "Acme Corp"  # Replace with an actual employer name pattern present in your test database
    response = client.get(f'/api/employers/name/{pattern}')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_photo():
    file_name = "test_photo.jpg"
    file_path = os.path.join(temp_dir, file_name)
    with open(file_path, "wb") as f:
        f.write(b"test image data")

    response = client.get(f'/api/photo/{file_name}')
    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/jpeg'


def test_upload_photo():
    file_name = "upload_test_photo.jpg"
    file_path = os.path.join(temp_dir, file_name)
    with open(file_path, "wb") as f:
        f.write(b"test image data")

    with open(file_path, "rb") as f:
        response = client.post('/api/photo/', files={"photo": (file_name, f, "image/jpeg")})
    assert response.status_code == 200
    assert response.json()['filename'] == file_name


def test_get_order():
    order_id = 1  # Replace with an actual order ID present in your test database
    response = client.get(f'/api/orders/{order_id}')
    assert response.status_code == 200
    assert response.json()['id'] == order_id


def test_get_orders_all():
    response = client.get('/api/orders/')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_add_order():
    new_order = {
        "status": "Active",
        "employer_name": "Test Employer"
    }
    response = client.post('/api/orders/', json=new_order)
    assert response.status_code == 200
    assert response.json()['employer_name'] == new_order['employer_name']

# Clean up the temporary directory after the tests
def teardown_module(module):
    shutil.rmtree(temp_dir)
