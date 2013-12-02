Feature: Pull ALA occurrences using the Data Mover's XMLRPC Service

Scenario: Pull Red Kangaroo occurrences from ALA
    Given I am connected to the Data Mover server
    When I pull occurrences from ALA using the LSID "urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae"
    Then I wait 10 seconds
    When I check the status of the move job
    Then I should see that the job status is "IN_PROGRESS"
    And I wait 30 seconds
    When I check the status of the move job
    Then I should see that the job status is "COMPLETED"
    And I should see "3" files in my temp directory
    And I should see the ALA files in my temp directory

Scenario: Pull an occurrence from ALA that does not exist
    Given I am connected to the Data Mover server
    When I pull occurrences from ALA using the LSID "bad:lsid:here"
    Then I wait 10 seconds
    When I check the status of the move job
    Then I should see that the job status is "FAILED"
    And I should see "0" files in my temp directory
