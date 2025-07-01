# DETFACE - Sistema de Reconhecimento Facial

## Overview

DETFACE is a complete facial recognition system for presence and permanence control, developed in Python using OpenCV and face_recognition libraries. The system provides fast facial recognition (under 3 seconds), supports up to 10 registered users, automatic entry/exit logging with timestamps, comprehensive reporting in CSV and PDF formats, and a simple terminal interface.

## System Architecture

The system follows a modular architecture with clear separation of concerns:

### Core Components
- **Main System Controller** (`main.py`): Central orchestrator handling system initialization and coordination
- **Face Detection Engine** (`face_detector.py`): Handles camera capture, face detection, and recognition processing
- **User Management** (`user_manager.py`): Manages user registration, deletion, and data persistence
- **Report Generation** (`report_generator.py`): Creates attendance reports in multiple formats

### Design Patterns
- **Object-Oriented Architecture**: Each module implements a dedicated class with specific responsibilities
- **Configuration-Driven**: Central JSON configuration file for system parameters
- **File-Based Storage**: Uses JSON for user data and CSV for attendance logs

## Key Components

### Face Detection System
- **Technology Stack**: OpenCV for camera handling, face_recognition library for facial encoding
- **Performance Optimization**: Frame skipping, configurable resolution, recognition cooldown periods
- **Security Features**: Recognition threshold settings, maximum failed attempts protection
- **Capacity**: Supports up to 10 users with configurable limits

### User Management System
- **Storage**: JSON-based user database with metadata only (no biometric data stored permanently)
- **Operations**: Add, remove, and modify user profiles
- **Security**: Automatic backups on user changes, confirmation requirements for deletions

### Reporting Engine
- **Output Formats**: CSV for data analysis, PDF for formal reports
- **Report Types**: Weekly, monthly, and custom date range reports
- **Libraries**: pandas for data processing, reportlab for PDF generation
- **Features**: Automatic monthly report generation (configurable)

### Configuration Management
- **Centralized Settings**: Single JSON configuration file for all system parameters
- **Categories**: Recognition settings, security settings, report settings, UI settings
- **Flexibility**: Runtime configuration changes without code modifications

## Data Flow

1. **User Registration**: Face capture → encoding generation → storage in faces/ directory
2. **Recognition Process**: Camera capture → face detection → encoding comparison → threshold validation → attendance logging
3. **Attendance Logging**: Recognized user → timestamp generation → CSV file append → optional backup
4. **Report Generation**: CSV data → pandas processing → PDF/Excel export → storage in reports/

## External Dependencies

### Core Libraries
- **opencv-python**: Camera interface and image processing
- **face-recognition**: Facial encoding and comparison algorithms
- **pandas**: Data manipulation and analysis
- **reportlab**: PDF report generation
- **openpyxl**: Excel file operations
- **numpy**: Numerical operations support

### System Requirements
- **Python**: Version 3.8 or higher
- **Camera**: Compatible webcam or USB camera
- **Storage**: Local file system for data persistence

## Deployment Strategy

### Local Deployment
- **Architecture**: Standalone desktop application
- **Storage**: Local file system with structured directory layout
- **Backup**: Configurable automatic backup system
- **Portability**: Self-contained with minimal external dependencies

### Directory Structure
```
/
├── faces/          # User face encodings
├── logs/           # System logs
├── reports/        # Generated reports
├── backup/         # Automatic backups
├── config.json     # System configuration
├── users.json      # User metadata
└── registro_presenca.csv  # Attendance records
```

### Security Considerations
- **Data Privacy**: Only facial encodings stored, not actual images
- **Access Control**: Configurable failed attempt limits and lockout periods
- **Backup Strategy**: Automatic backups with configurable intervals
- **Audit Trail**: Complete attendance logging with timestamps

## Changelog

- July 1, 2025: Fixed dependency issues by replacing face-recognition library with OpenCV-only solution
- July 1, 2025: Added demo mode for environments without camera access
- July 1, 2025: Created web interface for better camera access in browser environments
- June 30, 2025: Initial setup

## Recent Changes

### Camera Access Solution (July 1, 2025)
- **Problem Solved**: Original system failed due to face-recognition library compilation issues
- **Solution**: Replaced with OpenCV-only approach using Haar cascades and histogram-based features
- **New Features**: 
  - Web interface at port 5000 for browser-based camera access
  - Demo mode for testing without camera
  - Improved camera detection with multiple backends
- **User Impact**: System now works in Replit environment and can access notebook cameras through browser

### Dual Interface System
- **Terminal Interface**: Original command-line interface with demo mode
- **Web Interface**: Browser-based interface with real camera access
- **Port Configuration**: Web interface runs on port 5000

## User Preferences

Preferred communication style: Simple, everyday language.