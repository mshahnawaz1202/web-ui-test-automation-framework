@profile
Feature: Profile management

  @BDD-015
  Scenario: An authenticated user views profile details
    Given the user is logged in and has a profile created by the post-save signal
    When the user opens "/profile/"
    Then the profile image, username, and email are visible
    And the correct authenticated user's details are displayed

  @BDD-016
  Scenario: Anonymous visitors cannot view profile
    Given the visitor is not logged in
    When the visitor requests "/profile/"
    Then the visitor is redirected to login
    And no profile is displayed
