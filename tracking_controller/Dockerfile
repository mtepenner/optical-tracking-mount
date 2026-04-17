FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -o /tracker ./cmd/tracker

FROM alpine:3.19
RUN apk --no-cache add ca-certificates
COPY --from=builder /tracker /usr/local/bin/tracker

ENTRYPOINT ["tracker"]
