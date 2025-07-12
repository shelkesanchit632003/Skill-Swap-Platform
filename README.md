# Skill Swap Platform

A comprehensive web application that enables users to list their skills and request skill swaps with other users. Built with Flask, HTML, CSS, JavaScript, and SQLite.

## Features

### User Features
- **User Registration & Authentication**: Secure user accounts with login/logout functionality
- **Profile Management**: 
  - Basic info (name, location, profile photo)
  - Availability settings (weekends, evenings, etc.)
  - Public/private profile visibility
- **Skill Management**:
  - List skills offered with descriptions
  - List skills wanted to learn
- **Skill Discovery**:
  - Browse all available skills
  - Search skills by name or description
- **Swap Requests**:
  - Request skill swaps from other users
  - Accept or reject incoming swap requests
  - Delete pending requests
- **Rating System**:
  - Rate users after completed swaps
  - View ratings and feedback

### Admin Features
- **User Management**:
  - View all registered users
  - Ban/unban users who violate policies
- **Content Moderation**:
  - Approve or reject skill descriptions
  - Monitor for inappropriate content
- **Swap Monitoring**:
  - View all pending, accepted, and cancelled swaps
  - Track platform activity
- **Platform Communication**:
  - Send platform-wide messages and announcements
- **Analytics & Reports**:
  - Download user activity reports
  - View swap statistics
  - Track popular skills

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or download the project files**
   ```bash
   # Navigate to the project directory
   cd Project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your web browser
   - Navigate to `http://localhost:5000`

## Default Admin Account

The application comes with a pre-configured admin account:
- **Username**: `admin`
- **Password**: `admin123`

Use this account to access the admin panel and manage the platform.

## Project Structure

```
Project/
│
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── skillswap.db           # SQLite database (created automatically)
│
├── templates/             # HTML templates
│   ├── base.html          # Base template with navigation
│   ├── index.html         # Homepage
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── dashboard.html     # User dashboard
│   ├── profile.html       # User profile view
│   ├── edit_profile.html  # Profile editing
│   ├── browse_skills.html # Skill browsing
│   ├── request_swap.html  # Swap request form
│   ├── rate_user.html     # Rating form
│   ├── admin_dashboard.html    # Admin dashboard
│   ├── admin_users.html        # User management
│   ├── admin_messages.html     # Platform messages
│   └── admin_reports.html      # Analytics reports
│
└── static/               # Static files
    ├── css/
    │   └── style.css     # Custom styles
    ├── js/
    │   └── main.js       # JavaScript functionality
    └── uploads/          # User uploaded files
```

## Database Schema

The application uses SQLite with the following tables:

- **users**: User accounts and profile information
- **skills_offered**: Skills that users offer to teach
- **skills_wanted**: Skills that users want to learn
- **swap_requests**: Skill swap requests between users
- **ratings**: User ratings and feedback after swaps
- **platform_messages**: Admin announcements

## Key Features Explained

### User Workflow
1. **Register** → Create an account with basic information
2. **Setup Profile** → Add skills offered and wanted, set availability
3. **Browse Skills** → Search for skills you want to learn
4. **Request Swaps** → Send swap requests to skill providers
5. **Manage Requests** → Accept/reject incoming requests
6. **Complete Swaps** → Meet and exchange skills
7. **Rate Experience** → Provide feedback and ratings

### Admin Workflow
1. **Monitor Platform** → View statistics and activity
2. **Moderate Content** → Approve/reject skill descriptions
3. **Manage Users** → Handle policy violations
4. **Send Messages** → Communicate with all users
5. **Generate Reports** → Download activity data

## Security Features

- Password hashing using Werkzeug security
- Session management for user authentication
- File upload validation and security
- SQL injection prevention with parameterized queries
- XSS protection with template escaping

## Customization

### Adding New Features
- Modify `app.py` for backend functionality
- Add new templates in `templates/` directory
- Update `static/css/style.css` for styling
- Extend `static/js/main.js` for frontend features

### Database Modifications
- Update the `init_db()` function in `app.py`
- Add new table schemas as needed
- Implement migration logic for existing data

## Troubleshooting

### Common Issues

1. **Database errors**: Delete `skillswap.db` and restart the app to reset the database
2. **File upload issues**: Ensure the `static/uploads/` directory exists and is writable
3. **Port conflicts**: Change the port in `app.run()` if 5000 is already in use

### Development Mode
- The app runs in debug mode by default (`debug=True`)
- Changes to Python files will auto-reload the server
- Template and static file changes are reflected immediately

## License

This project is open source and available under the MIT License.

## Support

For questions or issues, please refer to the code comments or modify the application to suit your specific needs.
