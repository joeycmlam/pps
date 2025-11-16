```gherkin
Feature: Personal Portfolio Management System

  The system allows users to manage and track their financial transactions, view their portfolio positions, 
  and analyze historical AUM data. It ensures ease of use, transparency, and data security.

  Background:
    Given the user has successfully logged into their account
    And the user has an existing portfolio with transactions for stocks and mutual funds

  Scenario: Add a new stock transaction (Happy Path)
    Given the user is on the "Add Transaction" page
    When the user selects "Stock" as the asset type
    And enters the transaction details:
      | Field          | Value          |
      | Stock Name     | ABC Corp       |
      | Quantity       | 50             |
      | Purchase Price | 100            |
      | Date           | 2023-10-01     |
    And clicks the "Save" button
    Then the transaction should be successfully added to the portfolio
    And the portfolio position should be updated to include the new stock
    And the user should see a confirmation message "Transaction added successfully."

  Scenario: Import transactions from a CSV file (Alternative Path)
    Given the user is on the "Import Transactions" page
    When the user uploads a valid CSV file with transaction data
    And clicks the "Import" button
    Then the system should process the file
    And add the transactions to the user's portfolio
    And display a success message "Transactions imported successfully."
    And the portfolio position should reflect the imported transactions

  Scenario: View portfolio allocation by asset type (Happy Path)
    Given the user is on the "Portfolio Summary" page
    When the user views the portfolio allocation section
    Then the system should display a breakdown of the portfolio by asset type
    And the allocation percentages should sum up to 100%
    And the user should see a pie chart visualization of the allocation

  Scenario: Error handling for invalid transaction input (Error Handling)
    Given the user is on the "Add Transaction" page
    When the user selects "Stock" as the asset type
    And enters invalid transaction details:
      | Field          | Value          |
      | Stock Name     |                |
      | Quantity       | -10            |
      | Purchase Price | abc            |
      | Date           | invalid-date   |
    And clicks the "Save" button
    Then the system should not save the transaction
    And the user should see error messages:
      | Field          | Error Message                              |
      | Stock Name     | "Stock Name is required."                  |
      | Quantity       | "Quantity must be a positive number."      |
      | Purchase Price | "Purchase Price must be a valid number."   |
      | Date           | "Date must be in a valid format (YYYY-MM-DD)." |

  Scenario: Calculate and display historical AUM trends (Edge Case)
    Given the user is on the "Historical AUM" page
    And the user has transactions spanning multiple years
    When the user selects a date range from "2022-01-01" to "2023-10-01"
    Then the system should calculate the AUM for each day within the selected range
    And display a line chart showing the AUM trends over time
    And the chart should include data points for all days in the range
    And the user should see a summary of the highest, lowest, and average AUM during the period

  Scenario: Handle empty portfolio gracefully (Edge Case)
    Given the user has no transactions in their portfolio
    When the user navigates to the "Portfolio Summary" page
    Then the system should display a message "No transactions found. Start by adding your first transaction."
    And the portfolio allocation section should not display any data
    And the user should see a button "Add Transaction" to start adding transactions
```