from contextlib import contextmanager
import re
import sqlite3

import pytest

from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats
)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test


######################################################
#
#    Add and delete
#
######################################################

def test_create_meal(mock_cursor):
    """Test creating a new meal in the db."""

    # Call the function to create a new song
    create_meal(meal="Meal Name", cuisine="Meal Cuisine", price=5.50, difficulty="HARD")

    expected_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
                VALUES (?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Meal Name", "Meal Cuisine", 5.50, "HARD")
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_meal_duplicate(mock_cursor):
    """Test creating a song with a duplicate artist, title, and year (should raise an error)."""

    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: meal.meal")

    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError
    with pytest.raises(ValueError, match="Song with artist 'Meal Name' already exists."):
        create_meal(meal="Meal Name", cuisine="Meal Cuisine", price=5.50, difficulty="HARD")

def test_create_meal_invalid_price():
    """Test error when trying to create a song with an invalid duration (e.g., negative duration)"""

    # Attempt to create a song with a negative duration
    with pytest.raises(ValueError, match="Invalid meal price: -10 \(must be a positive float\)."):
        create_meal(meal="Meal Name", cuisine="Meal Cuisine", price=-10, difficulty="HARD")


def test_create_meal_invalid_difficulty():
    """Test error when trying to create a song with an invalid duration (e.g., negative duration)"""

    # Attempt to create a song with a negative duration
    with pytest.raises(ValueError, match="Invalid meal difficulty: 'not bad' \(Must be 'LOW', 'MED', or 'HIGH'.\)."):
        create_meal(meal="Meal Name", cuisine="Meal Cuisine", price=5.50, difficulty="not bad")

