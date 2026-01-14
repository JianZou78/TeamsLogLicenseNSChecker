import zipfile
import json
import os
import io
from tkinter import Tk, filedialog
import re


def extract_license_from_json(content, file_path):
    """Extract licenseName and NoiseSuppressionDefault from JSON content."""
    results = []
    try:
        data = json.loads(content)
        
        # Recursively search for licenseName and NoiseSuppressionDefault in the JSON structure
        def find_keys(obj, current_path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{current_path}.{key}" if current_path else key
                    if key == "licenseName":
                        results.append({
                            'file': file_path,
                            'path': new_path,
                            'value': value,
                            'key': 'licenseName'
                        })
                    elif key == "NoiseSuppressionDefault":
                        results.append({
                            'file': file_path,
                            'path': new_path,
                            'value': value,
                            'key': 'NoiseSuppressionDefault'
                        })
                    find_keys(value, new_path)
            elif isinstance(obj, list):
                for idx, item in enumerate(obj):
                    new_path = f"{current_path}[{idx}]"
                    find_keys(item, new_path)
        
        find_keys(data)
    except json.JSONDecodeError:
        pass
    
    return results


def extract_license_from_txt(content, file_path):
    """Extract licenseName and NoiseSuppressionDefault from TXT content using regex."""
    results = []
    try:
        text = content.decode('utf-8', errors='ignore')
        lines = text.split('\n')
        
        # Pattern 1: "licenseName":value (with quotes around licenseName and colon)
        pattern_license = r'"licenseName"\s*:\s*"?([^",}\s\n]+)"?'
        # Pattern 2a: "NoiseSuppressionDefault": value (JSON format with quotes)
        pattern_noise_json = r'"NoiseSuppressionDefault"\s*:\s*"?([^",}\s\n]+)"?'
        # Pattern 2b: NoiseSuppressionDefault = value (config format)
        pattern_noise_config = r'NoiseSuppressionDefault\s*=\s*"?([^",\s\n]+)"?'
        
        for line_num, line in enumerate(lines, 1):
            # Search for licenseName
            matches = re.finditer(pattern_license, line)
            for match in matches:
                match_pos = match.start()
                context_start = max(0, match_pos - 100)
                context_end = min(len(line), match.end() + 100)
                context = line[context_start:context_end].strip()
                
                results.append({
                    'file': file_path,
                    'path': f'Line {line_num}',
                  
                 
                    'full_line': line.strip(),
                    'key': 'licenseName'
                })
            
            # Search for NoiseSuppressionDefault (JSON format with quotes)
            matches = re.finditer(pattern_noise_json, line)
            for match in matches:
                match_pos = match.start()
                context_start = max(0, match_pos - 100)
                context_end = min(len(line), match.end() + 100)
                context = line[context_start:context_end].strip()
                
                results.append({
                    'file': file_path,
                    'path': f'Line {line_num}',
                    
                   
                    'full_line': line.strip(),
                    'key': 'NoiseSuppressionDefault'
                })
            
            # Search for NoiseSuppressionDefault (config format with =)
            matches = re.finditer(pattern_noise_config, line)
            for match in matches:
                match_pos = match.start()
                context_start = max(0, match_pos - 100)
                context_end = min(len(line), match.end() + 100)
                context = line[context_start:context_end].strip()
                
                results.append({
                    'file': file_path,
                    'path': f'Line {line_num}',
                 
                    'full_line': line.strip(),
                    'key': 'NoiseSuppressionDefault'
                })
    except Exception as e:
        pass
    
    return results


def process_zip_file(zip_file, parent_path="", level=0):
    """Process a zip file and extract licenseName from JSON and TXT files."""
    results = []
    
    try:
        with zipfile.ZipFile(zip_file, 'r') as zf:
            for file_info in zf.namelist():
                # Skip directories
                if file_info.endswith('/'):
                    continue
                
                full_path = os.path.join(parent_path, file_info)
                file_lower = file_info.lower()
                
                try:
                    file_content = zf.read(file_info)
                    
                    # Handle nested zip files
                    if file_lower.endswith('.zip'):
                        print(f"{'  ' * level}Processing nested zip: {full_path}")
                        nested_zip = io.BytesIO(file_content)
                        nested_results = process_zip_file(nested_zip, full_path, level + 1)
                        results.extend(nested_results)
                    
                    # Handle JSON files
                    elif file_lower.endswith('.json'):
                        print(f"{'  ' * level}Processing JSON: {full_path}")
                        json_results = extract_license_from_json(file_content, full_path)
                        results.extend(json_results)
                    
                    # Handle TXT files
                    elif file_lower.endswith('.txt'):
                        # Highlight RigelAppSettings.txt specifically
                        if 'rigelappsettings.txt' in file_lower:
                            print(f"{'  ' * level}Processing RigelAppSettings.txt: {full_path}")
                        else:
                            print(f"{'  ' * level}Processing TXT: {full_path}")
                        txt_results = extract_license_from_txt(file_content, full_path)
                        results.extend(txt_results)
                
                except Exception as e:
                    print(f"{'  ' * level}Error processing {full_path}: {str(e)}")
    
    except Exception as e:
        print(f"Error opening zip file: {str(e)}")
    
    return results


def main():
    """Main function to open file dialog and process Teams log file."""
    # Create root window and hide it
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    # Open file dialog
    print("Please select a Teams log .zip file...")
    file_path = filedialog.askopenfilename(
        title="Select Teams Log File",
        filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
    )
    
    if not file_path:
        print("No file selected. Exiting.")
        return
    
    print(f"\nProcessing file: {file_path}\n")
    print("=" * 80)
    
    # Process the zip file
    results = process_zip_file(file_path, os.path.basename(file_path))
    
    # Display results
    print("\n" + "=" * 80)
    print(f"\nFound {len(results)} result(s):\n")
    
    if results:
        for idx, result in enumerate(results, 1):
            key_name = result.get('key', 'unknown')
            print(f"{idx}. Key: {key_name}")
            print(f"   File: {result['file']}")
            print(f"   Location: {result['path']}")
            
            # Only show value and context for JSON files, not TXT files
            if 'full_line' not in result:
                # This is a JSON result
                print(f"   Value: {result['value']}")
            else:
                # This is a TXT result, only show full line
                print(f"   Full Line: {result['full_line']}")
            print()
    else:
        print("No 'licenseName' or 'NoiseSuppressionDefault' found in the log files.")
    
    # Optional: Save results to a file
    output_file = os.path.join(os.path.dirname(file_path), "license_analysis_results.txt")

    # Collect summary values
    license_names = set()
    noise_suppressions = set()
    for result in results:
        if result.get('key') == 'licenseName':
            # For TXT, try to extract value from the full_line if possible
            if 'value' in result:
                license_names.add(str(result['value']))
            elif 'full_line' in result:
                # Try to extract value from the line using non-greedy match
                match = re.search(r'"licenseName"\s*:\s*"(.*?)"', result['full_line'])
                if match:
                    license_names.add(match.group(1))
        elif result.get('key') == 'NoiseSuppressionDefault':
            if 'value' in result:
                noise_suppressions.add(str(result['value']))
            elif 'full_line' in result:
                # Try quoted format first
                match = re.search(r'"NoiseSuppressionDefault"\s*:\s*"(.*?)"', result['full_line'])
                if match:
                    noise_suppressions.add(match.group(1))
                else:
                    # Try unquoted format: NoiseSuppressionDefault = value
                    match = re.search(r'NoiseSuppressionDefault\s*=\s*([^\s\n]+)', result['full_line'], re.IGNORECASE)
                    if match:
                        noise_suppressions.add(match.group(1))

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Teams Log Analysis Results\n")
        f.write(f"Script Version: 1.0.0\n")
        f.write(f"Source: {file_path}\n")
        f.write(f"=" * 80 + "\n")
        f.write(f"SUMMARY\n")
        f.write(f"licenseName values: {', '.join(sorted(license_names)) if license_names else 'None found'}\n")
        f.write(f"NoiseSuppressionDefault values: {', '.join(sorted(noise_suppressions)) if noise_suppressions else 'None found'}\n")
        f.write(f"=" * 80 + "\n\n")
        f.write(f"Found {len(results)} result(s):\n\n")
        for idx, result in enumerate(results, 1):
            key_name = result.get('key', 'unknown')
            if 'full_line' not in result:
                # JSON result
                f.write(f"{idx},{key_name},{result['file']},{result['path']},{result['value']}\n")
            else:
                # TXT result: extract value and also output the full line
                value = ''
                line = result['full_line']
                if key_name == 'licenseName':
                    match = re.search(r'"licenseName"\s*:\s*"(.*?)"', line)
                    if match:
                        value = match.group(1)
                elif key_name == 'NoiseSuppressionDefault':
                    # Try quoted format first
                    match = re.search(r'"NoiseSuppressionDefault"\s*:\s*"(.*?)"', line)
                    if match:
                        value = match.group(1)
                    else:
                        # Try unquoted format: NoiseSuppressionDefault = value
                        match = re.search(r'NoiseSuppressionDefault\s*=\s*([^\s\n]+)', line, re.IGNORECASE)
                        if match:
                            value = match.group(1)
                if value:
                    f.write(f'{idx},{key_name},{result["file"]},{result["path"]},"{value}","{line}"\n')
                else:
                    f.write(f'{idx},{key_name},{result["file"]},{result["path"]},"","{line}"\n')
    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()
