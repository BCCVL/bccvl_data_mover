Feature: Move Service - Downloads from source and moves to destination using the Data Mover's XMLRPC Service

Scenario: Move http://www.intersect.org.au to test_machine
    Given I am connected to the Data Mover server
    And I want to move a file to "test_machine" with file path "behave_test/bccvl/visualizer/some_file.txt"
    And my file type is "url" with id "http://www.intersect.org.au"
    When I request a move with the defined requirements
    Then I should see that the response is PENDING or IN_PROGRESS
    Then I wait 5 seconds
    When I check the status of the move job
    Then I should see that the move job status is "COMPLETED"
    And I should see the file "behave_test/bccvl/visualizer/some_file.txt" in my temp directory

Scenario: Move with invalid parameters
    Given I am connected to the Data Mover server
    And I want to move a file to "unknown_destination" with source path "behave_test/bccvl/visualizer/some_file.txt"
    And my file protocol is "url" with url "http://www.intersect.org.au"
    When I request a move with the defined requirements
    Then I should see that the response status is REJECTED and the reason is "Missing or incorrect parameters"

Scenario: Move http://www.intersect.org.au to an unknown destination
    Given I am connected to the Data Mover server
    And I want to move a file to "unknown_destination" with file path "behave_test/bccvl/visualizer/some_file.txt"
    And my file type is "url" with id "http://www.intersect.org.au"
    When I request a move with the defined requirements
    Then I should see that the response status is REJECTED and the reason is "Unknown destination"

Scenario: Move http://www.intersect.org.au to test_machine - Unknown source type
    Given I am connected to the Data Mover server
    And I want to move a file to "test_machine" with file path "behave_test/bccvl/visualizer/some_file.txt"
    And my file type is "ftp" with id "http://www.intersect.org.au"
    When I request a move with the defined requirements
    Then I should see that the response is PENDING or IN_PROGRESS
    Then I wait 5 seconds
    When I check the status of the move job
    Then I should see that the move job status is "FAILED"
    And I should see that the reason is "Unknown source type ftp"

Scenario: Move http://www.intersect.org.au to test_machine - Could not download from URL
    Given I am connected to the Data Mover server
    And I want to move a file to "test_machine" with file path "behave_test/bccvl/visualizer/some_file.txt"
    And my file type is "url" with id "http://www.intersect.org.a"
    When I request a move with the defined requirements
    Then I should see that the response is PENDING or IN_PROGRESS
    Then I wait 5 seconds
    When I check the status of the move job
    Then I should see that the move job status is "FAILED"
    And I should see that the reason is "Could not download from URL"

Scenario: Move http://www.intersect.org.au to test_machine_bad - Unable to send to destination
    Given I am connected to the Data Mover server
    And I want to move a file to "test_machine_bad" with file path "behave_test/bccvl/visualizer/some_file.txt"
    And my file type is "url" with id "http://www.intersect.org.au"
    When I request a move with the defined requirements
    Then I should see that the response is PENDING or IN_PROGRESS
    Then I wait 5 seconds
    When I check the status of the move job
    Then I should see that the move job status is "FAILED"
    And I should see that the reason is "Unable to send to destination"