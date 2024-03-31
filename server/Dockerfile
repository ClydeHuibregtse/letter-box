# Use the official Ubuntu 20.04 base image
FROM ubuntu:20.04

# Update the package lists
RUN apt-get update

# Install necessary dependencies
RUN apt-get install -y curl build-essential

# Install Rust using rustup
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Add the Rust binaries to the PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Configure the installation directory
ENV APP_DIR=/opt/letter-boxed
ENV DATA_DIR=${APP_DIR}/data

# Set the working directory
WORKDIR $APP_DIR

# Copy your application files to the container
COPY . $APP_DIR

# Build your application
RUN cargo build --release
RUN ls -R ${APP_DIR}

# Expose the port your application listens on
EXPOSE 3000

# Set the command to run your application
CMD ["cargo", "run", "--release"]