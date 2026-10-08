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
