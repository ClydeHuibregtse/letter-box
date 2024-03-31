# Use the official Ubuntu base image
FROM ubuntu:latest

# Install Node.js and npm
RUN apt-get update && apt-get install -y curl
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

# Set the working directory
WORKDIR /app

# Copy the rest of the app files
COPY . .

# Install dependencies
RUN npm install

# Build the Svelte Kit app
RUN npm run build

# Expose the app port
EXPOSE 3001

# Start the app
CMD [ "npm", "run", "preview" ]