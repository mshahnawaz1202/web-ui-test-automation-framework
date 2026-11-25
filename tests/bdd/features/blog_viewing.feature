@blog_viewing
Feature: Blog viewing

  @BDD-008
  Scenario: A public visitor views the blog listing
    Given one or more posts exist
    When a public visitor opens "/"
    Then each post displays its title, content, author, and date
    And the visitor can click a title and open its detail page

  @BDD-009
  Scenario: Listing renders when no posts exist
    Given the database contains no posts
    When a visitor opens "/"
    Then the shared page and navigation remain visible without post cards
    And the public page renders successfully

  @BDD-010
  Scenario: A visitor opens an existing post
    Given a post exists with a known ID
    And the visitor is on the home listing
    When the visitor follows that post's title link
    Then the detail page displays the matching title, content, author, and date
    And the detail page shows the selected post only

  @BDD-011
  Scenario: Detail returns 404 for an unknown post
    Given the requested post ID does not exist
    When a visitor requests the detail page for an unknown ID
    Then the application returns an HTTP 404 response
    And no nonexistent post data is rendered
