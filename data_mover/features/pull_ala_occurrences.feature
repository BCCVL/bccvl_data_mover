Feature: Pull ALA occurrences using the Data Mover's XMLRPC Service

Scenario: Pull Red Kangaroo occurrences from ALA
    Given I am connected to the Data Mover server
    When I pull occurrences from ALA using the LSID "urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae"
    Then I wait 10 seconds
    When I check the status of the pull job
    Then I should see that the job status is "DOWNLOADING"
    And I wait 30 seconds
    When I check the status of the pull job
    Then I should see that the job status is "COMPLETED"
    And I should see the file "behave_test/ALA/urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae.csv"
    And I should see the file "behave_test/ALA/urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae.json"
    And I should see the file "behave_test/dataset_provider/Red Kangaroo (Macropus rufus) occurrences.json"

Scenario: Pull an occurrence from ALA that does not exist
    Given I am connected to the Data Mover server
    When I pull occurrences from ALA using the LSID "bad:lsid:here"
    Then I wait 10 seconds
    When I check the status of the pull job
    Then I should see that the job status is "DOWNLOADING"
    And I wait 1 minutes
    When I check the status of the pull job
    Then I should see that the job status is "FAILED"
