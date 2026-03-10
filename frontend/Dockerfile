FROM node:20-alpine

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["sh", "-c", "npm install && npm run dev -- --hostname 0.0.0.0"]
