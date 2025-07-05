from functions import generate_segment_percentages

# Load file and read bytes
with open("04032025.Clean_.xlsx", "rb") as f:
    file_bytes = f.read()

# Call the function
results = generate_segment_percentages(file_bytes)
print(results)
