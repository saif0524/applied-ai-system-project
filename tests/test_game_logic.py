from logic_utils import check_guess, update_score

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result[0] == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result[0] == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result[0] == "Too Low"


def test_update_score_win():
    # IF win in the 3rd attempt, the score should be 70
    result = update_score(50, "Win", 3)
    assert result == 110
 
def test_update_score_too_high():
    result = update_score(50, "Too High", 2)
    assert result == 45
 
