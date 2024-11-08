#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


##########################################################
#
# Meal Management
#
##########################################################

clear_catalog() {
  echo "Clearing the db..."
  curl -s -X DELETE "$BASE_URL/clear-meals" | grep -q '"status": "success"'
}

create_meal() {
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$4
 
  echo "Adding meal ($meal) ..."
  curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}"

  if [ $? -eq 0 ]; then
    echo "Meal added successfully."
  else
    echo "Failed to add meal."
    exit 1
  fi
}

delete_meal_by_id() {
  meal_id=$1

  echo "Deleting song by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-from-kitchen-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (ID $meal_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get mean by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_name() {
  meal=$1

  echo "Getting meal by meal name (Meal: '$meal')..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-from-kitchen-by-name?meal=$(echo $meal | sed 's/ /%20/g')")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by compound key."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (by name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get song by name."
    exit 1
  fi
}


############################################################
#
# Battle Setup Management
#
############################################################

prep_combatant() {
  meal=$1

  echo "Adding meal as combatant: $meal ..."
  response=$(curl -s -X POST "$BASE_URL/prep-combatant" \
    -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal added to combatant list successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to add meal to combatants"
    exit 1
  fi
}

get_combatants() {
  echo "Retrieving current song..."
  response=$(curl -s -X GET "$BASE_URL/get-combatants")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Current Combatants JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve combatants."
    exit 1
  fi
}

clear_combatants() {
  echo "Clearing combatants..."
  response=$(curl -s -X POST "$BASE_URL/clear-combatants")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants cleared successfully."
  else
    echo "Failed to clear combatants."
    exit 1
  fi
}

############################################################
#
# Battle
#
############################################################

battle() {
  echo "Executing a battle..."
  response=$(curl -s -X POST "$BASE_URL/battle")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Battle finished."
  else
    echo "Failed to battle."
    exit 1
  fi
}


######################################################
#
# Leaderboard
#
######################################################

# Function to get the song leaderboard sorted by wins
get_meal_leaderboard_wins() {
  echo "Getting meal leaderboard sorted by wins..."
  response=$(curl -s -X GET "$BASE_URL/meal-leaderboard?sort=wins")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by wins):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal leaderboard."
    exit 1
  fi
}

# Function to get the song leaderboard sorted by win_pct
get_meal_leaderboard_win_pct() {
  echo "Getting meal leaderboard sorted by win_pct..."
  response=$(curl -s -X GET "$BASE_URL/meal-leaderboard?sort=win_pct")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by wins):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal leaderboard."
    exit 1
  fi
}


# Health checks
check_health
check_db

# Clear the catalog
clear_catalog

# Create meals
create_meal "Pizza" "Italian" 15.99 "MED" 
create_meal "Tacos" "Mexican" 10.50 "LOW"
create_meal "Sushi" "Japanese" 12.00 "HIGH"
create_meal "Pho" "Vietnamese" 19.99 "MED"
create_meal "Pancakes" "American" 5.99 "MED"

delete_meal_by_id 1

get_meal_by_id 2
get_meal_by_name "Pho" 

prep_combatant "Tacos" 
prep_combatant "Sushi" 
battle
clear_combatants
prep_combatant "Pho" 
prep_combatant "Pancakes"
get_combatants
battle

get_meal_leaderboard_wins
get_meal_leaderboard_win_pct

echo "All tests passed successfully!"
