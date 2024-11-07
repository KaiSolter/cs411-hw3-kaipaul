import pytest

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal

@pytest.fixture()
def battle_model():
    """Fixture to provide a new battle_model for each test"""
    return BattleModel()

@pytest.fixture
def mock_update_meal_stats(mocker):
    """Mock the update_meal_stats function for testing
    """
    return mocker.patch("meal_max.models.kitchen_model.update_meal_stats")

"""Fixtures providing sample meals for the tests"""
@pytest.fixture
def sample_meal1():
    return Meal(1, "Meal 1", "Cuisine 1", 15, "LOW")

@pytest.fixture
def sample_meal2():
    return Meal(2, "Meal 2", "Cuisine 2", 30, "MED")

@pytest.fixture
def sample_meal3():
    return Meal(3, "Meal 3", "Cuisine 3", 45, "HIGH")

##################################################
# Prep Combatant Test Cases
##################################################

def test_prep_combatant(battle_model, sample_meal1):
    """Test prepping a meal"""
    battle_model.prep_combatant(sample_meal1) 
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == "Meal 1"
    
def test_prep_two_combatants(battle_model, sample_meal1, sample_meal2):
    """Test prepping two meals"""
    battle_model.prep_combatant(sample_meal1) 
    battle_model.prep_combatant(sample_meal2) 
    assert len(battle_model.combatants) == 2
    assert battle_model.combatants[0].meal == "Meal 1"
    assert battle_model.combatants[1].meal == "Meal 2"
    
def test_prep_too_many_meals(battle_model, sample_meal1, sample_meal2, sample_meal3):
    """Test trying to prep three meals"""
    battle_model.prep_combatant(sample_meal1) 
    battle_model.prep_combatant(sample_meal2) 
    with pytest.raises(ValueError, match ="Combatant list is full, cannot add more combatants."):  
        battle_model.prep_combatant(sample_meal3) 

##################################################
# Clear Combatants Test Cases
##################################################

def test_clear_combatants(battle_model, sample_meal1, sample_meal2):
    """Test clearing the combatant list"""
    battle_model.combatants.extend(sample_meal1)
    battle_model.combatants.extend(sample_meal2)
    assert len(battle_model.combatants) == 2
    
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, f"Expected 0 meals, but got {len(battle_model.combatants)}"
 
##################################################
# Get Combatants Test Cases
##################################################

def test_get_combatants(battle_model, sample_meal1, sample_meal2):
    battle_model.combatants.extend(sample_meal1)
    battle_model.combatants.extend(sample_meal2)
    ret_combatants = battle_model.get_combatants()
    assert len(ret_combatants) == 2, "Expected combatant list length to be 2"
    
    combatant1 = ret_combatants[0]
    combatant2 = ret_combatants[1]
    assert combatant1.id == 1
    assert combatant2.id == 2
    assert combatant1.meal == "Meal 1"
    assert combatant2.meal == "Meal 2"
    assert combatant1.cuisine == "Cuisine 1"
    assert combatant2.cuisine == "Cuisine 2"
    assert combatant1.price == 15
    assert combatant2.price == 30
    assert combatant1.difficulty == "LOW"
    assert combatant2.difficulty == "MED"
    
##################################################
# Get Battle Score Test Cases
##################################################

def test_lowdif_battle_score(battle_model, sample_meal1):
    battle_score = battle_model.get_battle_score(sample_meal1)
    expected_battle_score = (sample_meal1.price * len(sample_meal1.cuisine)) - 3
    assert battle_score == expected_battle_score, f"Expected battle score of {expected_battle_score} but got {battle_score}"

def test_meddif_battle_score(battle_model, sample_meal2):
    battle_score = battle_model.get_battle_score(sample_meal2)
    expected_battle_score = (sample_meal2.price * len(sample_meal2.cuisine)) - 2
    assert battle_score == expected_battle_score, f"Expected battle score of {expected_battle_score} but got {battle_score}"
    
def test_highdif_battle_score(battle_model, sample_meal3):
    battle_score = battle_model.get_battle_score(sample_meal1)
    expected_battle_score = (sample_meal3.price * len(sample_meal3.cuisine)) - 1
    assert battle_score == expected_battle_score, f"Expected battle score of {expected_battle_score} but got {battle_score}"
    
    
##################################################
# Battle Test Cases
##################################################

def test_battle_lowvmeddif(battle_model, sample_meal1, sample_meal2):
    pass # todo