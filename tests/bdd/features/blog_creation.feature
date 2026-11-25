@blog_creation
Feature: Blog creation

  @BDD-012
  Scenario: An authenticated user creates a valid post
    Given the user is logged in
    And the user is on "/create-post/"
    When the user enters a valid title and content and selects Save
    Then one post is created for the logged-in author and the browser redirects to "/"
    And the new post appears on the home listing and a success message is visible

  @BDD-013
  Scenario: Anonymous visitors cannot create posts
    Given the visitor is not logged in
    When the visitor requests "/create-post/"
    Then the visitor is redirected to login with a next parameter
    And no post is created and the protected page is not displayed

  @BDD-014
  Scenario Outline: Post creation rejects empty or overlong values
    Given the user is authenticated
    And the user is on "/create-post/"
    When the user submits the title "<title>" and content "<content>" and selects Save
    Then the form remains on the page and shows the relevant validation errors
    And no invalid post is persisted

    Examples:
      | title                                                                                                 | content |
      |                                                                                                       | Content |
      | Valid title                                                                                           |         |
      | TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT | Content |
