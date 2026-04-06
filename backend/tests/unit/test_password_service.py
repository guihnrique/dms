"""
Unit tests for PasswordService - Task 2.1, 2.2, 2.3
Tests verify bcrypt password hashing and verification
"""
import pytest
import time
from app.services.password_service import PasswordService


def test_hash_password_with_bcrypt_cost_12():
    """
    RED PHASE: Test password hashing with bcrypt cost factor 12
    Requirements: 1.3, 6.1, 6.2
    """
    service = PasswordService()
    password = "SecurePassword123!"

    # Hash the password
    hashed = service.hash_password(password)

    # Verify it's a bcrypt hash (starts with $2b$)
    assert hashed.startswith("$2b$"), "Hash should be bcrypt format"

    # Verify cost factor is 12 (bcrypt format: $2b$12$...)
    cost_factor = int(hashed.split("$")[2])
    assert cost_factor == 12, f"Cost factor should be 12, got {cost_factor}"

    # Verify hash is not the plain password
    assert hashed != password, "Hash should not equal plain password"


def test_hash_password_generates_different_hashes_for_same_password():
    """
    RED PHASE: Test that same password generates different hashes (random salt)
    Requirements: 6.1
    """
    service = PasswordService()
    password = "SamePassword123!"

    # Hash same password twice
    hash1 = service.hash_password(password)
    hash2 = service.hash_password(password)

    # Hashes should be different due to random salt
    assert hash1 != hash2, "Same password should generate different hashes (random salt)"

    # But both should be valid bcrypt hashes
    assert hash1.startswith("$2b$")
    assert hash2.startswith("$2b$")


def test_hash_password_performance():
    """
    RED PHASE: Test that hashing takes approximately 250ms
    Requirements: 6.1
    """
    service = PasswordService()
    password = "PerformanceTest123!"

    # Measure hash time
    start = time.time()
    service.hash_password(password)
    elapsed = time.time() - start

    # Should take approximately 250ms (allow 50ms-1000ms range)
    assert 0.05 < elapsed < 1.0, \
        f"Hash time should be ~250ms, got {elapsed*1000:.0f}ms"

    print(f"  ℹ️  Hash time: {elapsed*1000:.0f}ms")


def test_hash_password_handles_various_characters():
    """
    RED PHASE: Test hashing with special characters
    Requirements: 1.3
    """
    service = PasswordService()

    # Test various password types
    passwords = [
        "Simple123",
        "With Space 123!",
        "Special!@#$%^&*()",
        "Unicode🔒Password",
        "Very" * 50  # Long password
    ]

    for pwd in passwords:
        hashed = service.hash_password(pwd)
        assert hashed.startswith("$2b$"), f"Failed to hash: {pwd[:20]}"


def test_verify_password_accepts_correct_password():
    """
    RED PHASE: Test password verification with correct password
    Requirements: 2.1, 6.3 (Task 2.2)
    """
    service = PasswordService()
    password = "CorrectPassword123!"

    # Hash the password
    hashed = service.hash_password(password)

    # Verify with correct password
    is_valid = service.verify_password(password, hashed)

    assert is_valid is True, "Correct password should verify successfully"


def test_verify_password_rejects_incorrect_password():
    """
    RED PHASE: Test password verification with wrong password
    Requirements: 2.1, 6.3 (Task 2.2)
    """
    service = PasswordService()
    correct_password = "CorrectPassword123!"
    wrong_password = "WrongPassword123!"

    # Hash the correct password
    hashed = service.hash_password(correct_password)

    # Verify with wrong password
    is_valid = service.verify_password(wrong_password, hashed)

    assert is_valid is False, "Wrong password should not verify"


def test_verify_password_timing_attack_resistance():
    """
    RED PHASE: Test that verification time is constant (timing-attack safe)
    Requirements: 6.3 (Task 2.2)
    """
    service = PasswordService()
    password = "TimingTest123!"
    hashed = service.hash_password(password)

    # Time correct password verification
    start = time.time()
    service.verify_password(password, hashed)
    correct_time = time.time() - start

    # Time incorrect password verification
    start = time.time()
    service.verify_password("WrongPassword123!", hashed)
    incorrect_time = time.time() - start

    # Times should be similar (within 50ms) for timing-attack resistance
    time_diff = abs(correct_time - incorrect_time)
    assert time_diff < 0.05, \
        f"Timing difference too large: {time_diff*1000:.0f}ms (timing attack risk)"

    print(f"  ℹ️  Timing difference: {time_diff*1000:.1f}ms (safe)")


def test_hash_password_never_returns_plain_password():
    """
    RED PHASE: Ensure plain password never leaked
    Requirements: 6.4
    """
    service = PasswordService()
    password = "SecretPassword123!"

    hashed = service.hash_password(password)

    # Hash should not contain the plain password
    assert password not in hashed, "Hashed value should not contain plain password"
    assert len(hashed) > len(password), "Hash should be longer than password"


def test_hash_password_rejects_empty_password():
    """
    GREEN PHASE: Test error handling for empty password
    Requirements: 6.1
    """
    service = PasswordService()

    with pytest.raises(ValueError, match="Password cannot be empty"):
        service.hash_password("")


def test_verify_password_handles_empty_inputs():
    """
    GREEN PHASE: Test verify_password with empty inputs
    Requirements: 6.3
    """
    service = PasswordService()
    hashed = service.hash_password("ValidPassword123!")

    # Empty plain password
    assert service.verify_password("", hashed) is False

    # Empty hash
    assert service.verify_password("ValidPassword123!", "") is False

    # Both empty
    assert service.verify_password("", "") is False


def test_verify_password_handles_invalid_hash_format():
    """
    GREEN PHASE: Test verify_password with invalid hash
    Requirements: 6.3
    """
    service = PasswordService()

    # Invalid hash format should return False, not raise exception
    assert service.verify_password("password", "invalid_hash") is False
    assert service.verify_password("password", "not_a_bcrypt_hash") is False


def test_password_service_cost_factor_validation():
    """
    GREEN PHASE: Test cost factor validation
    Requirements: 6.2
    """
    # Cost factor 12 should work
    service = PasswordService(cost_factor=12)
    assert service.cost_factor == 12

    # Cost factor below 12 should raise error
    with pytest.raises(ValueError, match="Cost factor must be at least 12"):
        PasswordService(cost_factor=10)
