# Pogo-Pin Monitoring System (PPM V5)

A comprehensive monitoring system designed to track and display yield data per tester by stage for pogo-pin testing processes.

## Features

- Real-time yield monitoring by tester and stage
- Graphical data visualization
- User authentication and login system
- Database connectivity for data storage
- Email notifications via integrated mailer
- Customizable themes (dark/light mode)
- Export and reporting capabilities
- History tracking and editing

## Installation

### Prerequisites

- Python 3.8 or higher
- Required Python packages (see requirements.txt if available)
- Oracle database access (if applicable)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/OliverFeronel090597/Pogo-Pin-Monitoring-System.git
   cd Pogo-Pin-Monitoring-System
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure database connection in `libs/DatabaseConnector.py`

4. Run the application:
   ```bash
   python PPM_V5.py
   ```

### Building Executable

The project uses PyInstaller for creating standalone executables:

```bash
python ToExe.py
```

Built executables will be available in the `EXE/` directory.

## Usage

1. Launch the application using `PPM_V5.py` or the built executable.
2. Log in with your credentials.
3. Select the tester and stage to monitor.
4. View yield data and graphs in real-time.
5. Use the various modules for data entry, history, and notifications.

## Project Structure

- `PPM_V5.py`: Main application entry point
- `libs/`: Core library modules
  - `DatabaseConnector.py`: Database connection handling
  - `DataGraphing.py`: Graphing and visualization
  - `Mailer.py`: Email functionality
  - `LoginForm.py`: User authentication
  - And more...
- `THEME/`: UI themes and stylesheets
- `icon/`: Application icons and resources
- `DATA/`: Data files and configurations
- `build/`: PyInstaller build artifacts
- `EXE/`: Built executables

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

## License

This project is licensed under the terms specified in the LICENSE file.

## Support

For issues or questions, please create an issue in the GitHub repository. 
