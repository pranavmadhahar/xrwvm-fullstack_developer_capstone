FROM node:18.12.1-bullseye-slim

WORKDIR /usr/src/app

# Copy dependency manifests first
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the source code
COPY . .

EXPOSE 3030
CMD ["node", "app.js"]
