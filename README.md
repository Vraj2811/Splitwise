# Splitwise - Expense Sharing & Tracking Application

A comprehensive web-based expense management application built with Python (Flask) that helps users track, split, and manage shared expenses with friends and groups.

## Overview

This application simplifies the process of managing shared expenses by providing intuitive tools for expense tracking, group management, and intelligent expense splitting. Whether you're splitting bills with roommates, organizing group trips, or tracking personal spending, this application makes it easy to keep everyone on the same page.

## Key Features

### 1. **Individual Expense Tracking**
- Add and manage personal expenses with detailed descriptions
- Categorize expenses for better organization and analysis
- Track expenses over time with timeline views
- View expense history with filtering and sorting options

### 2. **Group Management**
- Create and manage expense groups for shared activities
- Add members to groups and manage group settings
- Delete groups when no longer needed
- Real-time updates when group information changes

### 3. **Flexible Expense Splitting**
Split group expenses in three different ways:
- **Equal Split**: Divide expenses equally among all group members
- **Amount-Based Split**: Specify exact amounts each person owes
- **Share-Based Split**: Distribute expenses based on custom share percentages

### 4. **Expense Tracker & Analytics**
- **Category-Based Analysis**: View expense distribution by category with visual pie charts
- **Timeline Analysis**: Track expenses over time with daily and weekly bar charts
- **Description-Based Tracking**: Search and filter expenses by description
- **Expense Summary**: Quick overview of total spending and category breakdowns
- **Simplified Payments**: Calculate and display who owes whom, with options to simplify payment chains

### 5. **User Management**
- Secure user registration and authentication
- User profiles with unique identifiers
- View all users in the system
- Session management for secure access

## Technology Stack

- **Backend**: Python with Flask web framework
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite
- **Styling**: Custom CSS with dark theme

## Getting Started

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation

1. Clone or download the project
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and navigate to `http://localhost:5000`

## Usage

### Creating an Account
1. Register with a username and password
2. Log in to access the dashboard

### Managing Expenses
1. **Add Individual Expense**: Use the dashboard to add personal expenses
2. **Create a Group**: Set up a new group for shared expenses
3. **Add Group Expense**: Add expenses within a group and choose a splitting method
4. **View Tracker**: Analyze your spending patterns with charts and summaries

### Settling Payments
- Use the Simplified Payments feature to see who owes whom
- Settle debts efficiently with optimized payment suggestions

## Project Structure

```
├── app.py                          # Main Flask application
├── database.db                     # SQLite database
├── requirements.txt                # Python dependencies
├── static/
│   ├── main.css                   # Main stylesheet
│   └── styles.css                 # Additional styles
└── templates/
    ├── dashboard.html             # Main dashboard
    ├── group_page.html            # Group management
    ├── tracker.html               # Expense analytics
    ├── simplified_payments.html    # Payment settlement
    ├── login.html                 # Login page
    ├── register.html              # Registration page
    └── users.html                 # User management
```

## Features Highlights

✨ **Dark-Themed UI** - Easy on the eyes with a modern dark interface  
📊 **Visual Analytics** - Pie charts and bar charts for expense insights  
🔄 **Real-Time Updates** - Changes reflect immediately across the application  
💰 **Smart Splitting** - Multiple splitting methods for different scenarios  
🎯 **Category Management** - Organize expenses with predefined categories  
📱 **Responsive Design** - Works seamlessly on different screen sizes  

## Future Enhancements

- Export expense reports to PDF/CSV
- Mobile app version
- Advanced filtering and search capabilities
- Recurring expense automation
- Multi-currency support
- Integration with payment platforms

## License

This project is open source and available for personal and educational use.

## Support

For issues, questions, or suggestions, please refer to the project documentation or contact the developer.

