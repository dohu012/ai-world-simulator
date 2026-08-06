FROM node:22.17.0-alpine3.22 AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22.17.0-alpine3.22
ENV NODE_ENV=production
WORKDIR /app
COPY --from=build /app ./
USER node
EXPOSE 3000
CMD ["npm", "run", "start"]
