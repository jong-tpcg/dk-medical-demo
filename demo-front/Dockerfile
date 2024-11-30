# Build the frontend
FROM node:20 as vite-build

# pnpm 설치
RUN npm install -g pnpm

WORKDIR /app
COPY package.json pnpm-lock.yaml ./

RUN pnpm install

COPY . .
ENV ENV=dev

RUN pnpm build
# Step 2: Serve with Nginx
FROM nginx:alpine

# Cloud Run에서 사용하는 포트
ENV PORT 8080
ENV HOST 0.0.0.0
EXPOSE 8080


# 템플릿 설정 파일 복사
COPY nginx.conf /etc/nginx/conf.d/configfile.template

# 빌드된 정적 파일을 Nginx HTML 디렉토리로 복사
COPY --from=vite-build /app/dist /usr/share/nginx/html

# 런타임에 $PORT를 대체한 후 Nginx 실행
CMD sh -c "envsubst '\$PORT' < /etc/nginx/conf.d/configfile.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"