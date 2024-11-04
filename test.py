import subprocess
import timeit
import sys
import matplotlib.pyplot as plt
import glob
import os
import numpy as np

# Paths
python_script = "./squishy/squishy.py"
cpp_executable = "./squishy-cpp/squishy"
sample_directory = "./sample-inputs"
output_directory = "./sample-outputs"
os.makedirs(output_directory, exist_ok=True)  # Ensure output directory exists

# Helper functions
def run_python(input_args):
    subprocess.run([sys.executable, python_script] + input_args, capture_output=True, text=True)

def run_cpp(input_args):
    subprocess.run([cpp_executable] + input_args, capture_output=True, text=True)

def time_test(func, input_args):
    start_time = timeit.default_timer()
    func(input_args)
    end_time = timeit.default_timer()
    return end_time - start_time

# Prepare to gather data
image_files = sorted(glob.glob(f"{sample_directory}/*.png"))
total_times = []
image_file_sizes = []  # Store sizes of the input image files

# Run combined compression and decompression tests
print("Running Speed Test...")
for image_file in image_files:
    compressed_file = f"{output_directory}/{os.path.basename(image_file)[:-4]}_output.bin"
    decompressed_file = f"{output_directory}/{os.path.basename(image_file)[:-4]}_decompressed.png"
    compress_args = ["compress", image_file, compressed_file]
    decompress_args = ["decompress", compressed_file, decompressed_file]

    # Measure total time (compression + decompression) for Python
    python_total_time = time_test(run_python, compress_args) + time_test(run_python, decompress_args)

    # Measure total time (compression + decompression) for C++
    cpp_total_time = time_test(run_cpp, compress_args) + time_test(run_cpp, decompress_args)

    # Get the size of the input image file
    img_size = os.path.getsize(image_file)

    total_times.append((python_total_time, cpp_total_time))
    image_file_sizes.append(img_size)

    print(f"{image_file} | Python Total: {python_total_time:.3f}s, C++ Total: {cpp_total_time:.3f}s, Image Size: {img_size} B")

# Prepare data for plotting
avg_python_times = [times[0] for times in total_times]
avg_cpp_times = [times[1] for times in total_times]

# Plotting total times
plt.figure(figsize=(10, 5))

# Scatter plot for Python and C++ total times
plt.scatter(image_file_sizes, avg_python_times, color='b', label='Python', marker='o')
plt.scatter(image_file_sizes, avg_cpp_times, color='r', label='C++', marker='o')

# Fit linear trend line for Python
z1 = np.polyfit(image_file_sizes, avg_python_times, 1)
p1 = np.poly1d(z1)
plt.plot(image_file_sizes, p1(image_file_sizes), color='b', linestyle='--')

# Fit linear trend line for C++
z2 = np.polyfit(image_file_sizes, avg_cpp_times, 1)
p2 = np.poly1d(z2)
plt.plot(image_file_sizes, p2(image_file_sizes), color='r', linestyle='--')

# Labeling the plot
plt.xlabel('File Size (bytes)')
plt.ylabel('Total Time (seconds)')
plt.title('Squishy Speed Comparison Test')
plt.legend()
plt.tight_layout(pad=3)

# Calculate average total times for Python and C++
avg_python_total_time = np.mean(avg_python_times)
avg_cpp_total_time = np.mean(avg_cpp_times)
speedup_percentage = ((avg_python_total_time - avg_cpp_total_time) / avg_python_total_time) * 100

# Add caption with speedup percentage
plt.figtext(0.5, 0.01, f"C++ implementation is {speedup_percentage:.2f}% faster than Python", 
            ha="center", fontsize=10, color="black")

# Save the plot
plt.savefig('squishy_speed_comparison_test.png')
plt.close()
