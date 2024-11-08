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
    create_meal(meal="Meal Name", cuisine="Meal Cuisine", price=5.50, difficulty="HIGH")

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
    expected_arguments = ("Meal Name", "Meal Cuisine", 5.50, "HIGH")
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_meal_duplicate(mock_cursor):
    """Test creating a song with a duplicate artist, title, and year (should raise an error)."""

    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: meal.meal")

    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError
    with pytest.raises(ValueError, match="Song with artist 'Meal Name' already exists."):
        create_meal(meal="Meal Name", cuisine="Meal Cuisine", price=5.50, difficulty="HIGH")

def test_create_meal_invalid_price():
    """Test error when trying to create a song with an invalid duration (e.g., negative duration)"""

    # Attempt to create a meal with a negative price or not a float
    with pytest.raises(ValueError, match="Invalid price: -10 \(Price must be a positive number\)."):
        create_meal(meal="Meal Name", cuisine="Meal Cuisine", price=-10, difficulty="HIGH")
    with pytest.raises(ValueError, match="Invalid price: ten \(Price must be a positive number\)."):
        create_meal(meal="Meal Name", cuisine="Meal Cuisine", price="ten", difficulty="HIGH")



def test_create_meal_invalid_difficulty():
    """Test error when trying to create a meal with an invalid dificulty (e.g., negative duration)"""

    # Attempt to create a song with a negative duration
    with pytest.raises(ValueError, match="Invalid meal difficulty: 'not bad' \(Must be 'LOW', 'MED', or 'HIGH'.\)."):
        create_meal(meal="Meal Name", cuisine="Meal Cuisine", price=5.50, difficulty="not bad")

def test_delete_meal(mock_cursor):
    """Test soft deleting a meal from the catalog by meal ID."""

    # Simulate that the song exists (id = 1)
    mock_cursor.fetchone.return_value = ([False])

    # Call the delete_song function
    delete_meal(1)

    # Normalize the SQL for both queries (SELECT and UPDATE)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM songs WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE songs SET deleted = TRUE WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Ensure the correct SQL queries were executed
    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."

def test_delete_meal_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent song."""

    # Simulate that no song exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent song
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)

def test_delete_meal_already_deleted(mock_cursor):
    """Test error when trying to delete a song that's already marked as deleted."""

    # Simulate that the song exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])

    # Expect a ValueError when attempting to delete a song that's already been deleted
    with pytest.raises(ValueError, match="Meal with ID 999 has already been deleted"):
        delete_meal(999)

######################################################
#
#    Get Meal
#
######################################################

def test_get_meal_by_id(mock_cursor):
    # Simulate that the song exists (id = 1)
    mock_cursor.fetchone.return_value = (1, "Meal Name", "Meal Cuisine", 5.50, "HIGH")

    # Call the function and check the result
    result = get_meal_by_id(1)

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, "Meal Name", "Meal Cuisine", 5.50, "HIGH")

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_meal_by_id_bad_id(mock_cursor):
    # Simulate that no song exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the song is not found
    with pytest.raises(ValueError, match="Song with ID 999 not found"):
        get_meal_by_id(999)

def test_get_meal_by_name(mock_cursor):
    # Simulate that the meal exists (id = 1, meal="Meal Name", cuisine="Meal Cuisine", price=5.50, difficulty="HIGH")
    mock_cursor.fetchone.return_value = (1, "Meal Name", "Meal Cuisine", 5.50, "HIGH")

    # Call the function and check the result
    result = get_meal_by_name("Meal Name")

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, "Meal Name", "Meal Cuisine", 5.50, "HIGH")

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ? ")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Meal Name")
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_leaderboard(mock_cursor):
    """Test retrieving all meals that are not marked as deleted."""

    # Simulate that there are multiple songs in the database
    mock_cursor.fetchall.return_value = [
        (1, "Meal A", "Cuisine A", 5.50, "LOW", 10, 8, False),
        (2, "Meal B", "Cuisine B", 13.50, "MED", 10, 5, False),
        (3, "Meal C", "Cuisine A", 40, "HIGH", 4, 4, False)
    ]

    # Call the get_leaderboard function
    meals = get_leaderboard("wins")

    # Ensure the results match the expected output
    expected_result = [
        {"id": 1, "meal": "Meal A", "cuisine": "Cuisine A", "price": 5.50, "difficulty": "LOW", "battles": 10, "wins": 8, "win_pct": 0.8},
        {"id": 2, "meal": "Meal B", "cuisine": "Cuisine B", "price": 13.50, "difficulty": "MED", "battles": 10, "wins": 5, "win_pct": 0.5},
        {"id": 3, "meal": "Meal C", "cuisine": "Cuisine C", "price": 40, "difficulty": "HIGH", "battles": 4, "wins": 4, "win_pct": 1}
    ]

    assert meals == expected_result, f"Expected {expected_result}, but got {meals}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0
        ORDER BY wins DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Call the get_leaderboard function with param win_pct
    meals = get_leaderboard("win_pct")

    # Ensure the results match the expected output
    expected_result = [
        {"id": 3, "meal": "Meal C", "cuisine": "Cuisine C", "price": 40, "difficulty": "HIGH", "battles": 4, "wins": 4, "win_pct": 1},
        {"id": 2, "meal": "Meal B", "cuisine": "Cuisine B", "price": 13.50, "difficulty": "MED", "battles": 10, "wins": 5, "win_pct": 0.5},
        {"id": 1, "meal": "Meal A", "cuisine": "Cuisine A", "price": 5.50, "difficulty": "LOW", "battles": 10, "wins": 8, "win_pct": 0.8}
    ]

    assert meals == expected_result, f"Expected {expected_result}, but got {meals}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0
        ORDER BY win_pct DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_update_meal_stats_win(mock_cursor):
    """Test updating the stats of a meal with a win."""

    # Simulate that the song exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_play_count function with a sample song ID
    meal_id = 1
    update_meal_stats(meal_id, "win")

    # Normalize the expected SQL query
    expected_query = normalize_whitespace("""
        UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?
    """)

    # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (song ID, win)
    expected_arguments = (meal_id, "win")
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_update_meal_stats_loss(mock_cursor):
    """Test updating the stats of a meal with a loss."""

    # Simulate that the song exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_play_count function with a sample song ID
    meal_id = 1
    update_meal_stats(meal_id, "loss")

    # Normalize the expected SQL query
    expected_query = normalize_whitespace("""
        UPDATE meals SET battles = battles + 1 WHERE id = ?
    """)

    # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (song ID, loss)
    expected_arguments = (meal_id, "loss")
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

### Test for Updating a Deleted Meal:
def test_update_play_count_deleted_meal(mock_cursor):
    """Test error when trying to update play count for a deleted meal."""

    # Simulate that the song exists but is marked as deleted (id = 1)
    mock_cursor.fetchone.return_value = [True]

    # Expect a ValueError when attempting to update a deleted song
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        update_meal_stats(1)

    # Ensure that no SQL query for updating play count was executed
    mock_cursor.execute.assert_called_once_with("SELECT deleted FROM meals WHERE id = ?", (1,))
