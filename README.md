# TeamsLogLicenseNSChecker
This script analyzes Microsoft Teams log .zip files to extract the values of the keys "licenseName" and "NoiseSuppressionDefault" from both JSON and TXT files (including nested zip files). It outputs a summary and detailed results to a file called license_analysis_results.txt

Overview:
---------
This script analyzes Microsoft Teams log .zip files to extract the values of the keys "licenseName" and "NoiseSuppressionDefault" from both JSON and TXT files (including nested zip files). It outputs a summary and detailed results to a file called license_analysis_results.txt.

Requirements:
-------------
- Python 3.x (recommended 3.7+)
- No external packages required (uses only Python standard library)

How to Use:
-----------
1. Open a terminal (Command Prompt, PowerShell, or VS Code Terminal).
2. Activate your Python environment if needed (e.g., `venvTeamsLogLicenseAna`).
3. Navigate to the script directory:
   cd "c:\Users\jianzou\OneDrive - Microsoft\Python_JianScripts\TeamsLogAna"
4. Run the script:
   python teams_log_analyzer.py
5. A file dialog will appear. Select your Teams log .zip file.
6. The script will process the zip (including nested zips), extract the relevant key values, and print results to the terminal.
7. Results are saved to license_analysis_results.txt in the same folder as your log file.

Output Details:
---------------
- The summary section at the top of license_analysis_results.txt lists all unique values found for licenseName and NoiseSuppressionDefault. The script version is also included in the summary.
- The detailed section lists every occurrence found, including the file, location, and value.
- For TXT files, the script supports both quoted ("key":"value") and unquoted (key = value) formats.
- The script also processes nested zip files recursively.
