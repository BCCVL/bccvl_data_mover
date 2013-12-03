Feature: Move Service - Downloads from source and moves to destination using the Data Mover's XMLRPC Service

Scenario: Move http://www.intersect.org.au to test_machine
    Given I am connected to the Data Mover server
    And I want to use the destination host "test_machine" and some temp directory
    And my source is of type "url" with "url" of "http://www.intersect.org.au"
    When I request a move with the defined requirements
    Then I should see that the job status is either "PENDING" or "IN_PROGRESS"
    Then I wait 5 seconds
    When I check the status of the move job
    Then I should see that the job status is "COMPLETED"
    And I should see "1" files in my temp directory
    And I should see a file with suffix "html" in my temp directory

Scenario: Using SCP as a source and destination protocol
    Given I am connected to the Data Mover server
    And I want to use the destination host "test_machine" and some temp directory
    And my source is of type "scp" with host of "test_machine" and path of some temporary file named "temp_file.txt" with content "this is the content of my temp file"
    When I request a move with the defined requirements
    Then I should see that the job status is either "PENDING" or "IN_PROGRESS"
    Then I wait 5 seconds
    When I check the status of the move job
    Then I should see that the job status is "COMPLETED"
    And I should see "1" files in my temp directory
    And I should see a file in my temp directory named "temp_file.txt" with content "this is the content of my temp file"

Scenario: Move http://www.intersect.org.au to an unknown destination
    Given I am connected to the Data Mover server
    And I want to use the destination host "unknown_destination" and some temp directory
    And my source is of type "url" with "url" of "http://www.intersect.org.au"
    When I request a move with the defined requirements
    Then I should see that the job status is "REJECTED"
    And I should see "0" files in my temp directory
    And I should see that the job reason is "Unknown destination 'unknown_destination'"

Scenario: Move http://www.intersect.org.au to test_machine - Unknown source type
    Given I am connected to the Data Mover server
    And I want to use the destination host "test_machine" and some temp directory
    And my source is of type "ftp" with "url" of "http://www.intersect.org.au"
    When I request a move with the defined requirements
    Then I should see that the job status is "REJECTED"
    And I should see "0" files in my temp directory
    And I should see that the job reason is "Unknown source type 'ftp'"

Scenario: Move http://www.intersect.org.a to test_machine - Could not download from URL
    Given I am connected to the Data Mover server
    And I want to use the destination host "test_machine" and some temp directory
    And my source is of type "url" with "url" of "http://www.intersect.org.a"
    When I request a move with the defined requirements
    Then I should see that the job status is either "PENDING" or "IN_PROGRESS"
    Then I wait 5 seconds
    When I check the status of the move job
    Then I should see that the job status is "FAILED"
    And I should see "0" files in my temp directory
    And I should see that the job reason is "Could not download from URL http://www.intersect.org.a"

Scenario: Move http://www.intersect.org.au to test_machine_bad - Unable to send to destination
    Given I am connected to the Data Mover server
    And I want to use the destination host "test_machine_bad" and some temp directory
    And my source is of type "url" with "url" of "http://www.intersect.org.au"
    When I request a move with the defined requirements
    Then I should see that the job status is either "PENDING" or "IN_PROGRESS"
    Then I wait 5 seconds
    When I check the status of the move job
    Then I should see that the job status is "FAILED"
    And I should see "0" files in my temp directory
    And I should see that the job reason is "Unable to send to destination"

Scenario: Move from multiple sources to test_machine
    Given I am connected to the Data Mover server
    And I want to use the destination host "test_machine" and some temp directory
    And my source is of type mixed
    And one of my sources is of type "url" with "url" of "http://www.intersect.org.au"
    And one of my sources is of type "ala" with "lsid" of "urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae"
    And one of my sources is of type "scp" with host of "test_machine" and path of some temporary file named "temp_file.txt" with content "this is the content of my temp file"
    When I request a move with the defined requirements
    Then I should see that the job status is either "PENDING" or "IN_PROGRESS"
    Then I wait 30 seconds
    When I check the status of the move job
    Then I should see that the job status is "COMPLETED"
    And I should see "5" files in my temp directory
    And I should see a file in my temp directory named "temp_file.txt" with content "this is the content of my temp file"
    And I should see a file with suffix "html" in my temp directory
    And I should see the ALA files in my temp directory

Scenario: Move from multiple sources to test_machine and zip
    Given I am connected to the Data Mover server
    And I want to use the destination host "test_machine" and some temp directory
    And I want to zip the files sent to the destination
    And my source is of type mixed
    And one of my sources is of type "url" with "url" of "http://www.intersect.org.au"
    And one of my sources is of type "ala" with "lsid" of "urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae"
    And one of my sources is of type "scp" with host of "test_machine" and path of some temporary file named "temp_file.txt" with content "this is the content of my temp file"
    When I request a move with the defined requirements
    Then I should see that the job status is either "PENDING" or "IN_PROGRESS"
    Then I wait 30 seconds
    When I check the status of the move job
    Then I should see that the job status is "COMPLETED"
    And I should see "1" files in my temp directory
    And I should see a file with suffix "zip" in my temp directory