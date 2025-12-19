# Google Form Autofill and Submit

A Python tool for automatically filling and submitting Google Forms with generated or custom data. This project provides both a graphical user interface (GUI) and command-line examples for automating form submissions.

## Features

- **GUI Interface**: User-friendly PyQt5-based application for easy form filling and submission
- **Form Parsing**: Automatically parses Google Form structure and fields
- **Data Generation**: Uses Faker library to generate realistic fake data
- **Multiple Field Types**: Supports various Google Form field types including:
  - Short answer
  - Paragraph
  - Multiple choice
  - Dropdown
  - Checkboxes
  - Linear scale
  - Date
  - Time
- **Batch Submission**: Submit multiple responses with customizable delays
- **Progress Tracking**: Real-time progress bar and submission statistics

## Limitations

- Only supports single-page Google Forms
- Does not support file upload fields (requires login)
- Requires form to be publicly accessible

## Requirements

- Python 3.6+
- PyQt5
- requests
- faker

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/googleform-autofill-and-submit.git
   cd googleform-autofill-and-submit
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install PyQt5 requests faker
   ```

## Usage

### GUI Application

Run the main application:
```bash
python main.py
```

The GUI allows you to:
- Enter the Google Form URL
- Configure submission settings (number of submissions, delay)
- View progress and results

### Command-Line Examples

See the `examples/` directory for command-line usage:

- `all_in_one.py`: Complete example with predefined form fields
- `multipage.py`: Example for multi-page forms (if supported)

To run an example:
```bash
python examples/all_in_one.py
```

### Using the Library

```python
from form import parse_form_entries
import requests

# Parse form entries
url = "https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform"
entries = parse_form_entries(url)

# Generate submission data (see examples for details)
# ...

# Submit the form
response_url = url.replace('/viewform', '/formResponse')
response = requests.post(response_url, data=form_data)
```

## Project Structure

- `main.py`: Main GUI application
- `form.py`: Form parsing functionality
- `generator.py`: Data generation utilities
- `examples/`: Command-line usage examples
- `run.bat`: Windows batch file to run the application

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and testing purposes only. Please respect the terms of service of Google Forms and do not use this tool for spam or malicious activities.