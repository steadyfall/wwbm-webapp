from auth.validate import (
    confirmPassword,
    emailValidator,
    passwordValidator,
    usernameValidator,
)


class TestUsernameValidator:
    def test_valid_alphanumeric(self):
        assert usernameValidator("john123") is True

    def test_valid_special_chars(self):
        assert usernameValidator("john.doe@test+user-name") is True

    def test_disallowed_char(self):
        assert usernameValidator("john!") is False

    def test_empty_string(self):
        assert usernameValidator("") is False

    def test_150_chars_rejected(self):
        assert usernameValidator("a" * 150) is False

    def test_149_chars_boundary(self):
        assert usernameValidator("a" * 149) is True


class TestEmailValidator:
    def test_valid_email(self):
        assert emailValidator("user@example.com") is True

    def test_no_at_sign(self):
        assert emailValidator("userexample.com") is False

    def test_no_domain(self):
        assert emailValidator("user@") is False

    def test_space_in_email(self):
        assert emailValidator("user @example.com") is False


class TestPasswordValidator:
    def test_valid(self):
        assert passwordValidator("john", "securePass1") is True

    def test_too_short(self):
        assert passwordValidator("john", "abc1A") is False

    def test_all_numeric(self):
        assert passwordValidator("john", "12345678") is False

    def test_contains_username(self):
        assert passwordValidator("john", "johnsmith1") is False

    def test_empty_username(self):
        assert passwordValidator("", "securePass1") is False


class TestConfirmPassword:
    def test_matching_valid_passwords(self):
        assert confirmPassword("john", "securePass1", "securePass1") is True

    def test_mismatched_passwords(self):
        assert confirmPassword("john", "securePass1", "otherPass1") is False

    def test_password2_fails_validation(self):
        assert confirmPassword("john", "securePass1", "abc") is False
