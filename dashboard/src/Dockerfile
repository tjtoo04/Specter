FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 5173

# Run vite from the root
CMD ["npm", "run", "dev"]
