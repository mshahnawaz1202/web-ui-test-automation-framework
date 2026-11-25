@authentication
Feature: Authentication

  @BDD-005
  Scenario: A registered user logs in
    Given a registered user "alice" exists
    And the registered user is on "/login/"
    When the user enters the correct username and password and selects Login
    Then the session is authenticated and the browser redirects to "/"
    And authenticated navigation replaces Login/Register with Profile/Create Post/Logout

  @BDD-006
  Scenario Outline: Login rejects incorrect credentials
    Given a registered user "alice" exists
    And a user is on "/login/"
    When the user enters the username "<username>" and password "<password>" and selects Login
    Then the login page remains visible and an authentication error is shown
    And no authenticated session is created

    Examples:
      | username | password           |
      | alice    | WrongPassword!2345 |
      | unknown  | StrongPass!2345    |

  @BDD-007
  Scenario: An authenticated user logs out
    Given the user is authenticated
    And the user uses the Logout navigation link
    When Django processes logout
    Then the session is cleared and "/logout/" shows the logged-out message
    And Login/Register links replace the authenticated navigation links
