FROM node:21.7.1-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . ./
RUN npm run ci --legacy-peer-deps

FROM nginx:1.25
COPY --from=build /app/build/ /static/