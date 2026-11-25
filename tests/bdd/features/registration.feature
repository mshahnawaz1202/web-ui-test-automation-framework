@registration
Feature: User registration

  @BDD-001
  Scenario: A visitor registers with valid details
    Given the visitor is on "/register/"
    When the visitor enters a unique username, a valid email, and matching strong passwords, then selects Sign Up
    Then a user account is created and the visitor is redirected to "/login/"
    And the login page displays the registration success message

  @BDD-002
  Scenario: Registration rejects an existing username
    Given a user with the username "existing" already exists
    And the visitor is on "/register/"
    When the visitor submits the existing username with otherwise valid data
    Then registration remains on the page and reports a duplicate username
    And no additional user is created

  @BDD-003
  Scenario: Registration rejects password mismatch
    Given the visitor is on "/register/"
    When the visitor enters two different passwords and submits
    Then registration remains on the page and highlights the password2 field
    And no account is created

  @BDD-004
  Scenario Outline: Registration validates email format
    Given the visitor is on "/register/"
    When the visitor submits the email "<email>" with otherwise valid data
    Then registration remains on the page and shows an email validation error
    And no account is created

    Examples:
      | email        |
      |              |
      | not-an-email |
