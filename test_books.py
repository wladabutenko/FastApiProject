from fastapi.testclient import TestClient

import books
import models
from database import SessionLocal


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


books.app.dependency_overrides[books.get_db] = override_get_db
client = TestClient(books.app)


def test_read_api():
    # Create a test book in the database
    db = SessionLocal()
    book = models.Books(title="Test Book", author="Test Author", description="Test description", rating=50)
    db.add(book)
    db.commit()
    db.refresh(book)

    # Call the read_api endpoint
    response = client.get("/")
    assert response.status_code == 200

    # Check that the test book is in the response for the first created book
    # assert len(response.json()) == 1
    # assert response.json()[0]["title"] == "Test Book"
    # assert response.json()[0]["author"] == "Test Author"
    # assert response.json()[0]["description"] == "Test description"
    # assert response.json()[0]["rating"] == 50


def test_create_book_success(book_valid_data):
    # Send a POST request to the API to create the test book
    response = client.post("/", json=book_valid_data)
    # Check that the response status code is 200 OK
    assert response.status_code == 200
    # Check that the response JSON matches the expected book data
    assert response.json() == book_valid_data


def test_create_book_with_failure(book_invalid_data):
    response = client.post("/", json=book_invalid_data)

    assert response.status_code == 422
    assert response.json() == {
      "detail": [
        {
          "loc": [
            "body",
            "author"
          ],
          "msg": "ensure this value has at most 100 characters",
          "type": "value_error.any_str.max_length",
          "ctx": {
            "limit_value": 100
          }
        },
        {
          "loc": [
            "body",
            "description"
          ],
          "msg": "ensure this value has at most 100 characters",
          "type": "value_error.any_str.max_length",
          "ctx": {
            "limit_value": 100
          }
        },
        {
          "loc": [
            "body",
            "rating"
          ],
          "msg": "ensure this value is less than 101",
          "type": "value_error.number.not_lt",
          "ctx": {
            "limit_value": 101
          }
         }
       ]
    }


def test_update_book_success(new_book_data):

    db = SessionLocal()
    book = models.Books(title="Test Book", author="Test Author", description="Test description", rating=50)
    db.add(book)
    db.commit()
    db.refresh(book)

    response = client.put(f"/{book.id}", json=new_book_data)
    assert response.status_code == 200

    # Retrieve the updated book from the database
    db.refresh(book)

    # Check that the book was updated correctly
    assert book.title == "Updated Book"
    assert book.author == "Updated Author"
    assert book.description == "Updated description"
    assert book.rating == 70


def test_update_book_failure(new_book_data):

    db = SessionLocal()
    book = models.Books(title="Test Book", author="Test Author", description="Test description", rating=50)
    db.add(book)
    db.commit()
    db.refresh(book)

    response = client.put(f"/{book.id + 1}", json=new_book_data)
    assert response.status_code == 404

    assert response.json() == {"detail": f"ID {book.id + 1}: Does not exist"}


def test_delete_book():
    # create a test book
    db = SessionLocal()
    book = models.Books(title="Test Book", author="Test Author", description="Test Description", rating=3)
    db.add(book)
    db.commit()

    # delete the book using the delete endpoint
    response = client.delete(f"/{book.id}")

    # check that the response has a 200 status code
    assert response.status_code == 200

    # check that the book has actually been deleted from the database
    deleted_book_model = db.query(models.Books).filter(models.Books.id == book.id).first()
    assert deleted_book_model is None


def test_delete_nonexistent_book():
    # Attempt to delete a non-existent book
    response = client.delete("/100")
    assert response.status_code == 404
