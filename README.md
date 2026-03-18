# Employee Asset Management

A comprehensive asset management system for Frappe/ERPNext v16.

## Features

- **Asset Category Master**: Define categories with maximum limits per employee and approval requirements.
- **Company Asset Master**: Track individual assets, their current status (Available, Assigned, Maintenance, Retired), and current holder.
- **Asset Request**: Employee portal for requesting assets with urgency and approval workflow.
- **Asset Assignment**: Formalize asset issuance with automated status updates.
- **Asset Return**: Track returns with condition monitoring and automated damage notifications.
- **Reporting**: "Employee Asset Register" for an overview of all issued assets.

## Installation

1. Get the app:
   ```bash
   bench get-app employee_asset_management
   ```
2. Install the app on your site:
   ```bash
   bench --site yourcurrentsite install-app employee_asset_management
   ```

## Workflow

The **Asset Request** DocType follows a formal workflow:
`Draft` -> `Pending Approval` -> `Approved` / `Rejected` -> `Fulfilled` (automatically updated on Assignment).

## Notifications

Administrators are automatically notified via email when an asset is returned in **Damaged** condition.


User Guide: Employee Asset Management System
Welcome to the Employee Asset Management System! This guide will take you through the end-to-end process of managing assets, from initial setup to tracking returns.

🚀 Step 1: Initial Setup (Masters)
Before you can issue assets, you need to define your categories and items.

1.1 Create Asset Categories
Define the types of assets your company owns.

Go to Asset Category list.
Click New.
Enter a Category Name (e.g., "Laptop", "Mobile", "Office Chair").
Set the Max Assets Per Employee (e.g., "1" for Laptops).
Save.
1.2 Add Company Assets
Add individual items to your inventory.

Go to Company Asset list.
Click New.
Enter Asset Name and select the Asset Category.
Set the initial Status to "Available".
Save.
📋 Step 2: Requesting an Asset
Employees (or managers on their behalf) can request assets they need.

Go to Asset Request.
Click New.
Select the Employee and the Asset Category they are requesting.
Enter the Requested Date.
Save the document. It will start in the Draft state.
🚦 Step 3: Approval Workflow
The request must move through the approval process:

Submit for Approval: In the Asset Request, use the Workflow button to move it to Pending Approval.
Review: A manager or system administrator can then Approve or Reject the request.
Once Approved, the request is ready for fulfillment.
🛠️ Step 4: Asset Assignment (Issuance)
Once a request is approved, you issue the actual asset.

Go to Asset Assignment.
Click New.
Select the Asset Request (this will auto-fill the Employee and Category).
Select the specific Company Asset (only "Available" assets of that category will show).
Enter the Assignment Date and Expected Return Date.
Save and Submit.
Note: This will automatically update the Asset Request status to Fulfilled and mark the Company Asset as Assigned.
🔄 Step 5: Returning an Asset
When an employee leaves or replaces an item, record the return.

Go to Asset Return.
Click New.
Select the Employee and the Company Asset being returned.
Set the Return Date.
Select the Condition (Excellent, Good, Fair, Damaged).
💡 Tip: If you select "Damaged", an automated email alert will be sent to the System Manager.
Save and Submit.
Note: The Company Asset status will revert to Available.
📊 Step 6: Tracking & Reporting
Monitor your assets using the built-in report.

Go to Employee Asset Register (Script Report).
Use filters to view assets by Employee or Category.
View critical details like Assignment Date, Expected Return Date, and current Status.
💡 Troubleshooting Tips
Asset already assigned: The system prevents assigning the same asset to different people during overlapping dates.
Limit Exceeded: You cannot assign more assets of a specific category than the limit defined in the Asset Category.
