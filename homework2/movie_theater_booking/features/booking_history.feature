Feature: Booking history
  Signed-in moviegoers can review their own reservations in a predictable order.

  Scenario: View my booking history
    Given I am signed in as "Sam"
    And "Sam" has booked seat "A1" for "Dune"
    When I open My Bookings
    Then I see booking "Dune" with seat "A1" and today's formatted date

  Scenario: Only my bookings are shown
    Given I am signed in as "Sam"
    And "Sam" has booked seat "A1" for "Dune"
    And "Alex" has booked seat "A2" for "Up"
    When I open My Bookings
    Then I see the booking for "Dune"
    But I do not see the booking for "Up"

  Scenario: Newest bookings appear first
    Given I am signed in as "Sam"
    And "Sam" has bookings on different and matching dates
    When I open My Bookings
    Then the bookings are shown by newest date and highest id first

  Scenario: Authenticated booking navigation
    Given I am signed in as "Sam"
    When I open My Bookings
    Then the navigation links to Movies and My Bookings

  Scenario: No booking history yet
    Given I am signed in as "Sam"
    And I have no bookings
    When I open My Bookings
    Then I see "You have no bookings yet."

  Scenario: Sign in to view booking history
    Given I am not signed in
    When I open My Bookings
    Then I am redirected to sign in
    And the navigation does not link to My Bookings
