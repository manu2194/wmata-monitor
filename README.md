## WMATA Monitor

**Introduction**

This Python 3 project, WMATA Monitor, provides real-time train arrival predictions for the Washington Metropolitan Area Transit Authority (WMATA) metro system in the DMV area (DC, Maryland, Virginia). It leverages the WMATA Developer API to fetch the latest arrival information for the nearest station based on the user's provided address.

**Features**

* **Real-time Train Predictions:** Get up-to-date arrival times for different lines at the closest station to your address.
* **Convenient Command Line Interface (CLI):** Run the project with `python app.py "<ADDRESS>"` to retrieve predictions as JSON data.
* **Flexible Data Access:** The `WmataMonitor` class offers the `find_closest_train_prediction` method to retrieve predictions in a Python dictionary format for further processing if needed.

**Installation**

1. **Prerequisites:**
   - Python 3.x ([https://www.python.org/downloads/](https://www.python.org/downloads/))
   - pip (package installer for Python) ([https://pip.pypa.io/en/stable/installation/](https://pip.pypa.io/en/stable/installation/))

2. **Install Required Packages:**
   Open a terminal or command prompt and navigate to your project directory. Then, execute the following command to install the necessary dependencies from the `requirements.txt` file:

   ```bash
   pip install -r requirements.txt
   ```

**API Key**

Before running the application, you need to obtain a WMATA API key from the WMATA Developer Portal ([https://developer.wmata.com/](https://developer.wmata.com/)). Set the API key as an environment variable named `WMATA_API_KEY`.

**Usage**

1. **Setting the API Key:**
   - **Windows:** Use the `set` command in the command prompt.
   - **macOS/Linux:** Use the `export` command in the terminal.

   ```bash
   set WMATA_API_KEY=<your_api_key>  # Windows
   export WMATA_API_KEY=<your_api_key>  # macOS/Linux
   ```

2. **Running the Application:**
   From the command line, run the following command, replacing `<ADDRESS string>` with your actual address:

   ```bash
   python app.py "<ADDRESS>"
   ```

   **Example:**

   ```bash
   python app.py "1600 Pennsylvania Ave NW, Washington, DC 20500"
   ```

3. **Output:**
   The application will output the train arrival predictions for each line at the nearest station to your address in JSON format.


**Additional Notes**

* The application currently retrieves predictions for the nearest station based on a geocoding API. Consider implementing custom logic if a more precise user-specified station selection is desired.

**Contributing**

We welcome contributions to improve this project. If you have suggestions or bug fixes, please feel free to create a pull request on a forked repository.

**License**

This project is licensed under the MIT License. See the `LICENSE` file for details.

**Support**

For any questions or issues, feel free to create an issue on the project's GitHub repository (if applicable).
