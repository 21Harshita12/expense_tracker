import database as db
import auth
import ml_utils

def test_full_flow():
    print("Initializing test database...")
    db.init_db()
    
    # 1. Test user operations
    print("Testing user registration and auth...")
    
    # Test validator
    is_ok, msg = auth.validate_password_strength("weak")
    assert is_ok is False
    assert "at least 8" in msg
    
    is_ok, msg = auth.validate_password_strength("weakpassword123")
    assert is_ok is False
    assert "uppercase" in msg
    
    is_ok, msg = auth.validate_password_strength("WEAKPASSWORD123")
    assert is_ok is False
    assert "lowercase" in msg
    
    is_ok, msg = auth.validate_password_strength("WeakPassword")
    assert is_ok is False
    assert "number" in msg
    
    is_ok, msg = auth.validate_password_strength("WeakPassword123")
    assert is_ok is False
    assert "special character" in msg
    
    # Strong password
    username = "test_verify_user"
    password = "Secure_Password_123!"
    is_ok, msg = auth.validate_password_strength(password)
    assert is_ok is True
    
    # Hash password
    pwd_hash = auth.hash_password(password)
    assert pwd_hash is not None
    assert pwd_hash != password
    
    # Register
    user_id = db.add_user(username, pwd_hash)
    if user_id is None:
        user = db.get_user_by_username(username)
        assert user is not None
        user_id = user["id"]
        print(f"User already exists. User ID: {user_id}")
    else:
        print(f"Successfully registered user. User ID: {user_id}")
        
    assert auth.check_password(password, pwd_hash) == True
    assert auth.check_password("wrong_password", pwd_hash) == False
    
    # 2. Test Mock Data Generation
    print("Testing 6-month mock data generation...")
    db.generate_mock_data(user_id)
    print("Mock data generated successfully!")
    
    df_inc = db.get_incomes(user_id)
    print(f"Total income records generated: {len(df_inc)}")
    assert len(df_inc) > 0
    
    df_exp = db.get_expenses(user_id)
    print(f"Total expense records generated: {len(df_exp)}")
    assert len(df_exp) > 0
    
    budgets = db.get_budgets(user_id)
    print(f"Set category budgets: {budgets}")
    assert len(budgets) > 0
    
    df_goals = db.get_savings_goals(user_id)
    print(f"Active savings goals count: {len(df_goals)}")
    assert len(df_goals) > 0
    
    df_bud = db.get_expenses_vs_budget(user_id)
    print("Current month budget utilization table:")
    print(df_bud)
    assert not df_bud.empty
    
    # 3. Test Machine Learning forecasting
    print("Testing ML forecasting using scikit-learn Linear Regression...")
    forecast = ml_utils.forecast_expenses(df_exp, months_to_predict=3)
    
    assert forecast["status"] == "success", f"Forecast failed: {forecast.get('message')}"
    print("Forecast succeeded!")
    print("Forecasted future months:")
    print(forecast["predictions"])
    print("Model metrics:")
    print(forecast["metrics"])
    
    assert len(forecast["predictions"]) == 3
    assert forecast["metrics"]["average_expense"] > 0
    
    # Test daily forecasting
    print("Testing ML daily forecasting...")
    forecast_daily = ml_utils.forecast_expenses_daily(df_exp, days_to_predict=10)
    assert forecast_daily["status"] == "success", f"Daily forecast failed: {forecast_daily.get('message')}"
    print("Daily forecast succeeded!")
    print("Forecasted future days (first 3):")
    print(forecast_daily["predictions"].head(3))
    print("Daily model metrics:")
    print(forecast_daily["metrics"])
    
    assert len(forecast_daily["predictions"]) == 10
    
    print("\n[SUCCESS] ALL BACKEND AND MACHINE LEARNING TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_full_flow()
