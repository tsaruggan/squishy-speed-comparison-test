# Use an official image with Python and build-essential (for C++ compilation)
FROM python:3.10-slim

# Install build tools, Git, and OpenCV dependencies
RUN apt-get update && \
    apt-get install -y clang make git libopencv-dev libopenblas-dev && \
    apt-get clean

# Set up a working directory
WORKDIR /test

# Clone the Python and C++ repositories from GitHub
RUN git clone https://github.com/tsaruggan/squishy.git
RUN git clone https://github.com/tsaruggan/squishy-cpp.git

# Install Python dependencies
RUN pip install matplotlib

# Navigate to the C++ directory and run make to build the program
WORKDIR /test/squishy-cpp
RUN make CXX=clang++ CXXFLAGS="-std=c++11 -I/usr/include/opencv4"

# Set working directory back to main test directory and add the Python script
WORKDIR /test
COPY test.py ./
COPY octopus.png ./

# Default command to run the Python test script
CMD ["python3", "test.py"]
