FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 5173

# CRITICAL CHANGE: Add '-- --host' to bind to 0.0.0.0
# This passes the --host flag to the underlying vite command
CMD ["npm", "run", "dev", "--", "--host"]